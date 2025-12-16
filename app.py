import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import gc
import time
from openai import OpenAI
import streamlit.components.v1 as components
import base64

# ==========================================
# 👇 0. 核心配置 👇
# ==========================================
st.set_page_config(
    page_title="Miss Pink Elf's Studio v25.0 (Final UX)", 
    layout="wide", 
    page_icon="🌸",
    initial_sidebar_state="expanded"
)

# ==========================================
# 👇 1. 核心样式与特效 👇
# ==========================================
def load_elysia_style():
    # 完整的 CSS 样式 (包含拖拽卡片的样式)
    st.markdown("""
    <style>
    /* 全局 */
    .stApp { background: linear-gradient(135deg, #FFF0F5 0%, #E6E6FA 100%); font-family: 'Comic Sans MS', sans-serif; }
    h1, h2, h3, h4 { background: -webkit-linear-gradient(45deg, #FF69B4, #87CEFA); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important; }
    
    /* 侧边栏 */
    section[data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.75); backdrop-filter: blur(20px); }

    /* 拖拽容器 */
    .dnd-container { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
    
    /* 拖拽卡片 */
    .dnd-item {
        position: relative;
        background: rgba(255,255,255,0.7);
        border-radius: 18px;
        padding: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.05);
        border: 2px solid transparent;
        transition: all 0.3s ease;
        cursor: grab;
    }
    .dnd-item:hover { border-color: #FFB6C1; }
    .dnd-item:active { cursor: grabbing; }

    /* 拖拽占位符 */
    .sortable-ghost { background: #FFC0CB; opacity: 0.4; border-radius: 18px; }
    
    /* 删除按钮 */
    .delete-btn {
        position: absolute; top: 10px; right: 10px;
        background: white; border: none; border-radius: 50%;
        width: 30px; height: 30px; color: #FF69B4;
        font-size: 16px; font-weight: bold; cursor: pointer;
        transition: all 0.2s; z-index: 10;
        display: flex; align-items: center; justify-content: center;
    }
    .delete-btn:hover { background: #FF69B4; color: white; transform: scale(1.1); }

    /* 输入控件 */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 12px !important; border: 2px solid #FFE4E1 !important;
        background: rgba(255, 255, 255, 0.85) !important;
    }
    
    /* 提交按钮 */
    div.stButton > button {
        background: linear-gradient(90deg, #FF9A9E 0%, #FECFEF 100%);
        color: white !important;
        border-radius: 20px !important; border: none !important;
        box-shadow: 0 4px 12px rgba(255, 105, 180, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

load_elysia_style()

# ==========================================
# 👇 2. 工具函数库 👇
# ==========================================
@st.cache_data(show_spinner=False)
def get_base64_image(image_bytes):
    return base64.b64encode(image_bytes).decode()

@st.cache_resource
def get_font(size):
    # (字体函数不变)
    pass

@st.cache_data(show_spinner=False)
def load_preview_image(file_name, _bytes):
    image = Image.open(io.BytesIO(_bytes))
    if image.mode in ('RGBA', 'P'): image = image.convert('RGB')
    image.thumbnail((400, 400))
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    return buf.getvalue()

def generate_sora_prompt_with_ai(...):
    # (AI Prompt 生成逻辑不变)
    pass

# ==========================================
# 👇 3. 状态管理 & 数据 👇
# ==========================================
if "files" not in st.session_state: st.session_state.files = []
if "shots_data" not in st.session_state: st.session_state.shots_data = {}
if 'last_result' not in st.session_state: st.session_state.last_result = None

SHOT_OPTIONS = ["CU (特写)", "MS (中景)", "LS (全景)", "ECU (极特写)", "OTS (过肩)", "FPV (第一人称)"]
# (其他预设数据省略)
RATIOS = {"16:9 (电影)": (1920, 1080), "9:16 (抖音)": (1080, 1920)}

# ==========================================
# 👇 4. 侧边栏 UI 👇
# ==========================================
def render_sidebar():
    # (侧边栏代码不变)
    pass
render_sidebar()

# ==========================================
# 👇 5. 主工作台 👇
# ==========================================
st.title("Miss Pink Elf's Studio v25.0")

# --- 文件上传 ---
newly_uploaded_files = st.file_uploader("📂 **拖入或添加图片**", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True, key="uploader")
if newly_uploaded_files:
    existing_names = {f['name'] for f in st.session_state.files}
    for file in newly_uploaded_files:
        if file.name not in existing_names:
            st.session_state.files.append({"name": file.name, "bytes": file.getvalue()})
            st.session_state.shots_data[file.name] = {"shot_type": "CU (特写)", "duration": 2.0, "desc": ""}
    st.rerun()

# --- 英雄区 / 工作区 ---
if not st.session_state.files:
    # (英雄区代码不变)
    st.info("👈 请上传图片")
else:
    st.caption("👇 按住卡片拖动排序，点击卡片右上角 ❌ 可直接删除")

    # --- ✨ 核心修复：拖拽组件移出表单 ---
    item_html_list = []
    for i, file_data in enumerate(st.session_state.files):
        thumb_bytes = load_preview_image(file_data["name"], file_data["bytes"])
        b64_thumb = get_base64_image(thumb_bytes)
        item_html_list.append(f"""
        <div class="dnd-item" data-id="{file_data['name']}">
            <button class="delete-btn" data-id="{file_data['name']}">X</button>
            <img src="data:image/jpeg;base64,{b64_thumb}" style="width: 100%; border-radius: 10px;">
        </div>
        """)

    # 这个组件现在只负责排序和删除的“信号”
    drag_area_event = components.html(
        f"""
        <div id="dnd-gallery" class="dnd-container">
            {''.join(item_html_list)}
        </div>
        <script src="https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js"></script>
        <script>
        const el = document.getElementById('dnd-gallery');
        const sortable = new Sortable(el, {{
            animation: 150, ghostClass: 'sortable-ghost',
            onEnd: function (evt) {{
                const newOrder = Array.from(el.children).map(item => item.getAttribute('data-id'));
                Streamlit.setComponentValue({{type: 'drag', order: newOrder.join(',')}});
            }}
        }});
        el.addEventListener('click', function(e) {{
            if (e.target.classList.contains('delete-btn')) {{
                const itemId = e.target.getAttribute('data-id');
                // 发送删除信号
                Streamlit.setComponentValue({{type: 'delete', id: itemId}});
            }}
        }});
        </script>
        """,
        height= (len(st.session_state.files) // 4 + 1) * 250, # 动态计算高度
        key="dnd_component"
    )

    # --- 处理前端事件 ---
    if drag_area_event:
        if drag_area_event['type'] == 'drag':
            new_order_names = drag_area_event['order'].split(',')
            st.session_state.files = sorted(st.session_state.files, key=lambda x: new_order_names.index(x['name']))
            st.rerun()
        elif drag_area_event['type'] == 'delete':
            file_name_to_delete = drag_area_event['id']
            st.session_state.files = [f for f in st.session_state.files if f['name'] != file_name_to_delete]
            del st.session_state.shots_data[file_name_to_delete]
            st.rerun()

    # --- 工作台表单 (现在只负责编辑和提交) ---
    with st.form("storyboard_form"):
        st.write("---")
        st.write("#### 📝 故事编织台")
        cols = st.columns(4)
        for i, file_data in enumerate(st.session_state.files):
            with cols[i % 4]:
                file_name = file_data['name']
                shot_info = st.session_state.shots_data.get(file_name, {})
                st.caption(f"镜头 {i+1}")
                st.session_state.shots_data[file_name]['shot_type'] = st.selectbox("视角", SHOT_OPTIONS, index=SHOT_OPTIONS.index(shot_info.get('shot_type', "CU (特写)")), key=f"s_{file_name}")
                st.session_state.shots_data[file_name]['duration'] = st.number_input("秒", value=shot_info.get('duration', 2.0), step=0.5, key=f"d_{file_name}")
                st.session_state.shots_data[file_name]['desc'] = st.text_input("描述", value=shot_info.get('desc', ''), placeholder="动作...", key=f"t_{file_name}")

        st.markdown("---")
        submit_btn = st.form_submit_button("✨ 施展魔法 ✨", use_container_width=True)

    # --- 生成逻辑 ---
    if submit_btn:
        final_shots_data = []
        for file_data in st.session_state.files:
            shot_info = st.session_state.shots_data[file_data['name']]
            final_shots_data.append({
                "bytes": file_data["bytes"],
                "shot_code": shot_info['shot_type'].split(" ")[0],
                "dur": shot_info['duration'],
                "desc": shot_info['desc']
            })
        
        # ... (后续的图片生成和 AI 调用逻辑不变)
        st.balloons()
        st.success("生成成功！")
        st.session_state.last_result = {"image": "canvas_placeholder", "prompt": "prompt_placeholder"}

    if st.session_state.last_result:
        st.info("结果展示区")
