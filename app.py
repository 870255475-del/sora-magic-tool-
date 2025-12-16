import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import gc
import time
import random
from openai import OpenAI

# ==========================================
# 👇 0. 核心配置 (已移除本地启动代码，云端专用) 👇
# ==========================================
st.set_page_config(
    page_title="Miss Pink Elf's Studio v10.0", 
    layout="wide", 
    page_icon="🌸",
    initial_sidebar_state="expanded"
)

# ==========================================
# 👇 1. 核心样式与特效 (CSS/JS) 👇
# ==========================================
def load_elysia_style():
    sakura_css = """
    <style>
    /* 全局优化 */
    .stApp {
        background: linear-gradient(135deg, #FFF0F5 0%, #E6E6FA 60%, #E0FFFF 100%);
        font-family: 'Comic Sans MS', 'Microsoft YaHei', sans-serif;
        color: #4A4A4A;
    }
    
    /* 樱花容器 (防遮挡优化) */
    .sakura-container {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none; z-index: 0; overflow: hidden;
    }
    .sakura {
        position: absolute; background-color: #FFB7C5; 
        border-radius: 100% 0 100% 0; opacity: 0.8;
        animation: fall linear infinite;
    }
    @keyframes fall {
        0% { opacity: 0; top: -10%; transform: translateX(0) rotate(0deg); }
        10% { opacity: 1; }
        100% { opacity: 0; top: 100%; transform: translateX(200px) rotate(720deg); }
    }

    /* 侧边栏进化：玻璃拟态 v2.0 */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.8);
        box-shadow: 2px 0 15px rgba(255, 192, 203, 0.15);
        z-index: 1;
    }

    /* 标题特效 */
    h1, h2, h3 {
        background: linear-gradient(45deg, #FF69B4, #87CEFA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important;
        letter-spacing: 1px;
    }
    
    /* 卡片悬浮特效 */
    .feature-card {
        background: rgba(255, 255, 255, 0.6);
        border-radius: 20px; padding: 25px;
        border: 2px solid #FFF;
        box-shadow: 0 8px 20px rgba(255, 182, 193, 0.15);
        transition: all 0.3s ease;
        text-align: center; height: 100%;
    }
    .feature-card:hover {
        transform: translateY(-8px) scale(1.02);
        background: rgba(255, 255, 255, 0.95);
        border-color: #FF69B4;
        box-shadow: 0 15px 30px rgba(255, 105, 180, 0.3);
    }
    .emoji-icon { font-size: 3.5em; margin-bottom: 15px; display: block; animation: float 3s ease-in-out infinite; }
    @keyframes float { 0% {transform: translateY(0px);} 50% {transform: translateY(-10px);} 100% {transform: translateY(0px);} }

    /* 控件极致美化 */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 12px !important; border: 2px solid #FFE4E1 !important;
        background: rgba(255, 255, 255, 0.85) !important;
        transition: border-color 0.3s;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #FF69B4 !important;
        box-shadow: 0 0 10px rgba(255, 105, 180, 0.2);
    }

    /* 按钮：流光溢彩 */
    div.stButton > button {
        background: linear-gradient(90deg, #FF9A9E 0%, #FECFEF 50%, #FF9A9E 100%);
        background-size: 200% auto;
        color: white !important;
        border-radius: 25px !important; border: none !important;
        box-shadow: 0 4px 15px rgba(255, 105, 180, 0.4) !important;
        transition: all 0.4s ease;
    }
    div.stButton > button:hover {
        background-position: right center;
        transform: scale(1.03);
    }
    </style>
    """
    
    sakura_js = """
    <script>
    function createSakura() {
        const container = document.createElement('div');
        container.className = 'sakura-container';
        document.body.appendChild(container);
        for (let i = 0; i < 40; i++) { 
            const petal = document.createElement('div');
            petal.className = 'sakura';
            const size = Math.random() * 12 + 6 + 'px';
            petal.style.width = size; petal.style.height = size;
            petal.style.left = Math.random() * 100 + 'vw';
            petal.style.animationDuration = Math.random() * 6 + 6 + 's';
            petal.style.animationDelay = Math.random() * 5 + 's';
            container.appendChild(petal);
        }
    }
    createSakura();
    </script>
    """
    st.markdown(sakura_css + sakura_js, unsafe_allow_html=True)

load_elysia_style()

