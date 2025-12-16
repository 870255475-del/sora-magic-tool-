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
    # ... (CSS 和 JS 代码与之前版本完全一样，此处省略) ...
    st.markdown("""<style>/* ... 你的粉色CSS ... */</style>""", unsafe_allow_html=True)

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
    img.thumbnail((400, 400))
    # 将缩略图转回 bytes，方便在 HTML 中显示
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

# ==========================================
# 👇 3. 状态管理 & 数据 👇
# ==========================================
if "files" not in st.session_state: st.session_state.files = []
if 'last_result' not in st.session_state: st.session_state.last_result = None
# ... (其他预设数据省略) ...
RATIOS = {"16:9 (电影)": (1920, 1080), "9:16 (抖音)": (1080, 1920)}

# ==========================================
# 👇 4. 侧边栏 UI 👇
# ==========================================
def render_sidebar():
    # ... (侧边栏代码不变，省略) ...
    pass
render_sidebar()

# ==========================================
# 👇 5. 主工作台 (上传逻辑修复) 👇
# ==========================================
st.title("Miss Pink Elf's Studio v16.1 (Final)")

# --- 🚀 修复后的上传逻辑 ---
newly_uploaded_files = st.file_uploader(
    "📂 **拖入或添加图片** (可多次添加)", 
    type=['jpg', 'png', 'jpeg'], 
    accept_multiple_files=True,
    key="uploader"
)

if newly_uploaded_files:
    existing_filenames = {f['name'] for f in st.session_state.files}
    
    # 标记是否有新文件被添加
    has_new_files = False
    for file in newly_uploaded_files:
        if file.name not in existing_filenames:
            st.session_state.files.append({
                "name": file.name,
                "bytes": file.getvalue()
            })
            existing_filenames.add(file.name)
            has_new_files = True
    
    # 如果真的有新文件，强制刷新一次页面
    if has_new_files:
        st.rerun()

# --- 英雄区 / 工作区 ---
if not st.session_state.files:
    # ... (英雄区代码不变，省略) ...
    st.info("👈 请上传图片")
else:
    st.caption("👇 按住图片拖动排序，点击右上角 ❌ 删除")

    def mark_for_deletion(index):
        st.session_state.delete_index = index

    if 'delete_index' in st.session_state and st.session_state.delete_index is not None:
        del st.session_state.files[st.session_state.delete_index]
        st.session_state.delete_index = None
        st.rerun()

    # --- 拖拽核心 ---
    sorted_items = sortable_items(st.session_state.files, key="sortable_gallery", direction="horizontal")
    st.session_state.files = sorted_items

    # --- 工作台表单 ---
    with st.form("storyboard_form"):
        shots_data = []
        cols = st.columns(4) 
        for i, file_data in enumerate(st.session_state.files):
            with cols[i % 4]:
                with st.container():
                    st.markdown('<div style="position: relative;">', unsafe_allow_html=True)
                    thumb_bytes = load_preview_image(file_data["bytes"])
                    st.image(thumb_bytes, use_container_width=True)
                    st.button("X", key=f"delete_{i}", on_click=mark_for_deletion, args=(i,), help="删除")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    s_type = st.selectbox("视角", ["CU", "MS", "LS"], key=f"s_{i}", label_visibility="collapsed")
                    dur = st.number_input("秒", value=2.0, step=0.5, key=f"d_{i}", label_visibility="collapsed")
                    desc = st.text_input("描述", placeholder="动作...", key=f"t_{i}", label_visibility="collapsed")
                    shots_data.append({"bytes": file_data["bytes"], "shot_code": s_type, "dur": dur, "desc": desc})
        
        st.markdown("---")
        submit_btn = st.form_submit_button("✨ 施展魔法 ✨", type="primary", use_container_width=True)

    # --- 生成逻辑 ---
    if submit_btn:
        # ... (生成逻辑不变) ...
        st.balloons()
        st.success("生成成功！")

    # --- 结果展示 ---
    if st.session_state.last_result:
        # ... (结果展示不变) ...
        pass
