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
    page_title="Miss Pink Elf's Studio v22.0 (Performance)", 
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
@st.cache_resource
def get_font(size):
    # ... (字体函数不变) ...
    pass
@st.cache_data(show_spinner=False)
def load_preview_image(file_name, _bytes): # 签名不变
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
# 👇 4. UI 渲染函数 👇
# ==========================================
def render_sidebar():
    # ... (侧边栏代码不变) ...
    pass
def render_hero_section():
    # ... (英雄区代码不变) ...
    st.info("👈 请上传图片")

def render_workspace():
    st.caption("👇 使用图片下方的 ⬆️⬇️ 按钮调整顺序，或在表单中勾选后批量删除")

    # --- ✨ 全新高性能排序与删除逻辑 ---
    
    # 按钮回调函数 (现在只修改数据，不刷新页面)
    def move_item(index, direction):
        if direction == "up" and index > 0:
            st.session_state.files.insert(index - 1, st.session_state.files.pop(index))
        elif direction == "down" and index < len(st.session_state.files) - 1:
            st.session_state.files.insert(index + 1, st.session_state.files.pop(index))

    # 排序按钮 (在表单外)
    cols_sort = st.columns(4)
    for i, file_data in enumerate(st.session_state.files):
        with cols_sort[i % 4]:
            with st.container():
                thumb = load_preview_image(file_data["name"], file_data["bytes"])
                st.image(thumb, use_container_width=True)
                
                c1, c2, _ = st.columns([1, 1, 4])
                with c1: st.button("⬆️", key=f"up_{i}", on_click=move_item, args=(i, "up"), use_container_width=True)
                with c2: st.button("⬇️", key=f"down_{i}", on_click=move_item, args=(i, "down"), use_container_width=True)

    st.markdown("---")
    
    # 表单
    with st.form("storyboard_form"):
        st.write("#### 📝 故事编织台")
        shots_data = []
        form_cols = st.columns(4)
        delete_flags = {}
        for i, file_data in enumerate(st.session_state.files):
            with form_cols[i % 4]:
                st.caption(f"镜头 {i+1}")
                delete_flags[i] = st.checkbox("删除", key=f"del_{i}")
                s_type = st.selectbox("视角", ["CU", "MS", "LS"], key=f"s_{i}", label_visibility="collapsed")
                dur = st.number_input("秒", value=2.0, step=0.5, key=f"d_{i}", label_visibility="collapsed")
                desc = st.text_input("描述", placeholder="动作...", key=f"t_{i}", label_visibility="collapsed")
                shots_data.append({"bytes": file_data["bytes"], "shot_code": s_type, "dur": dur, "desc": desc})
        st.markdown("---")
        col_btn1, col_btn2 = st.columns([2, 1])
        with col_btn1: submit_btn = st.form_submit_button("✨ 施展魔法 ✨", type="primary", use_container_width=True)
        with col_btn2: delete_submit_btn = st.form_submit_button("🗑️ 执行删除")

    # --- 处理按钮逻辑 (移出表单，在主流程中处理) ---
    if delete_submit_btn:
        indices_to_delete = sorted([i for i, checked in delete_flags.items() if checked], reverse=True)
        if indices_to_delete:
            for i in indices_to_delete: del st.session_state.files[i]
            st.success(f"已删除 {len(indices_to_delete)} 张图片！")
            time.sleep(1); st.rerun() # 只有在真正需要大幅重绘时才刷新

    if submit_btn:
        # ... (生成逻辑不变)
        st.balloons()
        st.success("生成成功！")
    
    if st.session_state.last_result:
        # ... (结果展示不变)
        pass

# ==========================================
# 👇 5. 主程序入口 (全新上传逻辑) 👇
# ==========================================
def main():
    render_sidebar()
    st.title("Miss Pink Elf's Studio v22.0")

    # --- 🐞 全新上传逻辑 (彻底修复所有状态 Bug) ---
    uploaded_files_now = st.file_uploader(
        "📂 **拖入或添加图片**", 
        type=['jpg', 'png', 'jpeg'], 
        accept_multiple_files=True,
        key="uploader"
    )
    
    if uploaded_files_now:
        existing_names = {f['name'] for f in st.session_state.files}
        has_new_files = False
        for f in uploaded_files_now:
            if f.name not in existing_names:
                st.session_state.files.append({"name": f.name, "bytes": f.getvalue()})
                has_new_files = True
        
        # 只有在【第一次】上传时才刷新，后续追加不刷新
        if has_new_files and len(st.session_state.files) == len(uploaded_files_now):
            st.rerun()

    if not st.session_state.files:
        render_hero_section()
    else:
        render_workspace()

if __name__ == "__main__":
    main()
