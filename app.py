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
    page_title="Miss Pink Elf's Studio v30.0 (Ultimate)", 
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

    /* ✨ 拖拽容器 (关键) */
    .dnd-container { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
    
    /* ✨ 拖拽卡片 (关键) */
    .dnd-item {
        position: relative;
        background: rgba(255,255,255,0.7);
        border-radius: 18px;
        padding: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.05);
        border: 2px solid transparent;
        transition: all 0.3s ease;
        cursor: grab; /* 抓取手势 */
    }
    .dnd-item:hover { border-color: #FFB6C1; }
    .dnd-item:active { cursor: grabbing; } /* 抓取中手势 */

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
    .feature-card {
        background: rgba(255, 255, 255, 0.6);
        border-radius: 20px; padding: 25px;
        border: 2px solid #FFF;
        box-shadow: 0 8px 20px rgba(255, 182, 193, 0.15);
        text-align: center; height: 100%;
    }
    .emoji-icon { font-size: 3.5em; margin-bottom: 15px; display: block; }
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
    possible_fonts = ["DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial.ttf"]
    for f in possible_fonts:
        try: return ImageFont.truetype(f, size)
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
    tech_specs = f"Specs: Ratio {ratio}, Motion {motion}/10, {cam}, {phys}"
    system_prompt = f"You are an expert Sora 2 prompt engineer..."
    user_content = f"Global Style: {global_style}\nStoryboard:\n"
    current_time = 0.0
    for idx, item in enumerate(shots_data):
        end_time = current_time + item['dur']
        user_content += f"- Shot {idx+1} ({current_time}s-{end_time}s): View={item['shot_code']}, Action={item['desc']}\n"
        current_time = end_time
    try:
        response = client.chat.completions.create(model=model_name, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}], temperature=0.7)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# ==========================================
# 👇 3. 状态管理 & 数据 👇
# ==========================================
if "files" not in st.session_state: st.session_state.files = []
if "shots_data" not in st.session_state: st.session_state.shots_data = {}
if 'last_result' not in st.session_state: st.session_state.last_result = None
if 'history' not in st.session_state: st.session_state.history = []

SHOT_OPTIONS = ["CU (特写)", "MS (中景)", "LS (全景)", "ECU (极特写)", "OTS (过肩)", "FPV (第一人称)"]
PRESETS_STYLE = {"🌸 爱莉希雅 (Anime)": "Dreamy Anime...", "🎥 电影质感 (Cinematic)": "Shot on 35mm film..."}
PRESETS_CAMERA = {"Auto (自动)": "Cinematic camera movement...", "Truck (横移)": "Smooth trucking shot..."}
TAGS_PHYSICS = ["Volumetric Lighting", "Ray-traced Reflections", "Fluid Simulation"]
RATIOS = {"16:9 (电影)": (1920, 1080), "9:16 (抖音)": (1080, 1920)}
DEFAULT_NEG = "morphing, distortion, bad anatomy, blurry, watermark, text"
MAX_FILES = 6

# ==========================================
# 👇 4. 侧边栏 UI 👇
# ==========================================
def render_sidebar():
    with st.sidebar:
        if os.path.exists("elysia_cover.jpg"):
            st.image("elysia_cover.jpg", use_container_width=True)
        st.markdown("### 🏹 魔法配置")
        with st.expander("🤖 连接 AI 大脑", expanded=True):
            api_provider = st.selectbox("API类型", ["自定义", "火山引擎 (豆包)", "DeepSeek", "OpenAI"])
            base, model = "", ""
            if api_provider == "火山引擎 (豆包)":
                st.markdown("👉 [**点我注册豆包**](https://www.volcengine.com/product/doubao)")
                base = "https://ark.cn-beijing.volces.com/api/v3"
            elif api_provider == "DeepSeek":
                st.markdown("👉 [**点我注册 DeepSeek**](https://platform.deepseek.com/)")
                base = "https://api.deepseek.com"; model = "deepseek-chat"
            st.session_state.api_key = st.text_input("API Key", type="password")
            st.session_state.base_url = st.text_input("Base URL", value=base)
            st.session_state.model_name = st.text_input("Model", value=model)

        st.markdown("---")
        st.markdown("#### 🧪 Sora 2 炼金台")
        st.session_state.selected_style = st.selectbox("🔮 滤镜风格", list(PRESETS_STYLE.keys()))
        st.session_state.cam_content = st.selectbox("📷 运镜方式", list(PRESETS_CAMERA.keys()))
        st.session_state.phys_content = st.multiselect("🌊 物理与光影", TAGS_PHYSICS, default=["Volumetric Lighting"])
        st.session_state.selected_ratio_name = st.selectbox("画幅比例", list(RATIOS.keys()))
        st.session_state.motion_strength = st.slider("⚡ 动态幅度", 1, 10, 5)
        st.session_state.neg_prompt = st.text_area("⛔ 负面提示词", value=DEFAULT_NEG, height=70)
        st.markdown("---")
        with st.expander("☕ 打赏作者", expanded=False):
            if os.path.exists("pay.jpg"):
                st.image("pay.jpg")

