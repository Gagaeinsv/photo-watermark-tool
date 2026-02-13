import streamlit as st
from PIL import Image
import io
import zipfile
import requests

# --- 1. CONFIG ---
st.set_page_config(
    page_title="SV Watermark Pro", 
    layout="wide", 
    page_icon="💧",
    initial_sidebar_state="expanded"
)

# --- 2. LICENSE VERIFICATION ---
def verify_license(key):
    if not key:
        return False
    
    # Секретний майстер-ключ для тебе та подарунків
    if key == "SV-MASTER-2026":
        return True
    
    try:
        # Твій реальний Product ID зі скріншота
        product_id = "xUKZUCNx_S4bzXzB__ml_w=="
        
        # Запит до Gumroad API для перевірки
        response = requests.post(
            "https://api.gumroad.com/v2/licenses/verify",
            data={"product_id": product_id, "license_key": key}
        )
        data = response.json()
        # Перевірка статусу та валідності
        return response.status_code == 200 and data.get("success") is True
    except:
        return False

# --- 3. CSS (NEON DARK THEME) ---
st.markdown("""
    <style>
    /* Глобальні стилі */
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"], .main {
        background-color: #0E1117 !important;
        color: #FFFFFF !important;
    }
    
    /* Текст та підписи яскраво-зелені */
    p, label, span, .stMarkdown, .stSlider label, .stSelectbox label {
        color: #00FF88 !important;
        font-weight: 600 !important;
    }

    /* Сайдбар з неоновою лінією */
    [data-testid="stSidebar"] {
        border-right: 2px solid #00FF88 !important;
        box-shadow: 5px 0px 20px rgba(0, 255, 136, 0.2) !important;
    }

    /* Блоки-картки */
    div[data-testid="column"] > div > div > div.stVerticalBlock {
        background-color: #161B22 !important;
        border: 1px solid #00FF88 !important;
        border-radius: 12px;
        padding: 25px;
    }

    /* Логотип SV */
    .brand-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: -60px;
        padding-bottom: 30px;
    }
    .sv-logo-box {
        background-color: #00FF88;
        color: #000000 !important;
        font-weight: 900;
        width: 60px; height: 60px;
        display: flex; align-items: center; justify-content: center;
        border-radius: 12px; font-size: 32px; margin-right: 15px;
    }

    /* Кнопки */
    .stButton > button {
        background-color: #00FF88 !important;
        color: #000000 !important;
        font-weight: 800 !important;
        height: 60px; border-radius: 10px;
    }
    footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# --- 4. LANGUAGES ---
if 'lang' not in st.session_state: st.session_state.lang = 'IT'
if 'usage_count' not in st.session_state: st.session_state.usage_count = 0

t = {
    "IT": {
        "t": "Watermark Pro",
        "f": "⚠️ Versione Gratuita: 5 foto.",
        "btn": "🚀 ELABORA TUTTO",
        "pre": "👁️ Anteprima SV",
        "usage": "Rimaste: ",
        "size": "Grandezza Logo %",
        "op": "Trasparenza (Alpha)",
        "pos": ["Centro", "In basso a destra", "In basso a sinistra", "Mosaico"]
    }
}[st.session_state.lang]

# --- 5. UI HEADER ---
st.markdown(f'<div class="brand-container"><div class="sv-logo-box">SV</div><h1 style="color:white; margin:0;">{t["t"]}</h1></div>', unsafe_allow_html=True)

# --- 6. SIDEBAR (LICENSE CONTROL) ---
with st.sidebar:
    st.markdown("### 🔐 SV Area PRO")
    # Посилання на твій товар
    st.link_button("💎 ACQUISTA LICENZA PRO", "https://8052063206525.gumroad.com/l/xuyjsl")
    st.write("---")
    user_key = st.text_input("Inserisci License Key", type="password")
    
    is_pro = verify_license(user_key)
    if is_pro:
        st.success("✅ PRO ATTIVO")
    else:
        st.warning(t["f"])

# --- 7. MAIN INTERFACE ---
col1, col2 = st.columns(2, gap="large")
with col1:
    with st.container():
        st.markdown("### 📂 1. Carica File")
        ups  = st.file_uploader("Photos", accept_multiple_files=True, type=['jpg','png','jpeg'], label_visibility="collapsed")
        lgo = st.file_uploader("Logo (PNG)", type=['png'])
with col2:
    with st.container():
        st.markdown("### ⚙️ 2. Setup Logo")
        p_sel = st.selectbox("Posizione", t["pos"])
        sz = st.slider(t["size"], 5, 100, 20)
        op = st.slider(t["op"], 0, 255, 128)

# --- 8. IMAGE LOGIC ---
def apply(img_f, logo_f, s, a, p):
    im = Image.open(img_f).convert("RGBA")
    wm = Image.open(logo_f).convert("RGBA")
    
    w_w = int((im.width * s) / 100)
    w_h = int(wm.height * (w_w / wm.width))
    wm = wm.resize((w_w, w_h), Image.Resampling.LANCZOS)
    
    r, g, b, alpha = wm.split()
    wm.putalpha(alpha.point(lambda x: x * (a / 255)))
    
    ly = Image.new('RGBA', im.size, (0,0,0,0))
    if "Centro" in p: ly.paste(wm, ((im.width - wm.width)//2, (im.height - wm.height)//2))
    elif "destra" in p: ly.paste(wm, (im.width - wm.width - 20, im.height - wm.height - 20))
    elif "sinistra" in p: ly.paste(wm, (20, im.height - wm.height - 20))
    elif "Mosaico" in p:
        for x in range(0, im.width, wm.width + 50):
            for y in range(0, im.height, wm.height + 50):
                ly.paste(wm, (x, y))
                
    return Image.alpha_composite(im, ly).convert("RGB")

# --- 9. PREVIEW & RUN ---
if ups  and lgo:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        st.markdown(f"### {t['pre']}")
        st.image(apply(ups[0], lgo, sz, op, p_sel), use_container_width=True)

st.write("")
max_f = 1000 if is_pro else 5
rem = max_f - st.session_state.usage_count

if not is_pro and rem <= 0:
    st.error("⛔ Limite raggiunto! Acquista la licenza.")
else:
    if not is_pro: st.write(f"{t['usage']} **{rem}**")
    if st.button(t["btn"], type="primary", use_container_width=True):
        if ups  and lgo:
            td = ups[:rem] if not is_pro else ups
            zb = io.BytesIO()
            with zipfile.ZipFile(zb, "a", zipfile.ZIP_DEFLATED) as z:
                for f in td:
                    res = apply(f, lgo, sz, op, p_sel)
                    b = io.BytesIO(); res.save(b, format='JPEG', quality=90)
                    z.writestr(f"SV_{f.name}", b.getvalue())
            if not is_pro: st.session_state.usage_count += len(td)
            st.success("✅ Fatto!"); st.download_button("📥 DOWNLOAD", zb.getvalue(), "SV_Photos.zip", use_container_width=True); st.rerun()