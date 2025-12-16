import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import gc
import time

# ==========================================
# 👇 0. 核心配置 👇
# ==========================================
st.set_page_config(
    page_title="Miss Pink Elf's Offline Studio", 
    layout="wide", 
    page_icon="🌸",
    initial_sidebar_state="expanded"
)

# ==========================================
# 👇 1. 核心样式 👇
# ==========================================
def load_elysia_style():
    # 完整的 CSS 样式
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #FFF0F5 0%, #E6E6FA 100%); font-family: 'Comic Sans MS', sans-serif; }
    h1, h2, h3, h4 { background: -webkit-linear-gradient(45deg, #FF69B4, #87CEFA); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important; }
    section[data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.75); backdrop-filter: blur(20px); }
    .card {
        background: rgba(255,255,255,0.7);
        border-radius: 18px;
        padding: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.05);
        border: 2px solid transparent;
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }
    .card:hover { border-color: #FFB6C1; }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 12px !important; border: 2px solid #FFE4E1 !important;
        background: rgba(255, 255, 255, 0.85) !important;
    }
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

# ==========================================
# 👇 3. 状态管理 & 数据 👇
# ==========================================
if "files" not in st.session_state: st.session_state.files = []
if 'last_result' not in st.session_state: st.session_state.last_result = None

SHOT_OPTIONS = ["CU (特写)", "MS (中景)", "LS (全景)", "ECU (极特写)", "OTS (过肩)", "FPV (第一人称)"]
RATIOS = {"16:9 (电影)": (1920, 1080), "9:16 (抖音)": (1080, 1920), "2.35:1 (宽屏)": (1920, 816), "1:1 (方图)": (1080, 1080)}
MAX_FILES = 6

# ==========================================
# 👇 4. 侧边栏 UI (极简化) 👇
# ==========================================
def render_sidebar():
    with st.sidebar:
        if os.path.exists("elysia_cover.jpg"):
            st.image("elysia_cover.jpg", use_container_width=True)
        st.markdown("### 🏹 魔法配置")
        st.session_state.selected_ratio_name = st.selectbox("画幅比例", list(RATIOS.keys()))
        st.session_state.border_width = st.slider("🖼️ 间距", 0, 50, 20)
        st.session_state.output_quality = st.select_slider("画质", ["1080P", "2K", "4K"], value="2K")
        st.session_state.scale_factor = {"1080P": 1.0, "2K": 1.5, "4K": 2.0}[st.session_state.output_quality]

        st.markdown("---")
        with st.expander("☕ 打赏作者", expanded=False):
            if os.path.exists("pay.jpg"):
                st.image("pay.jpg")

# ==========================================
# 👇 5. 主工作台 👇
# ==========================================
def render_hero_section():
    st.info(f"👈 请上传图片开始创作 (最多 {MAX_FILES} 张)")

