import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import gc
import time
from openai import OpenAI

# ==========================================
# 0. Core Configuration
# ==========================================
st.set_page_config(
    page_title="Miss Pink Elf's Studio v14.0 (Stable)", 
    layout="wide", 
    page_icon="🌸",
    initial_sidebar_state="expanded"
)

# ==========================================
# 1. Core Styles & Effects
# ==========================================
def load_elysia_style():
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
        box-shadow: 2px 0 15px rgba(255, 192, 203, 0.15);
        z-index: 1;
    }
    h1, h2, h3, h4 {
        background: -webkit-linear-gradient(45deg, #FF69B4, #87CEFA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
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
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 12px !important; border: 2px solid #FFE4E1 !important;
        background: rgba(255, 255, 255, 0.9) !important;
    }
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

load_elysia_style()

# ==========================================
# 2. Utility Functions
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
    - Incorporate negative prompts: "Avoid {neg_prompt}."
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
# 3. Data & State Management
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

# ==========================================
# 4. Sidebar UI
# ==========================================
with st.sidebar:
    if os.path.exists("elysia_cover.jpg"):
        st.image("elysia_cover.jpg", use_container_width=True)
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
    c1,