# ==========================================
# 👇 2. 工具函数库 (Utils) 👇
# ==========================================
@st.cache_resource
def get_font(size):
    # 创建一个字体备选列表，按推荐顺序排列
    # DejaVuSans-Bold 在 Linux 服务器上非常常见，且效果很好
    possible_fonts = [
        "DejaVuSans-Bold.ttf",  # Linux 服务器首选
        "arialbd.ttf",          # Windows 上的备选
        "Arial Bold.ttf",       # 另一种 Windows 命名
        "Arial.ttf",            # 如果粗体没有，用常规体也行
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" # 在某些 Linux 上的绝对路径
    ]
    
    # 挨个尝试列表里的字体
    for font_name in possible_fonts:
        try:
            # 只要找到一个能用的，就立刻返回
            return ImageFont.truetype(font_name, size)
        except IOError:
            # 如果找不到，就默默地继续尝试下一个
            continue
            
    # 如果列表里所有字体都失败了，才使用最后的备用方案
    return ImageFont.load_default()

@st.cache_data(show_spinner=False)
def load_preview_image(uploaded_file):
    image = Image.open(uploaded_file)
    if image.mode in ('RGBA', 'P'): image = image.convert('RGB')
    image.thumbnail((400, 400)) 
    return image

# 核心 AI 逻辑
def generate_sora_prompt_with_ai(api_key, base_url, model_name, global_style, cam, phys, ratio, motion, neg_prompt, shots_data):
    if not base_url: base_url = "https://api.openai.com/v1"
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    tech_specs = f"Specs: Ratio {ratio}, Motion {motion}/10, {cam}, {phys}"
    
    system_prompt = f"""
    你是由爱莉希雅强化的 Sora 2 提示词架构师。
    【任务目标】
    将用户的静态分镜表，转化为一段包含 "物理逻辑" 和 "叙事流动" 的 Sora 2 (Turbo) 视频提示词。
    【输出要求】
    1. 必须以技术参数开头: "{tech_specs}"
    2. 必须使用时间轴标记: [0s-2s], [2s-4s]...
    3. 必须融入负面提示词逻辑: "Ensure high quality, avoid {neg_prompt}."
    4. 不要输出你的思考过程，只输出最终的 Prompt。
    """
    
    user_content = f"Global Style: {global_style}\nStoryboard Sequences:\n"
    current_time = 0.0
    for idx, item in enumerate(shots_data):
        end_time = current_time + item['dur']
        user_content += f"- Sequence {idx+1} ({current_time}s-{end_time}s): Camera View={item['shot_code']}, Subject Action={item['desc']}\n"
        current_time = end_time
        
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 魔法中断: {str(e)}"

# ==========================================
# 👇 3. 配置数据与状态管理 👇
# ==========================================
PRESETS_STYLE = {
    "🌸 爱莉希雅 (Anime)": "Dreamy Anime, Makoto Shinkai style, vibrant pastel colors, crystal clear lighting.",
    "🎥 诺兰电影感 (IMAX)": "Shot on IMAX 70mm, Christopher Nolan style, realistic texture, muted tones.",
    "🌃 赛博朋克 (Cyberpunk)": "Neon-noir atmosphere, wet pavement reflections, volumetric fog, futuristic city.",
    "📱 抖音爆款 (Viral)": "Trending on TikTok, high saturation, sharp focus, slow motion, 60fps.",
    "🧊 3D 渲染 (C4D)": "Octane render, clay material, soft studio lighting, 3D character design."
}
PRESETS_CAMERA = {
    "Auto (自动)": "Cinematic camera movement matching action",
    "Truck (横移)": "Smooth trucking shot following subject",
    "Dolly In (推镜头)": "Slow dolly in to emphasize emotion",
    "Rack Focus (变焦)": "Rack focus from foreground to background",
    "FPV (穿越)": "Fast FPV drone flight"
}
TAGS_PHYSICS = ["Volumetric Lighting", "Ray-traced Reflections", "Subsurface Scattering", "Fluid Simulation", "Motion Blur"]
RATIOS = {"16:9 (电影)": (1920, 1080), "9:16 (抖音)": (1080, 1920), "2.35:1 (宽屏)": (1920, 816), "1:1 (方图)": (1080, 1080)}
DEFAULT_NEG = "morphing, distortion, bad anatomy, blurry, watermark, text, low quality, glitch"

if 'history' not in st.session_state: st.session_state.history = []
if 'last_result' not in st.session_state: st.session_state.last_result = None

