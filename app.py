import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import gc
import time
from openai import OpenAI
from streamlit_sortable import sortable_items # ✨ 拖拽排序的核心库

# ==========================================
# 👇 0. 核心配置 👇
# ==========================================
st.set_page_config(
    page_title="Miss Pink Elf's Studio v12.1", # 版本号+0.1
    layout="wide", 
    page_icon="🌸",
    initial_sidebar_state="expanded"
)

# ==========================================
# 👇 1. 核心样式与特效 👇
# ==========================================
def load_elysia_style():
    # ... (CSS 和 JS 代码与之前版本完全一样，此处省略以节省篇幅，请保留你原来的这部分代码) ...
    st.markdown("""
    <style>
    /* 全局优化 */
    .stApp {
        background: linear-gradient(135deg, #FFF0F5 0%, #E6E6FA 60%, #E0FFFF 100%);
        font-family: 'Comic Sans MS', 'Microsoft YaHei', sans-serif;
        color: #4A4A4A;
    }
    
    /* ... 其他样式保持不变 ... */
    
    /* 删除按钮 */
    .delete-btn {
        position: absolute;
        top: 8px; /* 微调位置 */
        right: 8px;
        background: rgba(255, 255, 255, 0.7);
        border: none;
        border-radius: 50%;
        width: 28px; /* 微调大小 */
        height: 28px;
        color: #FF69B4;
        font-size: 14px;
        font-weight: bold;
        line-height: 28px;
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

load_elysia_style()

# ==========================================
# 👇 2. 工具函数库 👇
# ==========================================
# ... (get_font, load_preview_image, generate_sora_prompt_with_ai 函数保持不变) ...
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

# ==========================================
# 👇 3. 状态管理 & 数据 👇
# ==========================================

# 初始化 session state
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if 'last_result' not in st.session_state: 
    st.session_state.last_result = None

# 预设数据... (省略)
PRESETS_STYLE = {"🌸 爱莉希雅 (Anime)": "Dreamy Anime...", "🎥 电影质感 (Cinematic)": "Shot on 35mm film..."}
PRESETS_CAMERA = {"Auto (自动)": "Cinematic camera movement...", "Truck (横移)": "Smooth trucking shot..."}

# ==========================================
# 👇 4. 侧边栏 UI (封装成函数) 👇
# ==========================================
def render_sidebar():
    # ... (侧边栏代码不变，省略)
    pass

render_sidebar()

# ==========================================
# 👇 5. 主工作台 (全新交互逻辑) 👇
# ==========================================

st.title("Miss Pink Elf's Studio v12.1")

# --- 文件上传与状态更新 ---
def on_upload_change():
    """当有新文件上传时，将它们追加到 session_state 中"""
    if st.session_state.new_files:
        for file in st.session_state.new_files:
            st.session_state.uploaded_files.append({
                "name": file.name,
                "bytes": file.getvalue()
            })

uploaded_files_widget = st.file_uploader(
    "📂 **拖入或添加图片** (可多次添加)", 
    type=['jpg', 'png', 'jpeg'], 
    accept_multiple_files=True,
    key="new_files", 
    on_change=on_upload_change
)

# --- 工作区 / 英雄区 切换 ---
if not st.session_state.uploaded_files:
    # ... (英雄区代码不变，省略)
    st.info("👈 请上传图片开始创作")
else:
    st.caption("👇 按住图片可以拖动排序，点击右上角 ❌ 可以删除")

    # --- 拖拽排序核心 ---
    sorted_files_data = sortable_items(
        st.session_state.uploaded_files, 
        key="sortable_gallery"
    )
    st.session_state.uploaded_files = sorted_files_data

    # --- 💥 核心 Bug 修复：删除逻辑 ---
    # 定义一个回调函数，当按钮被点击时，只记录要删除的索引
    def mark_for_deletion(index):
        st.session_state.delete_index = index

    # 在主渲染流程开始前，检查是否有待删除项
    if 'delete_index' in st.session_state and st.session_state.delete_index is not None:
        del st.session_state.uploaded_files[st.session_state.delete_index]
        st.session_state.delete_index = None # 重置标记
        st.rerun() # 安全地刷新
    # ======================================

    with st.form("storyboard_form"):
        shots_data = []
        cols = st.columns(4) 
        
        for i, file_data in enumerate(st.session_state.uploaded_files):
            col_index = i % 4
            with cols[col_index]:
                with st.container():
                    # st.markdown(f'<div style="position: relative;">', unsafe_allow_html=True) # 这行可以简化掉
                    
                    thumb = load_preview_image(file_data["bytes"])
                    st.image(thumb, use_container_width=True)
                    
                    # ❌ 删除按钮：现在调用回调函数，而不是直接 reran
                    st.button("X", key=f"delete_{i}", help="删除这张图片", on_click=mark_for_deletion, args=(i,))
                    
                    # st.markdown(f'</div>', unsafe_allow_html=True) # 这行可以简化掉

                    # 输入控件... (不变)
                    shot_options = ["ECU", "CU", "MS", "LS"]
                    s_type = st.selectbox("视角", shot_options, key=f"s_{i}", label_visibility="collapsed")
                    dur = st.number_input("秒", value=2.0, step=0.5, key=f"d_{i}", label_visibility="collapsed")
                    desc = st.text_input("描述", placeholder="动作...", key=f"t_{i}", label_visibility="collapsed")
                    
                    shots_data.append({"bytes": file_data["bytes"], "shot_code": s_type, "dur": dur, "desc": desc})
        
        st.markdown("---")
        submit_btn = st.form_submit_button("✨ 施展魔法 (生成) ✨", type="primary", use_container_width=True)

    # --- 生成逻辑 ---
    if submit_btn:
        # ... (生成逻辑不变)
        st.balloons()
        st.success("生成成功！")

    # --- 结果展示 ---
    if st.session_state.last_result:
        # ... (结果展示不变)
        pass
