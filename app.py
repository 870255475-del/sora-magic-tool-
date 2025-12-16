import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import gc
import time
from openai import OpenAI
import math

# ==========================================
# 👇 0. 核心配置 👇
# ==========================================
st.set_page_config(
    page_title="Miss Pink Elf's Studio v33.3 (Final)",
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
    /* 全局 */
    .stApp { background: linear-gradient(135deg, #FFF0F5 0%, #E6E6FA 100%); font-family: 'Comic Sans MS', sans-serif; }
    h1, h2, h3, h4 { background: -webkit-linear-gradient(45deg, #FF6B6B, #FFA07A); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important; }

    /* 侧边栏 */
    section[data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.75); backdrop-filter: blur(20px); }

    /* 卡片 */
    .card {
        background: rgba(255,255,255,0.7);
        border-radius: 18px;
        padding: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.05);
        border: 2px solid transparent;
        transition: all 0.3s ease;
        margin-bottom: 20px; /* 卡片间距 */
    }
    .card:hover { border-color: #FFB6C1; }

    /* 输入控件 */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 12px !important; border: 2px solid #FFE4E1 !important;
        background: rgba(255, 255, 255, 0.85) !important;
    }

    /* 提交按钮 */
    div.stButton > button {
        background: linear-gradient(90deg, #FF6B6B 0%, #FFA07A 100%);
        color: white !important;
        border-radius: 20px !important; border: none !important;
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4) !important;
    }
    .feature-card {
        background: rgba(255, 255, 255, 0.6);
        border-radius: 20px; padding: 25px;
        border: 2px solid #FFF;
        box-shadow: 0 8px 20px rgba(255, 182, 193, 0.15);
        text-align: center; height: 100%;
    }
    .emoji-icon { font-size: 3.5em; margin-bottom: 15px; display: block; }
    </style>
    """, unsafe_allow_html=True)

load_elysia_style()

# ==========================================
# 👇 2. 工具函数库 👇
# ==========================================
@st.cache_resource
def get_font(size):
    """尝试加载系统中可用的粗体字体，失败则使用默认字体"""
    possible_fonts = ["DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial.ttf", "msyhbd.ttc"]
    for f in possible_fonts:
        try: return ImageFont.truetype(f, size)
        except IOError: continue
    return ImageFont.load_default()

@st.cache_data(show_spinner=False)
def load_preview_image(file_name, _bytes):
    """加载并缓存上传图片的缩略图"""
    image = Image.open(io.BytesIO(_bytes))
    image.thumbnail((400, 400))
    return image

def generate_sora_prompt_with_ai(api_key, base_url, model_name, global_style, cam, phys, ratio, motion, neg_prompt, shots_data):
    """调用AI模型生成Sora提示词"""
    if not api_key: return "错误: 未提供 API Key。"
    if not base_url: base_url = "https://api.openai.com/v1"

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
    except Exception as e:
        return f"错误: 初始化OpenAI客户端失败 - {str(e)}"

    tech_specs = f"Specs: Ratio {ratio}, Motion {motion}/10, {cam}, {', '.join(phys)}"
    system_prompt = (
        "You are an expert Sora 2 prompt engineer. Your task is to transform a simple storyboard into a rich, vivid, and coherent video prompt. "
        "Combine the global style, technical specifications, and shot-by-shot descriptions into a single, compelling paragraph. "
        "Describe the scene, characters, and actions in a continuous narrative, ensuring smooth transitions between shots. "
        "Focus on creating a cinematic and emotionally resonant experience. Don't mention the shot timings or shot numbers explicitly in the final prompt. "
        f"Finally, append the negative prompt: --neg {neg_prompt}"
    )

    user_content = f"Global Style: {global_style}\nTechnical Specs: {tech_specs}\nStoryboard:\n"
    current_time = 0.0
    for idx, item in enumerate(shots_data):
        end_time = current_time + item['dur']
        user_content += f"- Shot {idx+1} ({current_time:.1f}s-{end_time:.1f}s): View={item['shot_code']}, Action={item['desc']}\n"
        current_time = end_time

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.75
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"调用API时出错: {str(e)}")
        return f"错误: 调用AI模型失败。请检查API Key、Base URL和网络连接。 {str(e)}"

# ==========================================
# 👇 2.1. 分镜图生成函数 👇
# ==========================================
def create_storyboard(files_data, shots_info, border, ratio_wh):
    """根据上传的图片和信息，生成一张完整的分镜图"""
    if not files_data:
        return None

    # 计算布局
    num_images = len(files_data)
    cols = 3
    rows = math.ceil(num_images / cols)

    # 定义每个单元格的尺寸 (基于16:9)
    base_w, base_h = (480, 270)

    canvas_w = cols * base_w + (cols + 1) * border
    canvas_h = rows * base_h + (rows + 1) * border

    canvas = Image.new('RGB', (canvas_w, canvas_h), (255, 250, 250))
    draw = ImageDraw.Draw(canvas)

    title_font = get_font(24)
    text_font = get_font(16)

    for i, file_data in enumerate(files_data):
        row = i // cols
        col = i % cols

        # 计算每个单元格的起始坐标
        x_start = col * base_w + (col + 1) * border
        y_start = row * base_h + (row + 1) * border

        # 加载并处理图片
        img = Image.open(io.BytesIO(file_data['bytes']))
        # 使用 ImageOps.fit 来裁剪和缩放图片以填充单元格，保持画面内容
        img_thumb = ImageOps.fit(img, (base_w, base_h), Image.Resampling.LANCZOS)
        canvas.paste(img_thumb, (x_start, y_start))

        # 添加半透明黑色背景以增强文本可读性
        shot_data = shots_info[file_data['name']]
        info_text = f"镜头 {i+1} ({shot_data['duration']}s) - {shot_data['shot_type']}\n{shot_data['desc']}"

        # 绘制文本
        text_pos_x = x_start + 10
        text_pos_y = y_start + 10
        draw.text((text_pos_x, text_pos_y), info_text, font=text_font, fill=(255,255,255), stroke_width=2, stroke_fill=(0,0,0))

    return canvas

# ==========================================
# 👇 3. 状态管理 & 数据 👇
# ==========================================
if "files" not in st.session_state: st.session_state.files = []
if "shots_data" not in st.session_state: st.session_state.shots_data = {}
if 'last_result' not in st.session_state: st.session_state.last_result = None

SHOT_OPTIONS = ["CU (特写)", "MS (中景)", "LS (全景)", "ECU (极特写)", "OTS (过肩)", "FPV (第一人称)"]
PRESETS_STYLE = {"🌸 爱莉希雅 (Anime)": "Dreamy Anime Style, pastel colors, sparkling effects, soft focus, beautiful and ethereal atmosphere, inspired by Makoto Shinkai.", "🎥 电影质感 (Cinematic)": "Shot on 35mm film, cinematic lighting, high contrast, anamorphic lens flare, professional color grading, realistic and immersive."}
PRESETS_CAMERA = {"Auto (自动)": "Cinematic camera movement", "Truck (横移)": "Smooth trucking shot", "Dolly (推拉)": "Gentle dolly in/out shot", "Crane (摇臂)": "Sweeping crane shot"}
TAGS_PHYSICS = ["Volumetric Lighting", "Ray-traced Reflections", "Fluid Simulation", "Depth of Field (DoF)", "Motion Blur"]
RATIOS = {"16:9 (电影)": "16:9", "9:16 (抖音)": "9:16"}
DEFAULT_NEG = "morphing, distortion, bad anatomy, blurry, watermark, text, low quality"
MAX_FILES = 6

# ==========================================
# 👇 4. 侧边栏 UI 👇
# ==========================================
def render_sidebar():
    with st.sidebar:
        if os.path.exists("elysia_cover.jpg"):
            st.image("elysia_cover.jpg", use_container_width=True)
        st.markdown("### 🏹 魔法配置")
        with st.expander("🤖 连接 AI 大脑", expanded=True):
            api_provider = st.selectbox("API类型", ["自定义", "火山引擎 (豆包)", "DeepSeek", "OpenAI"])
            base, model = "", ""
            if api_provider == "火山引擎 (豆包)":
                st.markdown("👉 [**点我注册豆包**](https://www.volcengine.com/product/doubao)")
                base = "https://ark.cn-beijing.volces.com/api/v3"; model = "ep-20240722112448-l2a2o" # 请替换为你的模型
            elif api_provider == "DeepSeek":
                st.markdown("👉 [**点我注册 DeepSeek**](https://platform.deepseek.com/)")
                base = "https://api.deepseek.com"; model = "deepseek-chat"
            st.session_state.api_key = st.text_input("API Key", type="password", placeholder="请输入你的 API Key")
            st.session_state.base_url = st.text_input("Base URL", value=base)
            st.session_state.model_name = st.text_input("Model", value=model)

        st.markdown("---")
        st.markdown("#### 🧪 Sora 2 炼金台")
        st.session_state.selected_style_key = st.selectbox("🔮 滤镜风格", list(PRESETS_STYLE.keys()))
        st.session_state.cam_content_key = st.selectbox("📷 运镜方式", list(PRESETS_CAMERA.keys()))
        st.session_state.phys_content = st.multiselect("🌊 物理与光影", TAGS_PHYSICS, default=["Volumetric Lighting"])
        st.session_state.selected_ratio_name = st.selectbox("画幅比例", list(RATIOS.keys()))
        st.session_state.motion_strength = st.slider("⚡ 动态幅度", 1, 10, 5)
        st.session_state.neg_prompt = st.text_area("⛔ 负面提示词", value=DEFAULT_NEG, height=70)
        st.markdown("---")
        st.session_state.border_width = st.slider("🖼️ 间距", 0, 50, 20)
        st.markdown("---")
        with st.expander("☕ 打赏作者", expanded=False):
            if os.path.exists("pay.jpg"):
                st.image("pay.jpg")

# ==========================================
# 👇 5. 主工作台 👇
# ==========================================
def render_hero_section():
    st.info(f"👈 请在左侧上传图片开始创作 (最多 {MAX_FILES} 张)")

def main():
    render_sidebar()
    st.title("Miss Pink Elf's Studio v33.3")

    newly_uploaded_files = st.file_uploader(f"📂 **拖入图片 (最多 {MAX_FILES} 张)**", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True, key="uploader")
    if newly_uploaded_files:
        if len(st.session_state.files) + len(newly_uploaded_files) > MAX_FILES:
            st.warning(f"总数超出限制！最多只能上传 {MAX_FILES} 张图片。")
        else:
            existing_names = {f['name'] for f in st.session_state.files}
            files_to_add = [f for f in newly_uploaded_files if f.name not in existing_names]
            for file in files_to_add:
                st.session_state.files.append({"name": file.name, "bytes": file.getvalue()})
                st.session_state.shots_data[file.name] = {"shot_type": "MS (中景)", "duration": 2.0, "desc": ""}
            if files_to_add:
                st.rerun()

    if not st.session_state.files:
        render_hero_section()
    else:
        st.caption("👇 在每个卡片中编辑信息，使用 ⬆️⬇️ 调整顺序，或点击 ❌ 删除")
        st.write("---")

        cols = st.columns(3)

        def move_item(index, direction):
            if direction == "up" and index > 0: st.session_state.files.insert(index - 1, st.session_state.files.pop(index))
            elif direction == "down" and index < len(st.session_state.files) - 1: st.session_state.files.insert(index + 1, st.session_state.files.pop(index))
            st.rerun()

        def delete_item(index):
            file_name = st.session_state.files[index]['name']
            del st.session_state.shots_data[file_name]
            st.session_state.files.pop(index)
            st.rerun()

        for i, file_data in enumerate(st.session_state.files):
            with cols[i % 3]:
                with st.container():
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.image(load_preview_image(file_data["name"], file_data["bytes"]), use_container_width=True)

                    file_name = file_data['name']
                    shot_info = st.session_state.shots_data.get(file_name, {})

                    st.caption(f"镜头 {i+1}: {file_name[:20]}")

                    s_type = st.selectbox("视角", SHOT_OPTIONS, index=SHOT_OPTIONS.index(shot_info.get('shot_type', "MS (中景)")), key=f"s_{i}")
                    dur = st.number_input("秒", value=shot_info.get('duration', 2.0), min_value=0.5, step=0.5, key=f"d_{i}")
                    desc = st.text_input("描述", value=shot_info.get('desc', ''), placeholder="这个镜头里发生了什么...", key=f"t_{i}")

                    st.session_state.shots_data[file_name] = {"shot_type": s_type, "duration": dur, "desc": desc}

                    c1, c2, c3 = st.columns([1,1,1])
                    with c1: st.button("⬆️", key=f"up_{i}", on_click=move_item, args=(i, "up"), use_container_width=True, disabled=(i==0))
                    with c2: st.button("⬇️", key=f"down_{i}", on_click=move_item, args=(i, "down"), use_container_width=True, disabled=(i==len(st.session_state.files)-1))
                    with c3: st.button("❌", key=f"del_{i}", on_click=delete_item, args=(i,), use_container_width=True, type="primary")

                    st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")
        if st.button("✨ 施展魔法 (生成分镜 + 咒语) ✨", type="primary", use_container_width=True):
            final_shots_data = []
            for file_data in st.session_state.files:
                shot_info = st.session_state.shots_data[file_data['name']]
                # 【修改】注释掉描述检查，允许为空
                # if not shot_info['desc'].strip():
                #     st.error(f"错误：镜头 {file_data['name']} 的描述不能为空！")
                #     return # 终止执行

                final_shots_data.append({
                    "bytes": file_data["bytes"],
                    "shot_code": shot_info['shot_type'].split(" ")[0],
                    "dur": shot_info['duration'],
                    "desc": shot_info['desc']
                })

            with st.status("💎 魔法咏唱中...", expanded=True) as status:
                status.write("🖼️ 正在构建专业分镜...")

                canvas = create_storyboard(st.session_state.files, st.session_state.shots_data, st.session_state.border_width, RATIOS[st.session_state.selected_ratio_name])

                prompt_res = ""
                if 'api_key' in st.session_state and st.session_state.api_key:
                    status.write("🧠 AI 正在撰写剧本...")
                    prompt_res = generate_sora_prompt_with_ai(
                        api_key=st.session_state.api_key,
                        base_url=st.session_state.base_url,
                        model_name=st.session_state.model_name,
                        global_style=PRESETS_STYLE[st.session_state.selected_style_key],
                        cam=PRESETS_CAMERA[st.session_state.cam_content_key],
                        phys=st.session_state.phys_content,
                        ratio=RATIOS[st.session_state.selected_ratio_name],
                        motion=st.session_state.motion_strength,
                        neg_prompt=st.session_state.neg_prompt,
                        shots_data=final_shots_data
                    )
                else:
                    prompt_res = "提示: 未配置 API Key，跳过AI生成。请在左侧配置后重试。"

                status.update(label="✨ 魔法完成！", state="complete")

                buf = io.BytesIO()
                if canvas:
                    canvas.save(buf, format="JPEG")
                    image_bytes = buf.getvalue()
                else:
                    image_bytes = None

                st.session_state.last_result = {"image_bytes": image_bytes, "prompt": prompt_res}
                st.rerun()

        if st.session_state.last_result:
            # 【修改】注释掉气球动画
            # st.balloons()
            st.markdown("---")
            st.markdown("### 📜 魔法卷轴已展开")

            prompt_result = st.session_state.last_result["prompt"]
            if prompt_result.startswith("错误:"):
                st.error(prompt_result)
            else:
                st.text_area("✨ AI 生成的Sora提示词", value=prompt_result, height=250)

            if st.session_state.last_result["image_bytes"]:
                st.markdown("---")
                st.markdown("### 🖼️ 生成的分镜总览")
                st.image(st.session_state.last_result["image_bytes"], use_container_width=True)

if __name__ == "__main__":
    main()
