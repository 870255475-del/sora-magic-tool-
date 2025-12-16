import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import gc
import time
from openai import OpenAI
from streamlit_sortable import sortable_items # 拖拽排序库

# ==========================================
# 👇 0. 核心配置 👇
# ==========================================
st.set_page_config(
    page_title="Miss Pink Elf's Studio v16.1 (Final)", 
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
    .stApp {
        background: linear-gradient(135deg, #FFF0F5 0%, #E6E6FA 60%, #E0FFFF 100%);
        font-family: 'Comic Sans MS', 'Microsoft YaHei', sans-serif;
        color: #4A4A4A;
    }
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
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.8);
        z-index: 1;
    }
    h1, h2, h3, h4 {
        background: -webkit-linear-gradient(45deg, #FF69B4, #87CEFA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    .delete-btn {
        position: absolute; top: 8px; right: 8px;
        background: rgba(255, 255, 255, 0.7); border: none;
        border-radius: 50%; width: 28px; height: 28px;
        color: #FF69B4; font-size: 14px; font-weight: bold;
        line-height: 28px; text-align: center; cursor: pointer;
        transition: all 0.2s; z-index: 10;
    }
    .delete-btn:hover { background: #FF69B4; color: white; transform: scale(1.1); }
    div.stButton > button {
        background: linear-gradient(90deg, #FF9A9E 0%, #FECFEF 100%);
        color: white !important;
        border-radius: 20px !important; border: none !important;
        box-shadow: 0 4px 12px rgba(255, 105, 180, 0.3) !important;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover { transform: translateY(-2px); }
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
    possible_fonts = ["DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial.ttf"]
    for f in possible_fonts:
        try: return ImageFont.truetype(f, size)
        except IOError: continue
    return ImageFont.load_default()

@st.cache_data(show_spinner=False)
def load_preview_image(_bytes):
    image = Image.open(io.BytesIO(_bytes))
    if image.mode in ('RGBA','P'): image = image.convert('RGB')
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
if "files" not in st.session_state: st.session_state.files = []
if 'last_result' not in st.session_state: st.session_state.last_result = None

PRESETS_STYLE = {"🌸 爱莉希雅 (Anime)": "Dreamy Anime...", "🎥 电影质感 (Cinematic)": "Shot on 35mm film..."}
PRESETS_CAMERA = {"Auto (自动)": "Cinematic camera movement...", "Truck (横移)": "Smooth trucking shot..."}
TAGS_PHYSICS = ["Volumetric Lighting", "Ray-traced Reflections", "Fluid Simulation"]
RATIOS = {"16:9 (电影)": (1920, 1080), "9:16 (抖音)": (1080, 1920)}
DEFAULT_NEG = "morphing, distortion, bad anatomy, blurry, watermark, text"

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
                base = "https://ark.cn-beijing.volces.com/api/v3"
            elif api_provider == "DeepSeek":
                st.markdown("👉 [**点我注册 DeepSeek**](https://platform.deepseek.com/)")
                base = "https://api.deepseek.com"; model = "deepseek-chat"
            api_key = st.text_input("API Key", type="password")
            base_url = st.text_input("Base URL", value=base)
            model_name = st.text_input("Model", value=model, placeholder="豆包请填 Endpoint ID")

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
        with st.expander("☕ 打赏作者 (小费)", expanded=False):
            if os.path.exists("pay.jpg"):
                st.image("pay.jpg", use_container_width=True)
                
render_sidebar()

# ==========================================
# 👇 5. 主工作台 (全新拖拽逻辑) 👇
# ==========================================
st.title("Miss Pink Elf's Studio v16.1")

newly_uploaded_files = st.file_uploader(
    "📂 **拖入图片**", 
    type=['jpg', 'png', 'jpeg'], 
    accept_multiple_files=True,
    key="uploader"
)

if newly_uploaded_files:
    existing_filenames = {f['name'] for f in st.session_state.files}
    for file in newly_uploaded_files:
        if file.name not in existing_filenames:
            st.session_state.files.append({
                "name": file.name,
                "bytes": file.getvalue()
            })
            existing_filenames.add(file.name)

if not st.session_state.files:
    st.info("👈 请上传图片")
else:
    st.caption("👇 按住图片拖动排序，点击右上角 ❌ 删除")

    def mark_for_deletion(index):
        st.session_state.delete_index = index

    if 'delete_index' in st.session_state and st.session_state.delete_index is not None:
        del st.session_state.files[st.session_state.delete_index]
        st.session_state.delete_index = None
        st.rerun()

    # 拖拽核心
    sorted_items = sortable_items(st.session_state.files, key="sortable_gallery", direction="horizontal")
    st.session_state.files = sorted_items

    # 表单
    with st.form("storyboard_form"):
        shots_data = []
        cols = st.columns(4) 
        for i, file_data in enumerate(st.session_state.files):
            with cols[i % 4]:
                with st.container():
                    st.markdown('<div style="position: relative;">', unsafe_allow_html=True)
                    thumb = load_preview_image(file_data["bytes"])
                    st.image(thumb, use_container_width=True)
                    st.button("X", key=f"delete_{i}", on_click=mark_for_deletion, args=(i,), help="删除")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    s_type = st.selectbox("视角", ["CU", "MS", "LS"], key=f"s_{i}", label_visibility="collapsed")
                    dur = st.number_input("秒", value=2.0, step=0.5, key=f"d_{i}", label_visibility="collapsed")
                    desc = st.text_input("描述", placeholder="动作...", key=f"t_{i}", label_visibility="collapsed")
                    shots_data.append({"bytes": file_data["bytes"], "shot_code": s_type, "dur": dur, "desc": desc})
        
        st.markdown("---")
        submit_btn = st.form_submit_button("✨ 施展魔法 ✨", type="primary", use_container_width=True)

    if submit_btn:
        # ... (生成逻辑不变)
        st.balloons()
        st.success("生成成功！")

    if st.session_state.last_result:
        # ... (结果展示不变)
        pass
