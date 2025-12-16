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
    page_title="Miss Pink Elf's Studio v15.0 (Final Fix)", 
    layout="wide", 
    page_icon="🌸",
    initial_sidebar_state="expanded"
)

# ==========================================
# 👇 1. 核心样式与特效 👇
# ==========================================
def load_elysia_style():
    # ... (CSS 代码与之前版本完全一样，此处省略) ...
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
    return img

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
# 👇 5. 主工作台 (全新布局，修复表单 Bug) 👇
# ==========================================
st.title("Miss Pink Elf's Studio v15.0")

# --- 文件上传 ---
def on_upload():
    for f in st.session_state.uploader:
        st.session_state.files.append({"name": f.name, "bytes": f.getvalue()})
st.file_uploader("📂 **拖入图片**", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True, key="uploader", on_change=on_upload)

# --- 英雄区 / 工作区 ---
if not st.session_state.files:
    # ... (英雄区代码不变) ...
    st.info("👈 请上传图片")
else:
    st.caption("👇 使用图片下方的 ⬆️⬇️ 按钮调整顺序，或在表单中勾选后批量删除")

    # --- ✨ 核心修复：排序按钮移出表单 ---
    cols = st.columns(4)
    for i, file_data in enumerate(st.session_state.files):
        with cols[i % 4]:
            with st.container():
                thumb = load_preview_image(file_data["bytes"])
                st.image(thumb, use_container_width=True)
                
                # 排序按钮的回调函数
                def move_item(index, direction):
                    if direction == "up" and index > 0:
                        st.session_state.files.insert(index - 1, st.session_state.files.pop(index))
                    elif direction == "down" and index < len(st.session_state.files) - 1:
                        st.session_state.files.insert(index + 1, st.session_state.files.pop(index))
                
                # 操控区域 (现在在表单外面)
                c1, c2, _ = st.columns([1, 1, 4])
                with c1:
                    st.button("⬆️", key=f"up_{i}", on_click=move_item, args=(i, "up"), help="上移", use_container_width=True)
                with c2:
                    st.button("⬇️", key=f"down_{i}", on_click=move_item, args=(i, "down"), help="下移", use_container_width=True)

    st.markdown("---")
    
    # --- 工作台表单 (现在只负责编辑和删除) ---
    with st.form("storyboard_form"):
        st.write("#### 📝 故事编织台")
        shots_data = []
        form_cols = st.columns(4)
        delete_flags = {}

        for i, file_data in enumerate(st.session_state.files):
            with form_cols[i % 4]:
                st.caption(f"镜头 {i+1}: {file_data['name'][:20]}...") # 显示文件名
                
                # 勾选删除
                delete_flags[i] = st.checkbox("删除", key=f"del_{i}")
                
                # 输入控件
                s_type = st.selectbox("视角", ["CU", "MS", "LS"], key=f"s_{i}", label_visibility="collapsed")
                dur = st.number_input("秒", value=2.0, step=0.5, key=f"d_{i}", label_visibility="collapsed")
                desc = st.text_input("描述", placeholder="动作...", key=f"t_{i}", label_visibility="collapsed")
                
                shots_data.append({"bytes": file_data["bytes"], "shot_code": s_type, "dur": dur, "desc": desc})
        
        st.markdown("---")
        
        # 两个提交按钮
        col_btn1, col_btn2 = st.columns([2, 1])
        with col_btn1:
            submit_btn = st.form_submit_button("✨ 施展魔法 (生成) ✨", type="primary", use_container_width=True)
        with col_btn2:
            delete_submit_btn = st.form_submit_button("🗑️ 执行删除", use_container_width=True)

    # --- 处理按钮逻辑 ---
    if delete_submit_btn:
        indices_to_delete = sorted([i for i, checked in delete_flags.items() if checked], reverse=True)
        if indices_to_delete:
            for i in indices_to_delete:
                del st.session_state.files[i]
            st.success(f"已删除 {len(indices_to_delete)} 张图片！")
            time.sleep(1)
            st.rerun()

    if submit_btn:
        # ... (生成逻辑不变)
        st.balloons()
        st.success("生成成功！")

    # --- 结果展示 ---
    if 'last_result' in st.session_state and st.session_state.last_result:
        # ... (结果展示不变)
        pass
