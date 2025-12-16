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
    page_title="Miss Pink Elf's Studio v31.0 (Ultimate Stable)", 
    layout="wide", 
    page_icon="🌸",
    initial_sidebar_state="expanded"
)

# ==========================================
# 👇 1. 核心样式与特效 👇
# ==========================================
def load_elysia_style():
    st.markdown("""
    <style>
    /* 全局 */
    .stApp { background: linear-gradient(135deg, #FFF0F5 0%, #E6E6FA 100%); font-family: 'Comic Sans MS', sans-serif; }
    h1, h2, h3, h4 { background: -webkit-linear-gradient(45deg, #FF69B4, #87CEFA); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important; }
    
    /* 侧边栏 */
    section[data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.75); backdrop-filter: blur(20px); }

    /* 卡片 */
    .card {
        position: relative;
        background: rgba(255,255,255,0.7);
        border-radius: 18px;
        padding: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.05);
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    .card:hover { border-color: #FFB6C1; }
    
    /* 删除按钮 */
    .delete-btn {
        position: absolute; top: 10px; right: 10px;
        background: white; border: none; border-radius: 50%;
        width: 30px; height: 30px; color: #FF69B4;
        font-size: 16px; font-weight: bold; cursor: pointer;
        transition: all 0.2s; z-index: 10;
        display: flex; align-items: center; justify-content: center;
    }
    .delete-btn:hover { background: #FF69B4; color: white; transform: scale(1.1); }

    /* 输入控件 */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 12px !important; border: 2px solid #FFE4E1 !important;
        background: rgba(255, 255, 255, 0.85) !important;
    }
    
    /* 提交按钮 */
    div.stButton > button {
        background: linear-gradient(90deg, #FF9A9E 0%, #FECFEF 100%);
        color: white !important;
        border-radius: 20px !important; border: none !important;
        box-shadow: 0 4px 12px rgba(255, 105, 180, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

load_elysia_style()

# ==========================================
# 👇 2. 工具函数库 👇
# ==========================================
@st.cache_resource
def get_font(size):
    possible_fonts = ["DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial.ttf"]
    for f in possible_fonts:
        try: return ImageFont.truetype(f, size)
        except IOError: continue
    return ImageFont.load_default()

@st.cache_data(show_spinner=False)
def load_preview_image(file_name, _bytes):
    image = Image.open(io.BytesIO(_bytes))
    image.thumbnail((400, 400))
    return image

def generate_sora_prompt_with_ai(api_key, base_url, model_name, global_style, cam, phys, ratio, motion, neg_prompt, shots_data):
    if not api_key: return "API Key not provided."
    if not base_url: base_url = "https://api.openai.com/v1"
    client = OpenAI(api_key=api_key, base_url=base_url)
    tech_specs = f"Specs: Ratio {ratio}, Motion {motion}/10, {cam}, {phys}"
    system_prompt = f"You are an expert Sora 2 prompt engineer..."
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
if "files" not in st.session_state: st.session_state.files = []
if 'last_result' not in st.session_state: st.session_state.last_result = None
if 'history' not in st.session_state: st.session_state.history = []

SHOT_OPTIONS = ["CU (特写)", "MS (中景)", "LS (全景)", "ECU (极特写)", "OTS (过肩)", "FPV (第一人称)"]
PRESETS_STYLE = {"🌸 爱莉希雅 (Anime)": "Dreamy Anime...", "🎥 电影质感 (Cinematic)": "Shot on 35mm film..."}
PRESETS_CAMERA = {"Auto (自动)": "Cinematic camera movement...", "Truck (横移)": "Smooth trucking shot..."}
TAGS_PHYSICS = ["Volumetric Lighting", "Ray-traced Reflections", "Fluid Simulation"]
RATIOS = {"16:9 (电影)": (1920, 1080), "9:16 (抖音)": (1080, 1920)}
DEFAULT_NEG = "morphing, distortion, bad anatomy, blurry, watermark, text"
MAX_FILES = 6

# ==========================================
# 👇 4. UI 渲染函数 👇
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
                base = "https://ark.cn-beijing.volces.com/api/v3"
            elif api_provider == "DeepSeek":
                st.markdown("👉 [**点我注册 DeepSeek**](https://platform.deepseek.com/)")
                base = "https://api.deepseek.com"; model = "deepseek-chat"
            st.session_state.api_key = st.text_input("API Key", type="password")
            st.session_state.base_url = st.text_input("Base URL", value=base)
            st.session_state.model_name = st.text_input("Model", value=model)

        st.markdown("---")
        st.markdown("#### 🧪 Sora 2 炼金台")
        st.session_state.selected_style = st.selectbox("🔮 滤镜风格", list(PRESETS_STYLE.keys()))
        st.session_state.cam_content = st.selectbox("📷 运镜方式", list(PRESETS_CAMERA.keys()))
        st.session_state.phys_content = st.multiselect("🌊 物理与光影", TAGS_PHYSICS, default=["Volumetric Lighting"])
        st.session_state.selected_ratio_name = st.selectbox("画幅比例", list(RATIOS.keys()))
        st.session_state.motion_strength = st.slider("⚡ 动态幅度", 1, 10, 5)
        st.session_state.neg_prompt = st.text_area("⛔ 负面提示词", value=DEFAULT_NEG, height=70)
        st.markdown("---")
        with st.expander("☕ 打赏作者", expanded=False):
            if os.path.exists("pay.jpg"):
                st.image("pay.jpg")

def render_hero_section():
    st.info(f"👈 请上传图片开始创作 (最多 {MAX_FILES} 张)")
    # (英雄区代码不变)

def render_results():
    if st.session_state.last_result:
        # (结果展示代码不变)
        pass

# ==========================================
# 👇 5. 主程序入口 👇
# ==========================================
def main():
    render_sidebar()
    st.title("Miss Pink Elf's Studio v31.0")

    # --- 上传逻辑 ---
    uploaded_files_now = st.file_uploader(f"📂 **拖入图片 (最多 {MAX_FILES} 张)**", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True, key="uploader")
    if uploaded_files_now:
        if len(st.session_state.files) >= MAX_FILES:
            st.warning(f"最多只能处理 {MAX_FILES} 张图片！")
        else:
            existing_names = {f['name'] for f in st.session_state.files}
            files_to_add = [f for f in newly_uploaded_files if f.name not in existing_names][:MAX_FILES - len(st.session_state.files)]
            for file in files_to_add:
                st.session_state.files.append({"name": file.name, "bytes": file.getvalue()})
            if files_to_add: st.rerun()

    # --- 英雄区 / 工作区 ---
    if not st.session_state.files:
        render_hero_section()
    else:
        st.caption("👇 在每个卡片中编辑信息，使用 ⬆️⬇️ 调整顺序，或点击 ❌ 删除")
        st.write("---")

        # --- ✨ 全新“多合一”卡片式工作区 (无表单，无拖拽) ---
        cols = st.columns(3)
        shots_data = []

        # 按钮回调函数 (高性能，无 reran)
        def move_item(index, direction):
            if direction == "up" and index > 0: st.session_state.files.insert(index - 1, st.session_state.files.pop(index))
            elif direction == "down" and index < len(st.session_state.files) - 1: st.session_state.files.insert(index + 1, st.session_state.files.pop(index))
        def delete_item(index):
            st.session_state.files.pop(index)

        for i, file_data in enumerate(st.session_state.files):
            with cols[i % 3]:
                with st.container():
                    st.markdown('<div class="card">', unsafe_allow_html=True) # 应用卡片样式
                    st.image(load_preview_image(file_data["name"], file_data["bytes"]), use_container_width=True)
                    
                    st.caption(f"镜头 {i+1}")
                    
                    s_type_full = st.selectbox("视角", SHOT_OPTIONS, key=f"s_{i}")
                    dur = st.number_input("秒", value=2.0, step=0.5, key=f"d_{i}")
                    desc = st.text_input("描述", placeholder="动作...", key=f"t_{i}")
                    
                    c1, c2, c3 = st.columns([1,1,1])
                    with c1: st.button("⬆️", key=f"up_{i}", on_click=move_item, args=(i, "up"), use_container_width=True)
                    with c2: st.button("⬇️", key=f"down_{i}", on_click=move_item, args=(i, "down"), use_container_width=True)
                    with c3: st.button("❌", key=f"del_{i}", on_click=delete_item, args=(i,), use_container_width=True, type="primary")

                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    shots_data.append({"bytes": file_data["bytes"], "shot_code": s_type_full.split(" ")[0], "dur": dur, "desc": desc})

        st.write("---")
        if st.button("✨ 施展魔法 (生成分镜 + 咒语) ✨", type="primary", use_container_width=True):
            with st.status("💎 魔法咏唱中...", expanded=True) as status:
                # ... (生成逻辑不变)
                status.update(label="✨ 魔法完成！", state="complete")
                st.session_state.last_result = {"image_bytes": b'', "prompt": "Generated prompt"}

    render_results()

if __name__ == "__main__":
    main()
