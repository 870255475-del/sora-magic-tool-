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
    page_title="Miss Pink Elf's Studio v29.0 (Ultimate)", 
    layout="wide", 
    page_icon="🌸",
    initial_sidebar_state="expanded"
)

# ==========================================
# 👇 1. 核心样式与特效 👇
# ==========================================
def load_elysia_style():
    st.markdown("""
    <style>
    /* 全局优化 */
    .stApp {
        background: linear-gradient(135deg, #FFF0F5 0%, #E6E6FA 100%);
        font-family: 'Comic Sans MS', 'Microsoft YaHei', sans-serif;
    }
    h1, h2, h3, h4 {
        background: -webkit-linear-gradient(45deg, #FF69B4, #87CEFA);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    /* 侧边栏 */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(20px);
    }
    </style>
    """, unsafe_allow_html=True)

load_elysia_style()

# ==========================================
# 👇 2. 工具函数库 👇
# ==========================================
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
    image.thumbnail((400, 400))
    return image

def generate_sora_prompt_with_ai(api_key, base_url, model_name, global_style, cam, phys, ratio, motion, neg_prompt, shots_data):
    if not api_key: return "API Key not provided."
    if not base_url: base_url = "https://api.openai.com/v1"
    client = OpenAI(api_key=api_key, base_url=base_url)
    tech_specs = f"Specs: Ratio {ratio}, Motion {motion}/10, {cam}, {phys}"
    system_prompt = f"You are an expert Sora 2 prompt engineer..."
    user_content = f"Global Style: {global_style}\nStoryboard:\n"
    # ... (AI prompt generation logic)
    return "Generated prompt based on inputs."

# ==========================================
# 👇 3. 状态管理 & 数据 👇
# ==========================================
if "files" not in st.session_state: st.session_state.files = []
if "shots_data" not in st.session_state: st.session_state.shots_data = {}
if 'last_result' not in st.session_state: st.session_state.last_result = None
if 'history' not in st.session_state: st.session_state.history = []
if 'edit_mode' not in st.session_state: st.session_state.edit_mode = False

# (Preset data)
SHOT_OPTIONS = ["CU (特写)", "MS (中景)", "LS (全景)", "ECU (极特写)", "OTS (过肩)", "FPV (第一人称)"]
MAX_FILES = 6
# ... (Other presets)

# ==========================================
# 👇 4. UI 渲染函数 (封装) 👇
# ==========================================
def render_sidebar():
    with st.sidebar:
        # ... (Sidebar code)
        pass

def render_hero_section():
    st.info(f"👈 请上传图片开始创作 (最多 {MAX_FILES} 张)")
    # ... (Hero section code)

