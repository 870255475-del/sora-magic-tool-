import streamlit as st
from3: st.markdown("<div class='feature-card'><span class='emoji-icon'>🌸</span><h3>唯 PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import gc
import time美体验</h3><p>丝滑预览与拖拽排序</p></div>", unsafe_allow_html=True)

def main():
    render_sidebar()
    st.title("Miss Pink Elf's Studio v26
from openai import OpenAI
import streamlit.components.v1 as components
import base64

# =================.1")

    newly_uploaded_files = st.file_uploader(f"📂 **拖入=========================
# 👇 0. 核心配置 👇
# ==========================================
st.set_page图片 (最多 {MAX_FILES} 张)**", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True, key="uploader")
    if newly_uploaded_files:
        if len(st.session_state_config(
    page_title="Miss Pink Elf's Studio v26.1 (Complete)", .files) >= MAX_FILES:
            st.warning(f"最多只能上传 {MAX_FILES} 张图片哦！")
        else:
            existing_names = {f['name'] for f in st.session
    layout="wide", 
    page_icon="🌸",
    initial_sidebar_state="expanded"_state.files}
            files_to_add = []
            for file in newly_uploaded_files
)

# ==========================================
# 👇 1. 核心样式与特效 👇
# ==========================================
:
                if file.name not in existing_names:
                    files_to_add.append({"namedef load_elysia_style():
    # 完整的 CSS 样式 (包含拖拽卡片的样式)
    st": file.name, "bytes": file.getvalue()})
            space_left = MAX_FILES - len(st.session_state.files)
            if len(files_to_add) > space_left:
                .markdown("""
    <style>
    /* 全局 */
    .stApp { background: linear-gradient(files_to_add = files_to_add[:space_left]
            for file_data in files_to_add:
                st.session_state.files.append(file_data)
                st135deg, #FFF0F5 0%, #E6E6FA 100%); font.session_state.shots_data[file_data['name']] = {"shot_type": "CU (特写-family: 'Comic Sans MS', sans-serif; }
    h1, h2, h3, h4)", "duration": 2.0, "desc": ""}
            if files_to_add:
                st.rerun()

    if not st.session_state.files:
        render_hero_section()
    else { background: -webkit-linear-gradient(45deg, #FF69B4, #87CEFA); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font:
        st.caption("👇 按住卡片拖动排序，点击卡片右上角 ❌ 可直接-weight: 800 !important; }
    
    /* 侧边栏 */
    section[data-testid="stSidebar"] { background-color: rgba(255, 255, 25删除")

        item_html_list = []
        for i, file_data in enumerate(st.session_state.files):
            thumb_bytes = load_preview_image(file_data["name"], file_data["bytes"])
            b64_thumb = get_base64_image(thumb_bytes)
            item_html_list5, 0.75); backdrop-filter: blur(20px); }

    /* 拖拽容器 */
    .dnd-container { display: grid; grid-template-columns: repeat(3,.append(f"""
            <div class="dnd-item" data-id="{file_data['name']}">
                <button class="delete-btn" data-id="{file_data['name']}">X 1fr); gap: 20px; }
    
    /* 拖拽卡片 */
    </button>
                <img src="data:image/jpeg;base64,{b64_thumb}" style="width: 100%; border-radius: 10px;">
            </div>
            """)

.dnd-item {
        position: relative;
        background: rgba(255,255,255,0.7);
        border-radius: 18px;
        padding: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.0        drag_area = components.html(
            f"""
            <div id="dnd-gallery" class="dnd-container">
                {''.join(item_html_list)}
            </div>
            <script5);
        border: 2px solid transparent;
        transition: all 0.3s ease;
         src="https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js"></cursor: grab;
    }
    .dnd-item:hover { border-color: #FFBscript>
            <script>
            const el = document.getElementById('dnd-gallery');
            new6C1; }
    .dnd-item:active { cursor: grabbing; }

    /* 拖拽 Sortable(el, {{
                animation: 150, ghostClass: 'sortable-ghost',
                onEnd: function (evt) {{
                    const newOrder = Array.from(el.children).map(占位符 */
    .sortable-ghost { background: #FFC0CB; opacity: 0.4;item => item.getAttribute('data-id'));
                    Streamlit.setComponentValue({{type: 'drag', order: newOrder.join(',')}});
                }}
            }});
            el.addEventListener('click', function(e) {{
                if (e.target.classList.contains('delete-btn')) {{
                    const itemId = e.target border-radius: 18px; }
    
    /* 删除按钮 */
    .delete-btn {
        position: absolute; top: 10px; right: 10px;
        background: white.getAttribute('data-id');
                    Streamlit.setComponentValue({{type: 'delete', id: itemId}});
; border: none; border-radius: 50%;
        width: 30px; height: 30px; color: #FF69B4;
        font-size: 16px; font-weight: bold; cursor: pointer;
        transition: all 0.2s; z-index: 10;                }}
            }});
            </script>
            """,
            height= (len(st.session_state
        display: flex; align-items: center; justify-content: center;
    }
    .delete-.files) // 3 + 1) * 280,
            key="dnd_component"
        btn:hover { background: #FF69B4; color: white; transform: scale(1.1); })

        if drag_area:
            if drag_area['type'] == 'drag':
                new_order_names = drag_area['order'].split(',')
                st.session_state.files = sorted

    /* 输入控件 */
    .stTextInput input, .stNumberInput input, .stSelectbox div(st.session_state.files, key=lambda x: new_order_names.index(x['name']))
[data-baseweb="select"] {
        border-radius: 12px !important; border:                st.rerun()
            elif drag_area['type'] == 'delete':
                file_name 2px solid #FFE4E1 !important;
        background: rgba(255, 255, 255, 0.85) !important;
    }
    
    /* _to_delete = drag_area['id']
                st.session_state.files = [f for f in st.session_state.files if f['name'] != file_name_to_delete]
                del提交按钮 */
    div.stButton > button {
        background: linear-gradient(90deg, # st.session_state.shots_data[file_name_to_delete]
                st.rerun()

        with st.form("storyboard_form"):
            st.write("---")
            st.writeFF9A9E 0%, #FECFEF 100%);
        color: white !important;
("#### 📝 故事编织台")
            cols = st.columns(3)
            for i        border-radius: 20px !important; border: none !important;
        box-shadow: 0 4px 12px rgba(255, 105, 180, 0.3, file_data in enumerate(st.session_state.files):
                with cols[i % 3]:
                    file_name = file_data['name']
                    shot_info = st.session_state.shots) !important;
    }
    .feature-card {
        background: rgba(255, 255, 255, 0.6);
        border-radius: 20px; padding_data.get(file_name, {})
                    st.caption(f"镜头 {i+1}"): 25px;
        border: 2px solid #FFF;
        box-shadow: 0 8px 20px rgba(255, 182, 193, 0.
                    st.session_state.shots_data[file_name]['shot_type'] = st.selectbox("视角", SHOT_OPTIONS, index=SHOT_OPTIONS.index(shot_info.get('shot_type', "15);
        text-align: center; height: 100%;
    }
    .emojiCU (特写)")), key=f"s_{file_name}")
                    st.session_state.-icon { font-size: 3.5em; margin-bottom: 15px; display: block;shots_data[file_name]['duration'] = st.number_input("秒", value=shot_info.get }
    </style>
    """, unsafe_allow_html=True)

