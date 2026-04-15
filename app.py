import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import urllib.request
import io
import os

st.set_page_config(page_title="Ravi Poster Maker", layout="centered")

st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #0e1117 !important; color: #ffffff !important; }
    h1, h2, h3 { color: #ffffff !important; text-align: center; }
    .stButton>button { background-color: #ff4b4b; color: white !important; border-radius: 8px; width: 100%; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🎉 Pro Festival Poster Maker")
st.markdown("<p style='text-align: center;'>Live Editable Templates</p>", unsafe_allow_html=True)

# --- FONT & TEMPLATE SETUP ---
@st.cache_resource
def get_font(size):
    font_path = "Roboto-Black.ttf"
    if not os.path.exists(font_path):
        try:
            urllib.request.urlretrieve("https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Black.ttf", font_path)
        except: pass
    try: return ImageFont.truetype(font_path, size)
    except: return ImageFont.load_default()

def get_template(festival_name):
    W, H = 1080, 1920
    if festival_name == "Ambedkar Jayanti": bg_color, main_text = "#1E3A8A", "Happy Ambedkar\nJayanti"
    elif festival_name == "Diwali": bg_color, main_text = "#B91C1C", "Happy Diwali\nMay the light shine!"
    elif festival_name == "Holi": bg_color, main_text = "#9333EA", "Happy Holi\nColors of Joy!"
    else: bg_color, main_text = "#D97706", "Happy Birthday\nStay Blessed!"
        
    template = Image.new("RGBA", (W, H), bg_color)
    draw = ImageDraw.Draw(template)
    draw.text((100, 300), main_text, font=get_font(120), fill="white")
    return template

# --- MEMORY (RAM) SAVER LOGIC ---
if 'cutout' not in st.session_state:
    st.session_state.cutout = None

# --- UI START ---
festival = st.selectbox("1️⃣ Tyohar Select Karein:", ["Ambedkar Jayanti", "Diwali", "Holi", "Happy Birthday"])
user_name = st.text_input("2️⃣ Apna Naam Likhein:", "Ravi Prajapat")
uploaded_file = st.file_uploader("3️⃣ Apni Photo Daalein:", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    # STEP 1: Background Hatao Button
    if st.button("✂️ Step 1: Background Hatao"):
        with st.spinner("AI Cutting kar raha hai..."):
            from rembg import remove
            img = Image.open(uploaded_file)
            st.session_state.cutout = remove(img)
            st.success("Background hat gaya! Ab niche adjust karein.")

    # STEP 2: Live Editing (Sirf tab dikhega jab photo cut ho jayegi)
    if st.session_state.cutout:
        st.markdown("---")
        st.subheader("🎛️ Step 2: Photo ko Adjust Karein")
        
        # Sliders for User Control
        col1, col2 = st.columns(2)
        with col1: scale = st.slider("🔍 Photo Size", 10, 200, 100) / 100.0
        with col2: x_val = st.slider("↔️ Left / Right", -500, 500, 0)
        y_val = st.slider("↕️ Up / Down", -1000, 1000, 400) # Default 400 (Niche ki taraf)
        
        # Live Preview Processing
        template = get_template(festival)
        W, H = template.size
        cutout = st.session_state.cutout
        
        # Resize Subject
        ratio = min(W * 0.8 / cutout.width, H * 0.8 / cutout.height)
        new_w, new_h = int(cutout.width * ratio * scale), int(cutout.height * ratio * scale)
        if new_w > 0 and new_h > 0:
            cutout_resized = cutout.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Position Subject
            paste_x = (W - new_w) // 2 + x_val
            paste_y = (H - new_h) // 2 + y_val
            template.paste(cutout_resized, (paste_x, paste_y), cutout_resized)
        
        # Draw Name Banner on Top
        draw = ImageDraw.Draw(template)
        draw.rectangle([0, H - 150, W, H], fill="#000000")
        draw.text((50, H - 120), user_name, font=get_font(80), fill="#FFD700") 
        
        # Show Result
        st.image(template, use_container_width=True)
        
        # Download Button
        buf = io.BytesIO()
        template.save(buf, format='PNG')
        st.download_button(label="⬇️ Final Poster Download Karein", data=buf.getvalue(), file_name=f"Poster_{user_name}.png", mime="image/png")
