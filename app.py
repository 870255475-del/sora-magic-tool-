import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import gc
import time
from openai import OpenAI
from streamlit_sortable import sortable_items # ✨ 拖拽排序回归！

# ==========================================
# 👇 0. 核心配置 👇
# ==========================================
st.set_page_config(
    page_title="Miss Pink Elf's Studio v16.0 (D&D)", 
    layout="wide", 
    page_icon="🌸",
    initial_sidebar_state="expanded"
)

# ==========================================
# 👇 1. 核心样式与特效 👇
# ==========================================
def load_elysia_style():
    # ... (CSS 和 JS 代码与之前版本完全一样，此处省略以节省篇幅) ...
    st.markdown("""<style>/* ... 你的粉色CSS ... */</style>""", unsafe_allow_html=True)
load_elysia_style()

# ==========================================
# 👇 2. 工具函数库 👇
# ==========================================
@st.cache_resource
def get_font(size):
    # ... (字体函数不变) ...
    pass
@st.cache_data(show_spinner=False)
def load_preview_image(_bytes):
    # ... (缩略图函数不变) ...
    pass
def generate_sora_prompt_with_ai(...):
    # ... (AI Prompt 生成逻辑不变) ...
    pass

# ==========================================
# 👇 3. 状态管理 & 数据 👇
# ==========================================
# 初始化 session state
if "files" not in st.session_state:
    st.session_state.files = []
if 'last_result' not in st.session_state: 
    st.session_state.last_result = None
# ... (其他预设数据省略) ...
RATIOS = {"16:9 (电影)": (1920, 1080), "9:16 (抖音)": (1080, 1920)}

# ==========================================
# 👇 4. 侧边栏 UI 👇
# ==========================================
def render_sidebar():
    # ... (侧边栏代码不变) ...
    pass
render_sidebar()

# ==========================================
# 👇 5. 主工作台 (全新上传与拖拽逻辑) 👇
# ==========================================
st.title("Miss Pink Elf's Studio v16.0")

# --- 🚀 全新上传逻辑：防止重复添加 ---
newly_uploaded_files = st.file_uploader(
    "📂 **拖入或添加图片** (可多次添加)", 
    type=['jpg', 'png', 'jpeg'], 
    accept_multiple_files=True,
    key="uploader" # 不需要 on_change 了
)

if newly_uploaded_files:
    # 获取当前已存储的文件名列表
    existing_filenames = {f['name'] for f in st.session_state.files}
    
    # 只把【新】文件加入列表，防止重复
    for file in newly_uploaded_files:
        if file.name not in existing_filenames:
            st.session_state.files.append({
                "name": file.name,
                "bytes": file.getvalue()
            })
            existing_filenames.add(file.name) # 立即更新，防止单次上传的重复

# --- 英雄区 / 工作区 ---
if not st.session_state.files:
    # ... (英雄区代码不变) ...
    st.info("👈 请上传图片")
else:
    st.caption("👇 按住图片拖动排序，点击右上角 ❌ 删除")

    # --- 🐞 Bug 修复：删除逻辑 ---
    def mark_for_deletion(index):
        st.session_state.delete_index = index

    if 'delete_index' in st.session_state and st.session_state.delete_index is not None:
        del st.session_state.files[st.session_state.delete_index]
        st.session_state.delete_index = None
        st.rerun()

    # --- ✨ 拖拽排序核心 ---
    # `sortable_items` 现在包裹了所有图片
    sorted_items = sortable_items(
        st.session_state.files,
        key="sortable_gallery",
        direction="horizontal"
    )
    # 拖拽结束后，用新顺序更新 state
    st.session_state.files = sorted_items

    # --- 工作台表单 ---
    with st.form("storyboard_form"):
        shots_data = []
        cols = st.columns(4) 

        for i, file_data in enumerate(st.session_state.files):
            with cols[i % 4]:
                with st.container():
                    st.markdown(f'<div style="position: relative;">', unsafe_allow_html=True)
                    thumb = load_preview_image(file_data["bytes"])
                    st.image(thumb, use_container_width=True)
                    
                    # 删除按钮 (使用回调，绝对稳定)
                    st.button("X", key=f"delete_{i}", on_click=mark_for_deletion, args=(i,), help="删除")
                    st.markdown(f'</div>', unsafe_allow_html=True)

                    # 输入控件...
                    s_type = st.selectbox("视角", ["CU", "MS", "LS"], key=f"s_{i}", label_visibility="collapsed")
                    dur = st.number_input("秒", value=2.0, step=0.5, key=f"d_{i}", label_visibility="collapsed")
                    desc = st.text_input("描述", placeholder="动作...", key=f"t_{i}", label_visibility="collapsed")
                    
                    shots_data.append({"bytes": file_data["bytes"], "shot_code": s_type, "dur": dur, "desc": desc})
        
        st.markdown("---")
        submit_btn = st.form_submit_button("✨ 施展魔法 (生成) ✨", type="primary", use_container_width=True)

    # --- 生成逻辑 ---
    if submit_btn:
        # ... (生成逻辑不变) ...
        st.balloons()
        st.success("生成成功！")

    # --- 结果展示 ---
    if st.session_state.last_result:
        # ... (结果展示不变) ...
        pass
