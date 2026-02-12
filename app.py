import streamlit as st
from PIL import Image
import io
import zipfile

# --- 1. CONFIG ---
# Встановлюємо початковий стан панелі "expanded", щоб клієнт одразу бачив кнопку покупки
st.set_page_config(
    page_title="SV Watermark Pro", 
    layout="wide", 
    page_icon="💧",
    initial_sidebar_state="expanded"
)

# --- 2. CSS (БРЕНДИНГ ТА ФІКСИ) ---
st.markdown("""
    <style>
    /* Темна тема та неонові акценти */
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"], .main {
        background-color: #0E1117 !important;
        color: #FFFFFF !important;
    }
    
    /* РОБИМО КНОПКУ МЕНЮ ВИДИМОЮ (для маленьких екранів) */
    button[kind="headerNoPadding"] {
        display: flex !important;
        color: #00FF88 !important;
        visibility: visible !important;
    }

    /* ВЕСЬ ТЕКСТ ТА ПІДПИСИ ТЕПЕР ЯСКРАВО-ЗЕЛЕНІ */
    p, label, span, .stMarkdown, .stSlider label, .stSelectbox label {
        color: #00FF88 !important;
        font-weight: 600 !important;
    }

    /* НЕОНОВА ЛІНІЯ ТА ТІНЬ SIDEBAR */
    [data-testid="stSidebar"] {
        border-right: 2px solid #00FF88 !important;
        box-shadow: 5px 0px 20px rgba(0, 255, 136, 0.2) !important;
    }

    /* СТИЛЬ БЛОКІВ-КАРТОК */
    div[data-testid="column"] > div > div > div.stVerticalBlock {
        background-color: #161B22 !important;
        border: 1px solid #00FF88 !important;
        border-radius: 12px !important;
        padding: 25px !important;
        margin-bottom: 25px !important;
    }

    /* ЛОГОТИП SV (ЧОРНІ БУКВИ НА ЗЕЛЕНОМУ) */
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
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        font-size: 32px;
        margin-right: 15px;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.5);
    }
    .brand-name { color: #FFFFFF !important; font-size: 32px; font-weight: bold; }

    /* СТИЛЬ КНОПОК */
    .stButton > button {
        background-color: #00FF88 !important;
        color: #000000 !important;
        font-weight: 800 !important;
        height: 60px !important;
        font-size: 20px !important;
        border-radius: 10px !important;
    }

    /* ПРИХОВУЄМО ТЕХНІЧНІ ЕЛЕМЕНТИ */
    [data-testid="stToolbar"] { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIC & LANGUAGES (Trasparenza) ---
if 'usage_count' not in st.session_state: st.session_state.usage_count = 0
if 'lang' not in st.session_state: st.session_state.lang = 'IT'

def update_lang(): st.session_state.lang = st.session_state.lang_trigger

translations = {
    "IT": { "t": "Watermark Pro", "f": "⚠️ Versione Gratuita: 5 foto.", "btn": "🚀 ELABORA TUTTO", "pre": "👁️ Anteprima SV", "usage": "Rimaste: ", "size": "Grandezza Logo %", "op": "Trasparenza (Alpha)", "pos": ["Centro", "In basso a destra", "In basso a sinistra", "Mosaico"] },
    "EN": { "t": "Watermark Pro", "f": "⚠️ Free version: 5 photos.", "btn": "🚀 PROCESS ALL", "pre": "👁️ SV Preview", "usage": "Remaining: ", "size": "Logo Size %", "op": "Transparency (Alpha)", "pos": ["Center", "Bottom Right", "Bottom Left", "Mosaic"] },
    "DE": { "t": "Watermark Pro", "f": "⚠️ Kostenlose Version: 5 Fotos.", "btn": "🚀 FOTOS BEARBEITEN", "pre": "👁️ SV Vorschau", "usage": "Verbleibend: ", "size": "Logo-Größe %", "op": "Transparenz (Alpha)", "pos": ["Mitte", "Unten Rechts", "Unten Links", "Mosaik"] }
}
t = translations[st.session_state.lang]

# --- 4. HEADER ---
c_title, c_lang = st.columns([10, 1.4])
with c_title:
    st.markdown(f'<div class="brand-container"><div class="sv-logo-box">SV</div><div class="brand-name">{t["t"]}</div></div>', unsafe_allow_html=True)
with c_lang:
    st.selectbox("", ["IT", "EN", "DE"], index=["IT", "EN", "DE"].index(st.session_state.lang), key="lang_trigger", on_change=update_lang, label_visibility="collapsed")

# --- 5. SIDEBAR (ЗВ'ЯЗОК З GUMROAD) ---
with st.sidebar:
    st.markdown("### 🔐 SV Area PRO")
    
    # КНОПКА ПОКУПКИ, ЩО ВЕДЕ НА GUMROAD
    st.link_button("💎 ACQUISTA LICENZA PRO", "https://8052063206525.gumroad.com/l/xuyjsl")
    
    st.write("---")
    key = st.text_input("Inserisci License Key", type="password")
    
    # ПЕРЕВІРКА КЛЮЧА
    is_pro = key == "SV-PRO-2025"
    if is_pro: 
        st.success("✅ PRO ATTIVO")
    else: 
        st.warning(t["f"])

# --- 6. MAIN INTERFACE ---
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

# --- 7. PROCESSING ---
def apply(img_f, logo_f, s, a, p):
    im = Image.open(img_f).convert("RGBA"); wm = Image.open(logo_f).convert("RGBA")
    w_w = int((im.width * s) / 100); w_h = int(wm.height * (w_w / wm.width))
    wm = wm.resize((w_w, w_h), Image.Resampling.LANCZOS)
    r,g,b,alpha = wm.split(); wm.putalpha(alpha.point(lambda x: x * (a / 255)))
    ly = Image.new('RGBA', im.size, (0,0,0,0))
    if any(x in p for x in ["Centro", "Center", "Mitte"]): ly.paste(wm, ((im.width - wm.width)//2, (im.height - wm.height)//2))
    elif any(x in p for x in ["destra", "Right", "Rechts"]): ly.paste(wm, (im.width - wm.width - 20, im.height - wm.height - 20))
    elif any(x in p for x in ["sinistra", "Left", "Links"]): ly.paste(wm, (20, im.height - wm.height - 20))
    elif any(x in p for x in ["Mosaico", "Mosaic", "Mosaik"]):
        for x in range(0, im.width, wm.width + 50):
            for y in range(0, im.height, wm.height + 50): ly.paste(wm, (x, y))
    return Image.alpha_composite(im, ly).convert("RGB")

# --- 8. PREVIEW & EXECUTION ---
if ups  and lgo:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        st.markdown(f"### {t['pre']}")
        st.image(apply(ups[0], lgo, sz, op, p_sel), use_container_width=True)

st.write("")
max_f = 1000 if is_pro else 5
rem = max_f - st.session_state.usage_count

if not is_pro and rem <= 0:
    st.error("⛔ Limite raggiunto! Acquista la versione PRO.")
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