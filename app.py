import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import gc
import time
from openai import OpenAI
from streamlit_sortable import sortable_items # ✨ 新增：拖拽排序的核心库

# ==========================================
# 👇 0. 核心配置 👇
# ==========================================
st.set_page_config(
    page_title="Miss Pink Elf's Studio v12.0", 
    layout="wide", 
    page_icon="🌸",
    initial_sidebar_state="expanded"
)

# ==========================================
# 👇 1. 核心样式与特效 👇
# ==========================================
def load_elysia_style():
    # ... (CSS 和 JS 代码与之前版本完全一样，此处省略以节省篇幅，请保留你原来的这部分代码) ...
    # 为了保证代码完整性，我还是把样式代码加上
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
        z-index: 1;
    }

    /* 标题特效 */
    h1, h2, h3 {
        background: linear-gradient(45deg, #FF69B4, #87CEFA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900 !important;
    }
    
    /* 删除按钮 */
    .delete-btn {
        position: absolute;
        top: 10px;
        right: 10px;
        background: rgba(255, 255, 255, 0.7);
        border: none;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        color: #FF69B4;
        font-size: 16px;
        font-weight: bold;
        line-height: 30px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
        z-index: 10;
    }
    .delete-btn:hover {
        background: #FF69B4;
        color: white;
        transform: scale(1.1);
    }
    </style>
    """, unsafe_allow_html=True)

# ... (樱花JS代码省略，保持原样) ...

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
def load_preview_image(_uploaded_file_bytes):
    image = Image.open(io.BytesIO(_uploaded_file_bytes))
    if image.mode in ('RGBA', 'P'): image = image.convert('RGB')
    image.thumbnail((400, 400))
    return image

def generate_sora_prompt_with_ai(api_key, base_url, model_name, global_style, cam, phys, ratio, motion, neg_prompt, shots_data):
    # ... (AI Prompt 生成逻辑不变) ...
    # (此处代码省略以保持简洁)
    pass 

# ==========================================
# 👇 3. 状态管理 & 数据 👇
# ==========================================

# 初始化 session state，这是所有交互的核心
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if 'last_result' not in st.session_state: 
    st.session_state.last_result = None

# 预设数据... (省略)
PRESETS_STYLE = {"🌸 爱莉希雅 (Anime)": "Dreamy Anime...", "🎥 电影质感 (Cinematic)": "Shot on 35mm film..."}
PRESETS_CAMERA = {"Auto (自动)": "Cinematic camera movement...", "Truck (横移)": "Smooth trucking shot..."}
TAGS_PHYSICS = ["Volumetric Lighting", "Ray-traced Reflections", "Fluid Simulation"]
RATIOS = {"16:9 (电影)": (1920, 1080), "9:16 (抖音)": (1080, 1920)}
DEFAULT_NEG = "morphing, distortion, bad anatomy, blurry, watermark, text"

# ==========================================
# 👇 4. 侧边栏 UI (封装成函数) 👇
# ==========================================
def render_sidebar():
    with st.sidebar:
        if os.path.exists("elysia_cover.jpg"):
            st.image("elysia_cover.jpg", use_container_width=True)
            st.caption("✨ “Hi~ 让我们一起把故事变得更完美吧！”")

        st.markdown("### 🏹 魔法配置")
        
        with st.expander("🤖 连接 AI 大脑", expanded=True):
            # ... (API 配置部分代码不变，省略)
            pass

        st.markdown("---")
        st.markdown("#### 🧪 Sora 2 炼金台")
        # ... (Sora 2 参数配置部分代码不变，省略)
        pass
        
        st.markdown("---")
        with st.expander("☕ 打赏作者 (小费)", expanded=False):
            if os.path.exists("pay.jpg"):
                st.image("pay.jpg", caption="投喂灵感~", use_container_width=True)
            else:
                st.info("（等待投喂中...）")

render_sidebar()

# ==========================================
# 👇 5. 主工作台 (全新交互逻辑) 👇
# ==========================================

st.title("Miss Pink Elf's Studio v12.0")

# --- 文件上传与状态更新 ---
def on_upload_change():
    """当有新文件上传时，将它们追加到 session_state 中"""
    if st.session_state.new_files:
        for file in st.session_state.new_files:
            # 存入字典，包含原始文件名和字节数据，防止 Streamlit 的 UploadedFile 对象过期
            st.session_state.uploaded_files.append({
                "name": file.name,
                "bytes": file.getvalue()
            })

uploaded_files_widget = st.file_uploader(
    "📂 **拖入或添加图片** (可多次添加)", 
    type=['jpg', 'png', 'jpeg'], 
    accept_multiple_files=True,
    key="new_files", # 用 key 绑定到 session_state
    on_change=on_upload_change # 文件变化时调用回调函数
)

# --- 工作区 / 英雄区 切换 ---
if not st.session_state.uploaded_files:
    # ... (英雄区代码不变，省略)
    st.info("👈 请上传图片开始创作")
else:
    st.markdown("**“要把这一瞬间，变成永恒的故事吗？交给我吧~”**")
    st.caption("👇 按住图片可以拖动排序，点击右上角 ❌ 可以删除")

    # --- 拖拽排序核心 ---
    # `items` 是我们要排序的数据，`key` 必须唯一
    sorted_files_data = sortable_items(
        st.session_state.uploaded_files, 
        key="sortable_gallery"
    )
    # 拖拽结束后，用排序后的结果更新 session_state
    st.session_state.uploaded_files = sorted_files_data

    # --- 带表单的工作区 ---
    with st.form("storyboard_form"):
        shots_data = []
        # ✨ 改为 4 列，UI 更紧凑
        cols = st.columns(4) 
        
        for i, file_data in enumerate(st.session_state.uploaded_files):
            col_index = i % 4
            with cols[col_index]:
                # 使用 container 来定位删除按钮
                with st.container():
                    st.markdown(f'<div style="position: relative;">', unsafe_allow_html=True)
                    
                    # 预览图
                    thumb = load_preview_image(file_data["bytes"])
                    st.image(thumb, use_container_width=True)
                    
                    # ❌ 删除按钮
                    if st.button("X", key=f"delete_{i}", help="删除这张图片"):
                        # 从 session_state 中删除
                        st.session_state.uploaded_files.pop(i)
                        st.rerun() # 立即刷新页面
                    
                    st.markdown(f'</div>', unsafe_allow_html=True)

                    # 输入控件
                    shot_options = ["ECU", "CU", "MS", "LS", "OTS", "FPV"]
                    s_type = st.selectbox("视角", shot_options, key=f"s_{i}", label_visibility="collapsed")
                    dur = st.number_input("秒", value=2.0, step=0.5, key=f"d_{i}", label_visibility="collapsed")
                    desc = st.text_input("描述", placeholder="动作...", key=f"t_{i}", label_visibility="collapsed")
                    
                    shots_data.append({"bytes": file_data["bytes"], "shot_code": s_type, "dur": dur, "desc": desc})
        
        st.markdown("---")
        submit_btn = st.form_submit_button("✨ 施展魔法 (生成) ✨", type="primary", use_container_width=True)

    # --- 生成逻辑 ---
    if submit_btn:
        # ... (生成逻辑不变，只是现在读取 shots_data 里的 'bytes' 而不是 'file')
        # (此处代码省略以保持简洁)
        st.balloons()
        st.success("生成成功！请在下方查看结果。")

    # --- 结果展示 ---
    if st.session_state.last_result:
        # ... (结果展示代码不变)
        pass