def render_workspace():
    # --- 编辑模式切换 ---
    if st.session_state.edit_mode:
        if st.button("✅ 完成编辑", use_container_width=True, type="primary"):
            st.session_state.edit_mode = False
            st.rerun()
    else:
        if st.button("✏️ 编辑顺序 / 删除", use_container_width=True):
            st.session_state.edit_mode = True
            st.rerun()

    # --- 编辑模式 UI ---
    if st.session_state.edit_mode:
        st.write("---")
        st.subheader("🛠️ 编辑模式")
        st.caption("在这里调整顺序或删除图片。完成后点击上方的“完成编辑”按钮。")

        # 排序
        order_cols = st.columns(len(st.session_state.files))
        new_order = [0] * len(st.session_state.files)
        for i, col in enumerate(order_cols):
            with col:
                new_order[i] = st.number_input(f"位置 {i+1}", min_value=1, max_value=len(st.session_state.files), value=i+1, key=f"order_{i}")
        
        if st.button("🔄 应用排序"):
            try:
                # 检查输入是否有效
                if len(set(new_order)) != len(st.session_state.files):
                    st.error("排序数字不能重复！")
                else:
                    new_indices = [x - 1 for x in new_order]
                    st.session_state.files = [st.session_state.files[i] for i in new_indices]
                    st.success("顺序已更新！")
                    time.sleep(1)
                    st.rerun()
            except:
                st.error("排序输入无效。")

        # 删除
        cols = st.columns(4)
        for i, file_data in enumerate(st.session_state.files):
            with cols[i % 4]:
                st.image(load_preview_image(file_data["name"], file_data["bytes"]), use_container_width=True)
                if st.button("🗑️ 删除", key=f"del_{i}", use_container_width=True):
                    del st.session_state.files[i]
                    st.rerun()
    
    # --- 默认显示与编辑表单 ---
    else:
        st.write("---")
        with st.form("storyboard_form"):
            st.write("#### 📝 故事编织台")
            cols = st.columns(3)
            shots_data = []
            for i, file_data in enumerate(st.session_state.files):
                with cols[i % 3]:
                    st.image(load_preview_image(file_data["name"], file_data["bytes"]), use_container_width=True)
                    file_name = file_data['name']
                    shot_info = st.session_state.shots_data.get(file_name, {})
                    st.caption(f"镜头 {i+1}")
                    
                    st.session_state.shots_data[file_name]['shot_type'] = st.selectbox("视角", SHOT_OPTIONS, index=SHOT_OPTIONS.index(shot_info.get('shot_type', "CU (特写)")), key=f"s_{file_name}")
                    st.session_state.shots_data[file_name]['duration'] = st.number_input("秒", value=shot_info.get('duration', 2.0), step=0.5, key=f"d_{file_name}")
                    st.session_state.shots_data[file_name]['desc'] = st.text_input("描述", value=shot_info.get('desc', ''), placeholder="动作...", key=f"t_{file_name}")
                    
                    shots_data.append({"bytes": file_data["bytes"], "shot_code": st.session_state.shots_data[file_name]['shot_type'].split(" ")[0], "dur": st.session_state.shots_data[file_name]['duration'], "desc": st.session_state.shots_data[file_name]['desc']})

            st.markdown("---")
            submit_btn = st.form_submit_button("✨ 施展魔法 ✨", use_container_width=True)

        if submit_btn:
            with st.status("💎 魔法咏唱中...", expanded=True) as status:
                status.write("🖼️ 正在构建专业分镜...")
                # ... (Image generation logic remains the same, but read from shots_data)
                canvas = Image.new('RGB', (1280, 720), "#000000") # Placeholder
                
                prompt_res = ""
                if 'api_key' in st.session_state and st.session_state.api_key:
                    status.write("🧠 AI 正在撰写剧本...")
                    # ... (AI call logic remains the same)
                    prompt_res = "AI generated prompt."

                status.update(label="✨ 魔法完成！", state="complete")
                
                # 🐞 核心修复：存储二进制数据
                buf = io.BytesIO()
                canvas.save(buf, format="JPEG")
                st.session_state.last_result = {"image_bytes": buf.getvalue(), "prompt": prompt_res}
                st.session_state.history.append(st.session_state.last_result)
                gc.collect()

def render_results():
    if st.session_state.last_result:
        st.success("✅ 生成成功！")
        res = st.session_state.last_result
        tab1, tab2, tab3 = st.tabs(["🖼️ 专业分镜图", "📜 Sora 2 咒语", "🕰️ 历史记录"])
        with tab1:
            st.image(res["image_bytes"], use_container_width=True)
            st.download_button("📥 下载分镜图", res["image_bytes"], "sora_pro.jpg", "image/jpeg")
        with tab2:
            if res["prompt"]:
                st.code(res["prompt"])
                st.download_button("📄 下载提示词 (.txt)", res["prompt"], "prompt.txt")
        with tab3:
            st.caption("历史记录")
            # ... (History display logic remains the same)

# ==========================================
# 👇 5. 主程序入口 👇
# ==========================================
def main():
    render_sidebar()
    st.title("Miss Pink Elf's Studio v29.0")

    uploaded_files_now = st.file_uploader(f"📂 **拖入图片 (最多 {MAX_FILES} 张)**", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True, key="uploader")
    if uploaded_files_now:
        existing_names = {f['name'] for f in st.session_state.files}
        has_new_files = False
        for f in uploaded_files_now:
            if len(st.session_state.files) < MAX_FILES and f.name not in existing_names:
                st.session_state.files.append({"name": f.name, "bytes": f.getvalue()})
                st.session_state.shots_data[f.name] = {"shot_type": "CU (特写)", "duration": 2.0, "desc": ""}
                has_new_files = True
        if has_new_files:
            st.rerun()

    if not st.session_state.files:
        render_hero_section()
    else:
        render_workspace()
    
    render_results()

if __name__ == "__main__":
    main()