def main():
    render_sidebar()
    st.title("Miss Pink Elf's Studio")

    # --- 上传逻辑 ---
    uploaded_files_now = st.file_uploader(f"📂 **拖入图片 (最多 {MAX_FILES} 张)**", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True, key="uploader")
    if uploaded_files_now:
        if len(st.session_state.files) >= MAX_FILES:
            st.warning(f"最多只能处理 {MAX_FILES} 张图片！")
        else:
            existing_names = {f['name'] for f in st.session_state.files}
            files_to_add = [f for f in newly_uploaded_files if f.name not in existing_names][:MAX_FILES - len(st.session_state.files)]
            for file in files_to_add:
                st.session_state.files.append({"name": file.name, "bytes": file.getvalue()})
            if files_to_add:
                st.rerun()

    # --- 英雄区 / 工作区 ---
    if not st.session_state.files:
        render_hero_section()
    else:
        st.caption("👇 在每个卡片中编辑信息，使用 ⬆️⬇️ 调整顺序，或点击 ❌ 删除")
        st.write("---")

        cols = st.columns(3)
        shots_data = []

        def move_item(index, direction):
            if direction == "up" and index > 0: st.session_state.files.insert(index - 1, st.session_state.files.pop(index))
            elif direction == "down" and index < len(st.session_state.files) - 1: st.session_state.files.insert(index + 1, st.session_state.files.pop(index))
        
        def delete_item(index):
            st.session_state.files.pop(index)

        for i, file_data in enumerate(st.session_state.files):
            with cols[i % 3]:
                with st.container():
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.image(load_preview_image(file_data["name"], file_data["bytes"]), use_container_width=True)
                    st.caption(f"镜头 {i+1}: {file_data['name'][:20]}")
                    
                    s_type = st.selectbox("视角", SHOT_OPTIONS, key=f"s_{i}")
                    dur = st.number_input("秒", value=2.0, step=0.5, key=f"d_{i}")
                    desc = st.text_input("描述", placeholder="动作...", key=f"t_{i}")
                    
                    c1, c2, c3 = st.columns([1,1,1])
                    with c1: st.button("⬆️", key=f"up_{i}", on_click=move_item, args=(i, "up"), use_container_width=True)
                    with c2: st.button("⬇️", key=f"down_{i}", on_click=move_item, args=(i, "down"), use_container_width=True)
                    with c3: st.button("❌", key=f"del_{i}", on_click=delete_item, args=(i,), use_container_width=True, type="primary")

                    st.markdown('</div>', unsafe_allow_html=True)
                    shots_data.append({"bytes": file_data["bytes"], "shot_code": s_type.split(" ")[0], "dur": dur})
        
        st.write("---")
        if st.button("✨ 生成专业分镜图 ✨", type="primary", use_container_width=True):
            with st.status("💎 正在合成水晶...", expanded=True) as status:
                
                # ✨ 核心尺寸与布局修改 ✨
                MAX_OUTPUT_WIDTH = 1280
                border_width = 20
                
                cols_count = 3
                rows_count = 2 if len(shots_data) > 3 else 1
                
                single_w = (MAX_OUTPUT_WIDTH - (border_width * (cols_count + 1))) // cols_count
                ratio_w, ratio_h = RATIOS[st.session_state.selected_ratio_name]
                single_h = int(single_w * (ratio_h / ratio_w))
                
                bar_height = int(single_h * 0.15)
                cell_h = single_h + bar_height
                
                total_w = MAX_OUTPUT_WIDTH
                total_h = (cell_h * rows_count) + (border_width * (rows_count + 1))
                
                canvas = Image.new('RGB', (total_w, total_h), "#000000")
                font = get_font(int(bar_height * 0.4))
                
                for idx, item in enumerate(shots_data):
                    if idx >= 6: break
                    
                    src = Image.open(io.BytesIO(item["bytes"]))
                    src = ImageOps.fit(src, (single_w, single_h), method=Image.Resampling.LANCZOS)
                    
                    cell = Image.new('RGB', (single_w, cell_h), "#000000")
                    cell.paste(src, (0, bar_height))
                    
                    info_text = f"KF{idx+1} [{item['shot_code']} | {item['dur']}s]"
                    cdraw = ImageDraw.Draw(cell)
                    cdraw.text((15, (bar_height - 30) / 2), info_text, fill="#FFFFFF", font=font)
                    
                    r, c = idx // cols_count, idx % cols_count
                    x = border_width + (c * (single_w + border_width))
                    y = border_width + (r * (cell_h + border_width))
                    canvas.paste(cell, (x, y))
                
                buf = io.BytesIO()
                canvas.save(buf, format="JPEG")
                st.session_state.last_result = {"image_bytes": buf.getvalue()}
                status.update(label="✨ 合成完毕！", state="complete")

    if st.session_state.last_result:
        st.success("✅ 最终分镜图已生成！")
        res = st.session_state.last_result
        st.image(res["image_bytes"], use_container_width=True)
        st.download_button("📥 下载分镜图", res["image_bytes"], "storyboard_final.jpg", "image/jpeg")

if __name__ == "__main__":
    main()