# ==========================================
# 👇 4. 侧边栏 (UI 交互中心) 👇
# ==========================================
with st.sidebar:
    if os.path.exists("elysia_cover.jpg"):
        st.image("elysia_cover.jpg", use_container_width=True)
        st.caption("✨ “Hi~ 无论迭代多少次，我都与你同在！”")

    st.markdown("### 🏹 魔法配置")
    
    with st.expander("🤖 第一步：连接 AI 大脑", expanded=True):
        api_provider = st.selectbox("API类型", ["自定义", "火山引擎 (豆包)", "DeepSeek", "OpenAI"])
        
        # 默认值防止报错
        base, model = "", ""
        
        if api_provider == "火山引擎 (豆包)":
            st.markdown("👉 [**点我注册豆包**](https://www.volcengine.com/product/doubao)")
            base = "https://ark.cn-beijing.volces.com/api/v3"
        elif api_provider == "DeepSeek":
            st.markdown("👉 [**点我注册 DeepSeek**](https://platform.deepseek.com/)")
            base = "https://api.deepseek.com"; model = "deepseek-chat"
        elif api_provider == "OpenAI":
            st.markdown("👉 [**OpenAI 官网**](https://platform.openai.com/)")
            base = "https://api.openai.com/v1"; model = "gpt-4o"

        api_key = st.text_input("API Key", type="password")
        
        if api_provider != "自定义":
            base_url = st.text_input("Base URL", value=base)
            model_name = st.text_input("Model", value=model, placeholder="豆包请填 Endpoint ID")
        else:
            base_url = st.text_input("Base URL")
            model_name = st.text_input("Model")

    st.markdown("---")
    st.markdown("#### 🧪 Sora 2 炼金台")
    
    col_ui1, col_ui2 = st.columns(2)
    with col_ui1:
        selected_style = st.selectbox("🔮 风格", list(PRESETS_STYLE.keys()))
    with col_ui2:
        selected_cam = st.selectbox("📷 运镜", list(PRESETS_CAMERA.keys()))
    
    style_content = PRESETS_STYLE[selected_style]
    cam_content = PRESETS_CAMERA[selected_cam]
    
    selected_phys = st.multiselect("🌊 物理与光影", TAGS_PHYSICS, default=["Volumetric Lighting"])
    phys_content = ", ".join(selected_phys)
    
    selected_ratio_name = st.selectbox("画幅比例", list(RATIOS.keys()))
    target_size = RATIOS[selected_ratio_name]
    
    motion_strength = st.slider("⚡ 动态幅度", 1, 10, 5)
    neg_prompt = st.text_area("⛔ 负面提示词", value=DEFAULT_NEG, height=70)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1: border_width = st.slider("间距", 0, 30, 15)
    with c2: output_quality = st.select_slider("画质", ["2K", "4K"], value="2K")
    scale_factor = 1.5 if output_quality == "4K" else 1.0

    st.markdown("---")
    with st.expander("☕ 打赏作者 (小费)", expanded=False):
        if os.path.exists("pay.jpg"):
            st.image("pay.jpg", caption="投喂灵感~", use_container_width=True)
        else:
            st.info("（等待投喂中...）")

# ==========================================
# 👇 5. 主工作台 (Main Stage) 👇
# ==========================================

st.title("Miss Pink Elf's Studio v10.0")
st.markdown("**“要把这一瞬间，变成永恒的故事吗？交给我吧~”**")

