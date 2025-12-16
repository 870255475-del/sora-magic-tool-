import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import gc
import time
from openai import OpenAI

# ==========================================
# 👇 0. 核心配置 👇
# ==========================================
st.set_page_config(
    page_title="Miss Pink Elf's Studio v18.0 (Ultimate)", 
    layout="wide", 
    page_icon="🌸",
    initial_sidebar_state="expanded"
)

# ==========================================
# 👇 1. 核心样式与特效 👇
# ==========================================
def load_elysia_style():
    # 完整的 CSS 样式
    st.markdown("""
    <style>
    /* 全局优化 */
    .stApp {
        background: linear-gradient(135deg, #FFF0F5 0%, #E6E6FA 60%, #E0FFFF 100%);
        font-family: 'Comic Sans MS', 'Microsoft YaHei', sans-serif;
        color: #4A4A4A;
    }
    
    /* 樱花容器 */
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

    /* 侧边栏 */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.8);
        box-shadow: 2px 0 15px rgba(255, 192, 203, 0.15);
        z-index: 1;
    }

    /* 标题特效 */
    h1, h2, h3, h4 {
        background: linear-gradient(45deg, #FF69B4, #87CEFA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
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
    }
    .emoji-icon { font-size: 3.5em; margin-bottom: 15px; display: block; animation: float 3s ease-in-out infinite; }
    @keyframes float { 0% {transform: translateY(0px);} 50% {transform: translateY(-10px);} 100% {transform: translateY(0px);} }

    /* 输入框 */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 12px !important; border: 2px solid #FFE4E1 !important;
        background: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* 按钮 */
    div.stButton > button {
        background: linear-gradient(90deg, #FF9A9E 0%, #FECFEF 100%);
        color: white !important;
        border-radius: 20px !important; border: none !important;
        box-shadow: 0 4px 12px rgba(255, 105, 180, 0.3) !important;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 完整的 JS 脚本
    st.markdown("""
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
    """, unsafe_allow_html=True)

load_elysia_style()

# ==========================================
# 👇 2. 工具函数库 👇
# ==========================================
@st.cache_resource
def get_font(size):
    possible_fonts = ["DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    for font_name in possible_fonts:
        try:
            return ImageFont.truetype(font_name, size)
        except IOError:
            continue
    return ImageFont.load_default()

@st.cache_data(show_spinner=False)
def load_preview_image(_bytes):
    image = Image.open(io.BytesIO(_bytes))
    if image.mode in ('RGBA', 'P'): image = image.convert('RGB')
    image.thumbnail((400, 400))
    return image

def generate_sora_prompt_with_ai(api_key, base_url, model_name, global_style, cam, phys, ratio, motion, neg_prompt, shots_data):
    if not api_key: return "API Key not provided."
    if not base_url: base_url = "https://api.openai.com/v1"
    client = OpenAI(api_key=api_key, base_url=base_url)
    tech_specs = f"Specs: Ratio {ratio}, Motion {motion}/10, {cam}, {phys}"
    system_prompt = f"""You are an expert Sora 2 prompt engineer. Your task is to convert a storyboard into a narrative, physically-aware prompt.
    - Start with technical specs: "{tech_specs}"
    - Use timeline markers: [0s-2s].
    - Incorporate negative prompts: "Ensure high quality, avoid {neg_prompt}."
    - Output only the final prompt.
    """
    user_content = f"Global Style: {global_style}\nStoryboard:\n"
    current_time = 0.0
    for idx, item in enumerate(shots_data):
        end_time = current_time + item['dur']
        user_content += f"- Shot {idx+1} ({current_time}s-{end_time}s): View={item['shot_code']}, Action={item['desc']}\n"
        current_time = end_time
    try:
        response = client.chat.completions.create(model=model_name, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}], temperature=0.7)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# ==========================================
# 👇 3. 状态管理 & 数据 👇
# ==========================================
PRESETS_STYLE = {
    "🌸 爱莉希雅 (Anime)": "Dreamy Anime, Makoto Shinkai style, vibrant pastel colors, crystal clear lighting.",
    "🎥 诺兰电影感 (IMAX)": "Shot on IMAX 70mm, Christopher Nolan style, realistic texture, muted tones.",
    "🌃 赛博朋克 (Cyberpunk)": "Neon-noir atmosphere, wet pavement reflections, volumetric fog, futuristic city.",
    "📱 抖音爆款 (Viral)": "Trending on TikTok, high saturation, sharp focus, slow motion, 60fps.",
    "🧊 3D 渲染 (C4D)": "Octane render, clay material, soft studio lighting, 3D character design."
}
PRESETS_CAMERA = {
    "Auto (自动)": "Cinematic camera movement matching action", "Truck (横移)": "Smooth trucking shot following subject",
    "Dolly In (推镜头)": "Slow dolly in to emphasize emotion", "Rack Focus (变焦)": "Rack focus from foreground to background",
    "FPV (穿越)": "Fast FPV drone flight"
}
TAGS_PHYSICS = ["Volumetric Lighting", "Ray-traced Reflections", "Subsurface Scattering", "Fluid Simulation", "Motion Blur"]
RATIOS = {"16:9 (电影)": (1920, 1080), "9:16 (抖音)": (1080, 1920), "2.35:1 (宽屏)": (1920, 816), "1:1 (方图)": (1080, 1080)}
DEFAULT_NEG = "morphing, distortion, bad anatomy, blurry, watermark, text, low quality, glitch, extra limbs"

if "files" not in st.session_state: st.session_state.files = []
if 'last_result' not in st.session_state: st.session_state.last_result = None
if 'history' not in st.session_state: st.session_state.history = []

# ==========================================
# 👇 4. 侧边栏 UI 👇
# ==========================================
with st.sidebar:
    if os.path.exists("elysia_cover.jpg"):
        st.image("elysia_cover.jpg", use_container_width=True)
        st.caption("✨ “Hi~ 无论何时，我都会回应你的期待哦！”")
    else:
        st.warning("看板娘图片 'elysia_cover.jpg' 不见了哦！")

    st.markdown("### 🏹 魔法配置")
    with st.expander("🤖 第一步：连接 AI 大脑", expanded=True):
        api_provider = st.selectbox("API类型", ["自定义", "火山引擎 (豆包)", "DeepSeek", "OpenAI"])
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
    selected_style = st.selectbox("🔮 滤镜风格", list(PRESETS_STYLE.keys()))
    style_content = PRESETS_STYLE[selected_style]
    selected_cam = st.selectbox("📷 运镜方式", list(PRESETS_CAMERA.keys()))
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
# 👇 5. 主工作台 👇
# ==========================================
st.title("Miss Pink Elf's Studio v18.0 (Ultimate)")

# 上传逻辑
newly_uploaded_files = st.file_uploader("📂 **拖入图片**", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True, key="uploader")
if newly_uploaded_files:
    existing_filenames = {f['name'] for f in st.session_state.files}
    has_new_files = False
    for file in newly_uploaded_files:
        if file.name not in existing_filenames:
            st.session_state.files.append({"name": file.name, "bytes": file.getvalue()})
            has_new_files = True
    if has_new_files:
        st.rerun()

# 英雄区 / 工作区 切换
if not st.session_state.files:
    st.info("👈 请上传图片")
else:
    st.caption("👇 使用图片下方的 ⬆️⬇️ 按钮调整顺序，或在表单中勾选后批量删除")

    # 排序按钮 (在表单外)
    cols_sort = st.columns(4)
    for i, file_data in enumerate(st.session_state.files):
        with cols_sort[i % 4]:
            with st.container():
                thumb = load_preview_image(file_data["bytes"])
                st.image(thumb, use_container_width=True)
                def move_item(index, direction):
                    if direction == "up" and index > 0:
                        st.session_state.files.insert(index - 1, st.session_state.files.pop(index))
                    elif direction == "down" and index < len(st.session_state.files) - 1:
                        st.session_state.files.insert(index + 1, st.session_state.files.pop(index))
                c1, c2, _ = st.columns([1, 1, 4])
                with c1: st.button("⬆️", key=f"up_{i}", on_click=move_item, args=(i, "up"), use_container_width=True)
                with c2: st.button("⬇️", key=f"down_{i}", on_click=move_item, args=(i, "down"), use_container_width=True)

    st.markdown("---")
    
    # 表单 (只负责编辑和删除)
    with st.form("storyboard_form"):
        st.write("#### 📝 故事编织台")
        shots_data = []
        form_cols = st.columns(4)
        delete_flags = {}
        for i, file_data in enumerate(st.session_state.files):
            with form_cols[i % 4]:
                st.caption(f"镜头 {i+1}")
                delete_flags[i] = st.checkbox("删除", key=f"del_{i}")
                s_type = st.selectbox("视角", ["CU", "MS", "LS"], key=f"s_{i}", label_visibility="collapsed")
                dur = st.number_input("秒", value=2.0, step=0.5, key=f"d_{i}", label_visibility="collapsed")
                desc = st.text_input("描述", placeholder="动作...", key=f"t_{i}", label_visibility="collapsed")
                shots_data.append({"bytes": file_data["bytes"], "shot_code": s_type, "dur": dur, "desc": desc})
        st.markdown("---")
        col_btn1, col_btn2 = st.columns([2, 1])
        with col_btn1: submit_btn = st.form_submit_button("✨ 施展魔法 ✨", type="primary", use_container_width=True)
        with col_btn2: delete_submit_btn = st.form_submit_button("🗑️ 执行删除", use_container_width=True)

    # 按钮逻辑
    if delete_submit_btn:
        indices_to_delete = sorted([i for i, checked in delete_flags.items() if checked], reverse=True)
        if indices_to_delete:
            for i in indices_to_delete: del st.session_state.files[i]
            st.success(f"已删除 {len(indices_to_delete)} 张图片！")
            time.sleep(1)
            st.rerun()

    if submit_btn:
        with st.status("💎 魔法咏唱中...", expanded=True) as status:
            st.write("🖼️ 正在构建黑底白字专业分镜...")
            base_w, base_h = target_size
            final_w, final_h = int(base_w * scale_factor), int(base_h * scale_factor)
            count = len(shots_data)
            cols_count = 3
            rows_count = -(-count // cols_count)
            bar_height = int(final_h * 0.12)
            cell_h = final_h + bar_height
            total_w = (final_w * cols_count) + (border_width * (cols_count + 1))
            total_h = (cell_h * rows_count) + (border_width * (rows_count + 1))
            canvas = Image.new('RGB', (total_w, total_h), "#000000")
            draw = ImageDraw.Draw(canvas)
            font = get_font(int(bar_height * 0.5))
            for idx, item in enumerate(shots_data):
                src = Image.open(io.BytesIO(item["bytes"]))
                src = ImageOps.fit(src, (final_w, final_h), method=Image.Resampling.LANCZOS)
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
                st.write("🧠 AI 正在思考光影与运镜...")
                prompt_res = generate_sora_prompt_with_ai(
                    api_key, base_url, model_name, 
                    style_content, cam_content, phys_content, 
                    selected_ratio_name, motion_strength, neg_prompt, shots_data
                )
            
            status.update(label="✨ 魔法完成！", state="complete")
            st.session_state.last_result = {"image": canvas, "prompt": prompt_res}
            st.session_state.history.append({"image": canvas, "prompt": prompt_res, "time": time.strftime("%H:%M")})
            gc.collect()

    if st.session_state.last_result:
        res = st.session_state.last_result
        st.balloons()
        tab1, tab2, tab3 = st.tabs(["🖼️ 专业分镜图", "📜 Sora 2 咒语", "🕰️ 历史记录"])
        with tab1:
            st.image(res["image"], use_container_width=True)
            buf = io.BytesIO()
            res["image"].save(buf, format="JPEG", quality=95)
            st.download_button("📥 下载专业分镜图", buf.getvalue(), "sora_pro.jpg", "image/jpeg")
        with tab2:
            if res["prompt"]:
                st.code(res["prompt"], language="text")
                st.download_button("📄 下载提示词 (.txt)", res["prompt"], "prompt.txt", "text/plain")
        with tab3:
            st.caption("本次会话的历史记录")
            for i, h in enumerate(reversed(st.session_state.history[:-1])):
                with st.expander(f"🕒 记录 {h.get('time', i)}"):
                    st.image(h['image'], use_container_width=True)
                    if h['prompt']: st.code(h['prompt'])