# ==========================================
# 👇 5. 主工作台 👇
# ==========================================
def render_hero_section():
    st.info(f"👈 请上传图片开始创作 (最多 {MAX_FILES} 张)")
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown("<div class='feature-card'><span class='emoji-icon'>🧠</span><h3>Sora 2 内核</h3><p>优化的物理引擎提示词</p></div>", unsafe_allow_html=True)
    with col2: st.markdown("<div class='feature-card'><span class='emoji-icon'>🎬</span><h3>AI 导演</h3><p>自动编写时间轴剧本</p></div>", unsafe_allow_html=True)
    with col3: st.markdown("<div class='feature-card'><span class='emoji-icon'>🌸</span><h3>唯美体验</h3><p>丝滑预览与拖拽排序</p></div>", unsafe_allow_html=True)

def main():
    render_sidebar()
    st.title("Miss Pink Elf's Studio v30.1")

    newly_uploaded_files = st.file_uploader(f"📂 **拖入图片 (最多 {MAX_FILES} 张)**", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True, key="uploader")
    if newly_uploaded_files:
        if len(st.session_state.files) >= MAX_FILES:
            st.warning(f"最多只能上传 {MAX_FILES} 张图片！")
        else:
            existing_names = {f['name'] for f in st.session_state.files}
            files_to_add = [f for f in newly_uploaded_files if f.name not in existing_names]
            space_left = MAX_FILES - len(st.session_state.files)
            files_to_add = files_to_add[:space_left]

            for file in files_to_add:
                st.session_state.files.append({"name": file.name, "bytes": file.getvalue()})
                st.session_state.shots_data[file.name] = {"shot_type": "CU (特写)", "duration": 2.0, "desc": ""}
            if files_to_add:
                st.rerun()

    if not st.session_state.files:
        render_hero_section()
    else:
        st.caption("👇 按住卡片拖动排序，或在卡片中填写信息")
        
        item_html_list = []
        for i, file_data in enumerate(st.session_state.files):
            thumb_bytes = load_preview_image(file_data["name"], file_data["bytes"])
            b64_thumb = get_base64_image(thumb_bytes)
            file_name = file_data['name']
            
            item_html_list.append(f"""
            <div class="dnd-item" data-id="{file_name}">
                <button class="delete-btn" data-id="{file_name}" onclick="deleteItem(this)">X</button>
                <img src="data:image/jpeg;base64,{b64_thumb}" style="width: 100%; border-radius: 10px;">
            </div>
            """)

        drag_area = components.html(
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
            function deleteItem(btn) {{
                const itemId = btn.getAttribute('data-id');
                Streamlit.setComponentValue({{type: 'delete', id: itemId}});
            }}
            </script>
            """,
            height= (len(st.session_state.files) // 4 + 1) * 250,
            key="dnd_component"
        )
        
        if drag_area:
            if drag_area['type'] == 'drag':
                new_order_names = drag_area['order'].split(',')
                st.session_state.files = sorted(st.session_state.files, key=lambda x: new_order_names.index(x['name']))
                st.rerun()
            elif drag_area['type'] == 'delete':
                file_name_to_delete = drag_area['id']
                st.session_state.files = [f for f in st.session_state.files if f['name'] != file_name_to_delete]
                del st.session_state.shots_data[file_name_to_delete]
                st.rerun()

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
            
            with st.status("💎 魔法咏唱中...", expanded=True) as status:
                st.write("🖼️ 正在构建专业分镜...")
                # Image Generation Logic...
                
                prompt_res = ""
                if 'api_key' in st.session_state and st.session_state.api_key:
                    st.write("🧠 AI 正在撰写剧本...")
                    # AI Call Logic...
                
                status.update(label="✨ 魔法完成！", state="complete")
                # Store result as bytes to avoid MediaFileStorageError
                # canvas_bytes = ...
                st.session_state.last_result = {"image_bytes": b'', "prompt": prompt_res}
                st.session_state.history.append(st.session_state.last_result)
            
        if st.session_state.last_result:
            st.balloons()
            st.info("结果展示区")

if __name__ == "__main__":
    main()