uploaded_files = st.file_uploader("📂 拖入图片开始创作 (支持批量)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

# 👉 英雄区：无文件时显示引导
if not uploaded_files:
    st.markdown("<br>", unsafe_allow_html=True) 
    col_intro1, col_intro2, col_intro3 = st.columns(3)
    
    with col_intro1:
        st.markdown("""
        <div class="feature-card">
            <span class="emoji-icon">🧠</span>
            <h3>Sora 2 内核</h3>
            <p>基于官方文档优化的<br>物理引擎提示词逻辑</p>
        </div>
        """, unsafe_allow_html=True)
    with col_intro2:
        st.markdown("""
        <div class="feature-card">
            <span class="emoji-icon">🎬</span>
            <h3>AI 导演 v10</h3>
            <p>思维链 (CoT) 加持<br>更懂镜头语言与叙事</p>
        </div>
        """, unsafe_allow_html=True)
    with col_intro3:
        st.markdown("""
        <div class="feature-card">
            <span class="emoji-icon">🌸</span>
            <h3>唯美体验</h3>
            <p>极致丝滑的预览技术<br>樱花雨下的创作</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("💡 **V10.0 更新日志:** 修复了云端字体 Bug，移除了本地启动代码，优化了API连接逻辑，新增历史记录和 TXT 下载。")

else:
    # 排序文件
    uploaded_files.sort(key=lambda x: x.name)
    
    with st.container():
        with st.form("storyboard_form"):
            st.write("#### 📝 故事编织台")
            shots_data = []
            cols = st.columns(3)
            shot_options = ["ECU (极特写)", "CU (特写)", "MS (中景)", "LS (全景)", "OTS (过肩)", "FPV (第一人称)"]
            
            for i, f in enumerate(uploaded_files):
                if i >= 9: break
                with cols[i % 3]:
                    thumb = load_preview_image(f)
                    st.image(thumb, use_container_width=True)
                    
                    c1, c2 = st.columns([1.5, 1])
                    with c1: s_type = st.selectbox("视角", shot_options, key=f"s_{i}", label_visibility="collapsed")
                    with c2: dur = st.number_input("秒", value=2.0, step=0.5, key=f"d_{i}", label_visibility="collapsed")
                    desc = st.text_input("描述", placeholder="例如：女孩回头...", key=f"t_{i}", label_visibility="collapsed")
                    shots_data.append({"file": f, "shot_code": s_type.split(" ")[0], "dur": dur, "desc": desc if desc else "Cinematic shot"})
            
            st.markdown("---")
            submit_btn = st.form_submit_button("✨ 施展魔法 (生成专业分镜 + 咒语) ✨", type="primary", use_container_width=True)

    # 👉 生成逻辑
    if submit_btn:
        with st.status("💎 魔法咏唱中...", expanded=True) as status:
            st.write("🖼️ 正在构建黑底白字专业分镜...")
            # 图片处理
            base_w, base_h = target_size
            final_w, final_h = int(base_w * scale_factor), int(base_h * scale_factor)
            count = len(shots_data)
            cols_count = 3
            rows_count = -(-count // cols_count)
            
            # 【专业模式】黑条高度
            bar_height = int(final_h * 0.12)
            cell_h = final_h + bar_height
            
            total_w = (final_w * cols_count) + (border_width * (cols_count + 1))
            total_h = (cell_h * rows_count) + (border_width * (rows_count + 1))
            
            # 【专业模式】纯黑背景
            canvas = Image.new('RGB', (total_w, total_h), "#000000")
            draw = ImageDraw.Draw(canvas)
            font = get_font(int(bar_height * 0.5))
            
            for idx, item in enumerate(shots_data):
                src = Image.open(item["file"])
                src = ImageOps.fit(src, (final_w, final_h), method=Image.Resampling.LANCZOS)
                
                # 【专业模式】单格：黑底 + 左对齐白字
                cell = Image.new('RGB', (final_w, cell_h), "#000000")
                cell.paste(src, (0, bar_height))
                
                info_text = f"KF{idx+1} [{item['shot_code']} | {item['dur']}s]"
                cdraw = ImageDraw.Draw(cell)
                
                text_padding_left = int(20 * scale_factor)
                text_bbox = cdraw.textbbox((0, 0), info_text, font=font)
                text_h = text_bbox[3] - text_bbox[1]
                text_y = (bar_height - text_h) / 2
                
                cdraw.text((text_padding_left, text_y), info_text, fill="#FFFFFF", font=font)
                
                r, c = idx // cols_count, idx % cols_count
                x = border_width + (c * (final_w + border_width))
                y = border_width + (r * (cell_h + border_width))
                canvas.paste(cell, (x, y))
            
            prompt_res = ""
            if api_key:
                st.write("🧠 AI 正在思考光影与运镜 (CoT)...")
                prompt_res = generate_sora_prompt_with_ai(
                    api_key, base_url, model_name, 
                    style_content, cam_content, phys_content, 
                    selected_ratio_name, motion_strength, neg_prompt, shots_data
                )
            else:
                st.warning("⚠️ 未连接 API，跳过提示词生成")

            status.update(label="✨ 魔法完成！", state="complete", expanded=False)
            
            # 保存结果到 Session
            st.session_state.last_result = {"image": canvas, "prompt": prompt_res}
            # (迭代功能) 加入历史列表
            st.session_state.history.append({"image": canvas, "prompt": prompt_res, "time": time.strftime("%H:%M")})
            gc.collect()

    # 👉 结果显示区 (从 Session 读取)
    if st.session_state.last_result:
        res = st.session_state.last_result
        st.balloons()
        
        tab1, tab2, tab3 = st.tabs(["🖼️ 专业分镜图", "📜 Sora 2 咒语", "🕰️ 历史记录"])
        
        with tab1:
            st.caption("✅ 已严格遵循参考图格式：黑底、白字、左对齐。Sora 2 可完美识别。")
            st.image(res["image"], use_container_width=True)
            buf = io.BytesIO()
            res["image"].save(buf, format="JPEG", quality=95, subsampling=0)
            st.download_button("📥 下载专业分镜图", buf.getvalue(), "sora_storyboard_pro.jpg", "image/jpeg")
            
        with tab2:
            if res["prompt"]:
                st.code(res["prompt"], language="text")
                st.download_button("📄 下载提示词 (.txt)", res["prompt"], "prompt.txt", "text/plain")
            else:
                st.info("本次仅生成了图片，填写 API Key 可生成提示词。")
        
        with tab3:
            st.caption("本次会话的历史生成记录 (刷新后消失)")
            for i, h in enumerate(reversed(st.session_state.history[:-1])): 
                with st.expander(f"🕒 记录 {h.get('time', i)}"):
                    st.image(h['image'], use_container_width=True)
                    if h['prompt']: st.code(h['prompt'])