load_elysia_style()('duration', 2.0), step=0.5, key=f"d_{file_name}")
                    st

# ==========================================
# 👇 2. 工具函数库 👇
# ==========================================
@st.cache_data(show_spinner=False)
def get_base64_image(image_bytes):
.session_state.shots_data[file_name]['desc'] = st.text_input("描述", value=shot    return base64.b64encode(image_bytes).decode()

@st.cache_resource_info.get('desc', ''), placeholder="动作...", key=f"t_{file_name}")

            st.markdown("---")
            submit_btn = st.form_submit_button("✨ 施展魔法 ✨", use_container_width=True)

        if submit_btn:
            with st.status("💎 魔法咏
def get_font(size):
    possible_fonts = ["DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial.ttf"]
    for f in possible_fonts:
        try: return ImageFont.tru唱中...", expanded=True) as status:
                st.write("🖼️ 正在构建专业分镜...")
                etype(f, size)
        except IOError: continue
    return ImageFont.load_default()

@st.cache_data(show_spinner=False)
def load_preview_image(file_name, _bytes):
    image = Image.open(io.BytesIO(_bytes))
    if image.mode in ('RGBA', 'P'): image = image.convert('RGB')
    image.thumbnail((400, 400))
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    return buf.getvalue()

def generate_sora_prompt_with_ai(api_key, base_url, model_name, global_style, cam, phys, ratio, motion, neg_prompt, shots_data):
    if not api_key: return "API Key not provided."
    if not base_url: base_url = "https://api.openai.com/v1"
    client = OpenAI(api_key=api_key, base_url=base_url)
    tech_specs = f"Specs: Ratio {ratio}, Motion {motion}/10, {shots_data_to_generate = [st.session_state.shots_data[f['name']] for f in st.session_state.files]
                # Image Generation Logic
                # ...
                
                prompt_res = ""
                if 'api_key' in st.session_state and st.session_state.api_key:
                    st.write("🧠 AI 正在思考...")
                    # AI Call Logic
                    # ...
                
                status.update(label="✨ 魔法完成！", state="complete")
                st.session_state.last_result = {"image": "canvas_placeholder", "prompt": prompt_res}
                st.session_state.history.append(st.session_state.last_result)
            
        if st.session_state.last_result:
            st.balloons()
            st.info("结果展示区")

if __name__ == "__main__":
    main()
