import streamlit as st
from rembg import remove
from PIL import Image, ImageDraw, ImageFont
import urllib.request
import io
import os

st.set_page_config(page_title="Ravi Poster Maker", layout="centered")

st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #0e1117 !important; color: #ffffff !important; }
    h1, h2, h3 { color: #ffffff !important; text-align: center; }
    .stButton>button { background-color: #25D366; color: white !important; border-radius: 8px; width: 100%; font-weight: bold; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

st.title("🎉 Ravi Festival Poster Maker")
st.markdown("<p style='text-align: center;'>1-Click WhatsApp & Facebook Status Maker</p>", unsafe_allow_html=True)

# --- FONT LOAD KARNA ---
@st.cache_resource
def get_font(size):
    font_path = "Roboto-Black.ttf"
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Black.ttf"
            urllib.request.urlretrieve(url, font_path)
        except: pass
    try: return ImageFont.truetype(font_path, size)
    except: return ImageFont.load_default()

# --- TEMPLATE GENERATOR (Kyunki abhi hamare paas asli images nahi hain) ---
def get_template(festival_name):
    # Standard WhatsApp Status Size (1080 x 1920)
    W, H = 1080, 1920
    
    if festival_name == "Ambedkar Jayanti":
        bg_color = "#1E3A8A" # Deep Blue
        main_text = "Happy Ambedkar\nJayanti"
    elif festival_name == "Diwali":
        bg_color = "#B91C1C" # Deep Red
        main_text = "Happy Diwali\nMay the light shine!"
    elif festival_name == "Holi":
        bg_color = "#9333EA" # Purple
        main_text = "Happy Holi\nColors of Joy!"
    else: # Birthday
        bg_color = "#D97706" # Orange
        main_text = "Happy Birthday\nStay Blessed!"
        
    template = Image.new("RGBA", (W, H), bg_color)
    draw = ImageDraw.Draw(template)
    
    # Template par Tyohar ka naam likhna
    font_large = get_font(120)
    draw.text((100, 300), main_text, font=font_large, fill="white")
    return template

# --- APP LAYOUT ---
st.subheader("1️⃣ Tyohar Select Karein")
festival = st.selectbox("", ["Ambedkar Jayanti", "Diwali", "Holi", "Happy Birthday"])

st.subheader("2️⃣ Apni Photo Daalein")
uploaded_file = st.file_uploader("Upload Portrait Photo", type=['png', 'jpg', 'jpeg'])

st.subheader("3️⃣ Apna Naam Likhein")
user_name = st.text_input("Name (Eg: Ravi Prajapat):", "Aapka Naam")

if uploaded_file and st.button("🚀 Banao Mera Poster!"):
    with st.spinner("Poster ban raha hai..."):
        # 1. Template Load Karo
        template = get_template(festival)
        W, H = template.size
        
        # 2. User ki Photo ka Background Hatao
        img = Image.open(uploaded_file)
        cutout = remove(img)
        
        # 3. Photo ko Resize karo (Poster ke niche lagane ke liye)
        # Man lo photo height ko poster ki aadhi height ka banana hai
        target_h = int(H * 0.45) 
        ratio = target_h / cutout.height
        target_w = int(cutout.width * ratio)
        cutout_resized = cutout.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # 4. Photo ko Bottom-Right (Niche seedhe hath par) set karo
        paste_x = W - target_w - 50  # 50px right margin
        paste_y = H - target_h       # Bottom par chipka hua
        
        template.paste(cutout_resized, (paste_x, paste_y), cutout_resized)
        
        # 5. User ka Naam ek Banner par likho (Niche)
        draw = ImageDraw.Draw(template)
        font_name = get_font(80)
        
        # Naam ke peeche ek patti (banner) lagao
        draw.rectangle([0, H - 150, W, H], fill="#000000")
        
        # Center mein naam likho
        # Approximate center math
        draw.text((50, H - 120), user_name, font=font_name, fill="#FFD700") # Gold Color Text
        
        # --- PREVIEW & DOWNLOAD ---
        st.success("✅ Aapka Poster Tayar Hai!")
        st.image(template, use_container_width=True)
        
        buf = io.BytesIO()
        template.save(buf, format='PNG')
        
        st.download_button(
            label="⬇️ Download Poster for WhatsApp/Insta",
            data=buf.getvalue(),
            file_name=f"{festival}_Poster_{user_name}.png",
            mime="image/png"
        )
