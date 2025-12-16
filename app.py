import streamlit as st
from PIL import Image
import io
import os
import gc
import time
from openai import OpenAI
import streamlit.components.v1 as components # ✨ 引入前端组件核心

# ==========================================
# 👇 0. 核心配置 👇
# ==========================================
st.set_page_config(
    page_title="Miss Pink Elf's Studio v17.0 (Drag&Drop)", 
    layout="wide", 
    page_icon="🌸",
    initial_sidebar_state="expanded"
)

# ==========================================
# 👇 1. 核心样式与特效 👇
# ==========================================
def load_elysia_style():
    # 完整的 CSS 样式 (包含拖拽时的特殊样式)
    st.markdown("""
    <style>
    /* ... (之前的粉色CSS省略) ... */
    .stApp { background: linear-gradient(135deg, #FFF0F5 0%, #E6E6FA 100%); }
    h1, h2, h3 { background: linear-gradient(45deg, #FF69B4, #87CEFA); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    
    /* 拖拽容器 */
    .dnd-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr); /* 每行4个 */
        gap: 16px;
    }
    /* 可拖拽项 */
    .dnd-item {
        position: relative;
        background: rgba(255,255,255,0.7);
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: transform 0.2s;
        cursor: grab;
    }
    .dnd-item:active { cursor: grabbing; }
    /* 拖拽时的占位符样式 */
    .sortable-ghost {
        background: #FFC0CB; /* 粉色占位 */
        opacity: 0.5;
        border-radius: 15px;
    }
    
    /* 删除按钮 */
    .delete-btn {
        position: absolute; top: 15px; right: 15px;
        background: white; border: none; border-radius: 50%;
        width: 28px; height: 28px; color: #FF69B4;
        font-size: 14px; font-weight: bold; cursor: pointer;
        transition: all 0.2s; z-index: 10;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .delete-btn:hover { background: #FF69B4; color: white; transform: scale(1.1); }
    </style>
    """, unsafe_allow_html=True)

load_elysia_style()

# ==========================================
# 👇 2. 工具函数库 👇
# ==========================================
# ... (get_font, load_preview_image, generate_sora_prompt_with_ai 函数保持不变) ...
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
# 👇 5. 主工作台 (全新拖拽组件逻辑) 👇
# ==========================================
st.title("Miss Pink Elf's Studio v17.0")

# --- 文件上传 (防重复逻辑) ---
newly_uploaded_files = st.file_uploader("📂 **拖入图片**", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True, key="uploader")
if newly_uploaded_files:
    existing_filenames = {f['name'] for f in st.session_state.files}
    for file in newly_uploaded_files:
        if file.name not in existing_filenames:
            st.session_state.files.append({"name": file.name, "bytes": file.getvalue()})
    st.rerun() # 上传后立即刷新

# --- 英雄区 / 工作区 ---
if not st.session_state.files:
    # ... (英雄区代码不变) ...
    st.info("👈 请上传图片")
else:
    st.caption("👇 按住图片拖动排序，点击右上角 ❌ 删除")

    # --- ✨ 全新拖拽组件 ✨ ---
    item_html_list = []
    for i, file_data in enumerate(st.session_state.files):
        # 为每张图生成缩略图的 base64 编码，用于在 HTML 中显示
        thumb_bytes = load_preview_image(file_data["bytes"])
        import base64
        b64_thumb = base64.b64encode(thumb_bytes).decode()
        
        # 构造每个拖拽项的 HTML
        item_html = f"""
        <div class="dnd-item" data-id="{i}">
            <img src="data:image/jpeg;base64,{b64_thumb}" style="width: 100%; border-radius: 10px;">
        </div>
        """
        item_html_list.append(item_html)

    # 构造完整的 HTML 容器和 JS 脚本
    # `components.html` 会返回 JS 通过 `Streamlit.setComponentValue` 发送回来的值
    new_order_str = components.html(
        f"""
        <div id="dnd-gallery" class="dnd-container">
            {''.join(item_html_list)}
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js"></script>
        <script>
        const el = document.getElementById('dnd-gallery');
        const sortable = new Sortable(el, {{
            animation: 150,
            ghostClass: 'sortable-ghost',
            onEnd: function (evt) {{
                const items = el.children;
                const newOrder = Array.from(items).map(item => item.getAttribute('data-id'));
                // 将新顺序 (字符串数组) 发送回 Python
                Streamlit.setComponentValue(newOrder.join(','));
            }}
        }});
        </script>
        """,
        height=len(st.session_state.files) * 80 + 50, # 动态调整高度
        key="dnd_component"
    )

    # --- 处理拖拽后的新顺序 ---
    if new_order_str:
        new_order_indices = [int(i) for i in new_order_str.split(',')]
        # 根据新顺序重新排列 Python 里的数据
        st.session_state.files = [st.session_state.files[i] for i in new_order_indices]
        st.rerun() # 刷新以显示新顺序（并让下面的表单也更新）

    # --- 工作台表单 (负责编辑和删除) ---
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
        with col_btn1: submit_btn = st.form_submit_button("✨ 施展魔法 ✨", use_container_width=True)
        with col_btn2: delete_submit_btn = st.form_submit_button("🗑️ 执行删除", use_container_width=True)

    # --- 处理按钮逻辑 ---
    if delete_submit_btn:
        indices_to_delete = sorted([i for i, checked in delete_flags.items() if checked], reverse=True)
        if indices_to_delete:
            for i in indices_to_delete: del st.session_state.files[i]
            st.rerun()

    if submit_btn:
        # ... (生成逻辑不变)
        st.balloons()
        st.success("生成成功！")

    if st.session_state.last_result:
        # ... (结果展示不变)
        pass
