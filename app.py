import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import gc
import time
from openai import OpenAI
from streamlit_dnd import dnd # ✨ 引入新库

# ==========================================
# 👇 0. 核心配置 👇
# ==========================================
st.set_page_config(
    page_title="Miss Pink Elf's Studio v13.0 (DND)", 
    layout="wide", 
    page_icon="🌸",
    initial_sidebar_state="expanded"
)

# ==========================================
# 👇 1. 核心样式与特效 👇
# ==========================================
def load_elysia_style():
    # ... (CSS 和 JS 代码与之前版本完全一样，此处省略) ...
    pass
load_elysia_style()

# ==========================================
# 👇 2. 工具函数库 👇
# ==========================================
# ... (get_font, load_preview_image, generate_sora_prompt_with_ai 函数保持不变) ...
@st.cache_resource
def get_font(size):
    try: return ImageFont.truetype("arialbd.ttf", size)
    except: return ImageFont.load_default()

@st.cache_data(show_spinner=False)
def load_preview_image(_bytes):
    img = Image.open(io.BytesIO(_bytes))
    if img.mode in ('RGBA','P'): img = img.convert('RGB')
    img.thumbnail((300, 300))
    return img

# ==========================================
# 👇 3. 状态管理 & 数据 👇
# ==========================================
if "files" not in st.session_state:
    st.session_state.files = []
# ... (其他预设数据省略) ...
RATIOS = {"16:9 (电影)": (1920, 1080), "9:16 (抖音)": (1080, 1920)}

# ==========================================
# 👇 4. 侧边栏 UI 👇
# ==========================================
def render_sidebar():
    # ... (侧边栏代码不变，省略)
    pass
render_sidebar()

# ==========================================
# 👇 5. 主工作台 (全新 DND 拖拽逻辑) 👇
# ==========================================
st.title("Miss Pink Elf's Studio v13.0")

# --- 文件上传 ---
def on_upload():
    for f in st.session_state.uploader:
        st.session_state.files.append({"name": f.name, "bytes": f.getvalue()})

st.file_uploader("📂 **拖入图片**", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True, key="uploader", on_change=on_upload)

# --- 英雄区 / 工作区 ---
if not st.session_state.files:
    # ... (英雄区代码不变，省略)
    st.info("👈 请上传图片")
else:
    st.caption("👇 按住图片拖动排序，点击 ❌ 删除")

    # --- ✨ 新的拖拽逻辑 (streamlit_dnd) ---
    # `dnd` 函数返回排序后的新列表
    sorted_files = dnd(st.session_state.files, key="dnd_gallery")
    if sorted_files: # 如果用户拖拽了，就更新状态
        st.session_state.files = sorted_files
    
    # --- 工作台表单 ---
    with st.form("storyboard_form"):
        shots_data = []
        cols = st.columns(4)
        
        # 创建一个临时列表用于安全删除
        files_to_render = list(st.session_state.files)

        for i, file_data in enumerate(files_to_render):
            with cols[i % 4]:
                with st.container():
                    thumb = load_preview_image(file_data["bytes"])
                    st.image(thumb, use_container_width=True)

                    # 删除按钮
                    if st.button("❌", key=f"del_{i}", help="删除"):
                        # 直接从 session state 中删除并刷新
                        st.session_state.files.pop(i)
                        st.rerun()

                    # 输入控件...
                    s_type = st.selectbox("视角", ["CU", "MS", "LS"], key=f"s_{i}", label_visibility="collapsed")
                    dur = st.number_input("秒", value=2.0, step=0.5, key=f"d_{i}", label_visibility="collapsed")
                    desc = st.text_input("描述", placeholder="动作...", key=f"t_{i}", label_visibility="collapsed")
                    
                    shots_data.append({"bytes": file_data["bytes"], "shot_code": s_type, "dur": dur, "desc": desc})
        
        st.markdown("---")
        submit_btn = st.form_submit_button("✨ 施展魔法 ✨", use_container_width=True)

    # --- 生成逻辑 ---
    if submit_btn:
        # ... (生成逻辑不变，只是读取 shots_data 里的 'bytes')
        st.balloons()
        st.success("生成成功！")

    # --- 结果展示 ---
    if 'last_result' in st.session_state and st.session_state.last_result:
        # ... (结果展示代码不变)
        pass
