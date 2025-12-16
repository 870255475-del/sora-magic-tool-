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
    page_title="Miss Pink Elf's Studio v19.0 (Ultimate)", 
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
# 👇 2. 工具函数库 (封装与优化) 👇
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
if "files" not in st.session_state: st.session_state.files = []
if 'last_result' not in st.session_state: st.session_state.last_result = None
# ... (其他预设数据省略) ...
RATIOS = {"16:9 (电影)": (1920, 1080), "9:16 (抖音)": (1080, 1920)}

# ==========================================
# 👇 4. UI 渲染函数 (代码封装) 👇
# ==========================================

def render_sidebar():
    with st.sidebar:
        # ... (侧边栏代码不变) ...
        pass

def render_hero_section():
    st.markdown("<br>", unsafe_allow_html=True)
    # ... (英雄区代码不变) ...
    st.info("👈 请上传图片")

def render_workspace():
    st.caption("👇 在下方输入框中用数字排序 (例如: 3,1,2,4)，或勾选后批量删除")

    # --- ✨ 全新自定义排序 ---
    current_order = ", ".join(map(str, range(1, len(st.session_state.files) + 1)))
    new_order_str = st.text_input("调整顺序", value=current_order, help="输入新的顺序，用逗号隔开，例如: 3,1,2,4")
    
    if st.button("🔄 应用排序", use_container_width=True):
        try:
            new_order_indices = [int(i.strip()) - 1 for i in new_order_str.split(',')]
            if len(new_order_indices) == len(st.session_state.files) and all(0 <= i < len(st.session_state.files) for i in new_order_indices):
                st.session_state.files = [st.session_state.files[i] for i in new_order_indices]
                st.success("顺序已更新！")
                time.sleep(1)
                st.rerun()
            else:
                st.error("输入的顺序无效，请检查数字是否正确且不重复。")
        except:
            st.error("格式错误，请输入类似 '3,1,2,4' 的格式。")

    st.markdown("---")
    
    # --- 工作台表单 ---
    with st.form("storyboard_form"):
        # ... (表单代码不变) ...
        submit_btn = st.form_submit_button("✨ 施展魔法 ✨")
    
    # ... (按钮逻辑和结果展示不变) ...
    pass

# ==========================================
# 👇 5. 主程序入口 👇
# ==========================================
def main():
    render_sidebar()
    
    st.title("Miss Pink Elf's Studio v19.0 (Ultimate)")

    # --- 🐞 全新上传逻辑 (彻底修复重复 Bug) ---
    newly_uploaded = st.file_uploader(
        "📂 **拖入或添加图片**", 
        type=['jpg', 'png', 'jpeg'], 
        accept_multiple_files=True,
        key="uploader"
    )
    
    if newly_uploaded:
        # 只处理一次，处理后清空 uploader
        existing_names = {f['name'] for f in st.session_state.files}
        for f in newly_uploaded:
            if f.name not in existing_names:
                st.session_state.files.append({"name": f.name, "bytes": f.getvalue()})
        # 清空上传组件的状态，防止重复触发
        st.session_state.uploader = []
        st.rerun()

    # 根据是否有文件，决定显示英雄区还是工作区
    if not st.session_state.files:
        render_hero_section()
    else:
        render_workspace()

if __name__ == "__main__":
    main()
