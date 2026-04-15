import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
import urllib.request
import io
import os

st.set_page_config(page_title="Pro Poster Maker", layout="centered")

st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #0e1117 !important; color: #ffffff !important; }
    h1, h2, h3 { color: #ffffff !important; text-align: center; }
    .stButton>button { background-color: #ff4b4b; color: white !important; border-radius: 8px; width: 100%; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1e1e1e; border-radius: 4px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("🎉 Ultimate Poster Maker")
st.markdown("<p style='text-align: center;'>10+ Templates, LUTs & Full Editing Control</p>", unsafe_allow_html=True)

# --- MEMORY SAVER ---
if 'cutout' not in st.session_state: st.session_state.cutout = None

# --- HELPERS (FONTS & FILTERS) ---
@st.cache_resource
def get_font(size):
    font_path = "Roboto-Black.ttf"
    if not os.path.exists(font_path):
        try: urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Black.ttf", font_path)
        except: pass
    try: return ImageFont.truetype(font_path, size)
    except: return ImageFont.load_default()

def apply_filter(img, filter_name):
    if img.mode != 'RGBA': img = img.convert('RGBA')
    if "00" in filter_name: return img
    r, g, b, a = img.split()
    rgb_img = Image.merge("RGB", (r, g, b))
    if "01" in filter_name: rgb_img = ImageEnhance.Contrast(rgb_img).enhance(1.2)
    elif "02" in filter_name: rgb_img = ImageEnhance.Color(rgb_img).enhance(1.4)
    elif "03" in filter_name: rgb_img = ImageEnhance.Color(rgb_img).enhance(1.5); rgb_img = ImageEnhance.Contrast(rgb_img).enhance(1.2)
    return Image.merge("RGBA", (rgb_img.split()[0], rgb_img.split()[1], rgb_img.split()[2], a))

lut_list = ["00. No Filter", "01. Basic Crisp", "02. Color Boost", "03. Cinematic Pop"]

# --- TEMPLATE GENERATOR (With 10 Style Variations) ---
def get_template(festival_name, style_num, custom_bg):
    W, H = 1080, 1920
    
    # Agar user ne apna background dala hai
    if custom_bg:
        bg_img = Image.open(custom_bg).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
        return bg_img

    # Fake Colors for 10 Different Styles (Jab aap PC app banayenge tab yahan image file load hogi)
    base_colors = {
        "Ambedkar Jayanti": [(30, 58, 138), (29, 78, 216), (37, 99, 235), (59, 130, 246), (96, 165, 250), (23, 37, 84), (30, 64, 175), (55, 48, 163), (67, 56, 202), (79, 70, 229)],
        "Diwali": [(185, 28, 28), (220, 38, 38), (239, 68, 68), (248, 113, 113), (252, 165, 165), (127, 29, 29), (153, 27, 27), (194, 65, 12), (234, 88, 12), (249, 115, 22)],
        "Holi": [(147, 51, 234), (168, 85, 247), (192, 132, 252), (216, 180, 254), (233, 213, 255), (107, 33, 168), (126, 34, 206), (217, 70, 239), (232, 121, 249), (240, 171, 252)],
        "Happy Birthday": [(217, 119, 6), (245, 158, 11), (251, 191, 36), (252, 211, 77), (253, 230, 138), (180, 83, 9), (146, 64, 14), (13, 148, 136), (20, 184, 166), (45, 212, 191)]
    }
    
    color_rgb = base_colors[festival_name][style_num - 1]
    template = Image.new("RGBA", (W, H), color_rgb)
    return template

# --- MAIN UI ---
st.subheader("1️⃣ Event Setup")
col_e1, col_e2 = st.columns(2)
with col_e1: festival = st.selectbox("Tyohar:", ["Ambedkar Jayanti", "Diwali", "Holi", "Happy Birthday"])
with col_e2: style_num = st.selectbox("Design Template:", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

st.subheader("2️⃣ User Details")
user_name = st.text_input("Poster par Naam:", "Ravi Prajapat")
uploaded_file = st.file_uploader("Apni Photo Upload Karein:", type=['png', 'jpg', 'jpeg'])
custom_bg_file = st.file_uploader("Apna Custom Background (Optional):", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    # STEP 1: BACKGROUND REMOVAL (One time only)
    if st.button("✂️ Step 1: Process Photo (Cut Background)"):
        with st.spinner("AI Cutting kar raha hai (Wait 10 sec)..."):
            from rembg import remove
            img = Image.open(uploaded_file)
            st.session_state.cutout = remove(img)
            st.success("✅ Photo Ready! Ab niche tools se edit karein.")

    # STEP 2: PRO STUDIO EDITING
    if st.session_state.cutout:
        st.markdown("---")
        st.subheader("🎛️ Step 2: Pro Editor Dashboard")
        
        # Tabs for Clean UI
        tab1, tab2, tab3 = st.tabs(["📸 Photo Set Karein", "✨ Filters & Lights", "📝 Text & Colors"])
        
        with tab1:
            st.write("Photo Size aur Jagah")
            col1, col2 = st.columns(2)
            with col1: scale = st.slider("🔍 Size (%)", 10, 200, 100) / 100.0
            with col2: flip_sub = st.checkbox("↔️ Flip Photo")
            c3, c4 = st.columns(2)
            with c3: x_val = st.slider("↔️ Left / Right", -500, 500, 0)
            with c4: y_val = st.slider("↕️ Up / Down", -1000, 1000, 400)
            
        with tab2:
            st.write("Effects")
            selected_lut = st.selectbox("Apni Photo par Filter lagayein:", options=lut_list)
            bright_val = st.slider("☀️ Subject Brightness", 50, 150, 100)
            
        with tab3:
            st.write("Text Styling")
            txt_c1, txt_c2 = st.columns(2)
            with txt_c1: txt_color = st.color_picker("Text Color", "#FFD700")
            with txt_c2: txt_size = st.slider("Text Bada/Chota", 30, 200, 80)
            txt_y = st.slider("Text Upar/Niche Karein", 0, 1920, 1750)
            banner_show = st.checkbox("Niche Black Patti Lagayein", value=True)

        # --- LIVE RENDERING ---
        template = get_template(festival, style_num, custom_bg_file)
        W, H = template.size
        cutout = st.session_state.cutout
        
        # Apply Edits to Subject
        if flip_sub: cutout = ImageOps.mirror(cutout)
        if bright_val != 100: cutout = ImageEnhance.Brightness(cutout).enhance(bright_val / 100.0)
        cutout = apply_filter(cutout, selected_lut)
        
        # Resize & Paste Subject
        ratio = min(W * 0.8 / cutout.width, H * 0.8 / cutout.height)
        new_w, new_h = int(cutout.width * ratio * scale), int(cutout.height * ratio * scale)
        if new_w > 0 and new_h > 0:
            cutout_resized = cutout.resize((new_w, new_h), Image.Resampling.LANCZOS)
            paste_x = (W - new_w) // 2 + x_val
            paste_y = (H - new_h) // 2 + y_val
            template.paste(cutout_resized, (paste_x, paste_y), cutout_resized)
        
        # Draw Default Tyohar Text (Top)
        draw = ImageDraw.Draw(template)
        draw.text((100, 300), f"Happy {festival}\nStyle {style_num}", font=get_font(120), fill="white")
        
        # Draw User Text & Banner (Bottom)
        if banner_show: draw.rectangle([0, txt_y - 30, W, H], fill="#000000")
        draw.text((50, txt_y), user_name, font=get_font(txt_size), fill=txt_color) 
        
        # Show Preview
        st.image(template, use_container_width=True)
        
        # Download
        buf = io.BytesIO()
        template.save(buf, format='PNG')
        st.download_button("⬇️ Download Final Poster", data=buf.getvalue(), file_name=f"Poster_{festival}_{style_num}.png", mime="image/png")
