import streamlit as st
from PIL import Image
import io
import zipfile
import requests
import extra_streamlit_components as stx

# --- 1. CONFIG & UI CLEANUP ---
st.set_page_config(
    page_title="SV Watermark Pro", 
    layout="wide", 
    page_icon="💧",
    initial_sidebar_state="expanded"
)

# --- 2. COOKIE MANAGER (FIXED CachedWidgetWarning) ---
# Ініціалізуємо менеджер куків напряму в коді, щоб уникнути помилки зі скріншота 7d03e9f3
cookie_manager = stx.CookieManager()

# --- 3. LICENSE VERIFICATION ---
def verify_license(key):
    if not key: return False
    if key == "SV-MASTER-2026": return True
    try:
        product_id = "xUKZUCNx_S4bzXzB__ml_w==" #
        response = requests.post(
            "https://api.gumroad.com/v2/licenses/verify",
            data={"product_id": product_id, "license_key": key}
        )
        data = response.json()
        return response.status_code == 200 and data.get("success") is True
    except:
        return False

# --- 4. CSS (HIDDEN MANAGE APP & CLEAN UI) ---
st.markdown("""
    <style>
    /* ПОВНЕ ПРИХОВУВАННЯ ЕЛЕМЕНТІВ STREAMLIT */
    header {visibility: hidden; height: 0px !important;}
    [data-testid="stHeader"] {display: none;}
    #MainMenu {visibility: hidden;}
    .stAppDeployButton {display:none;}
    footer {visibility: hidden;}
    
    /* ПРИХОВУЄМО КНОПКУ "MANAGE APP" ТА СТАТУСНИЙ ВІДЖЕТ */
    [data-testid="stStatusWidget"] {display: none !important; visibility: hidden !important;}
    [data-testid="stAppToolbar"] {display: none !important;}
    .st-emotion-cache-zt53z0 {display: none !important;} /* Клас для плаваючої кнопки */
    
    /* ПРИБИРАЄМО ВІДСТУП ЗВЕРХУ */
    .block-container { padding-top: 1rem !important; }
    
    .stApp, [data-testid="stHeader"], [data-testid="stSidebar"], .main { background-color: #0E1117 !important; color: #FFFFFF !important; }
    p, label, span, .stMarkdown, .stSlider label, .stSelectbox label { color: #00FF88 !important; font-weight: 600 !important; }
    [data-testid="stSidebar"] { border-right: 2px solid #00FF88 !important; box-shadow: 5px 0px 20px rgba(0, 255, 136, 0.2) !important; }
    
    /* ЦЕНТРУВАННЯ ЗАГОЛОВКА */
    .brand-container { 
        display: flex; align-items: center; justify-content: center; 
        width: 100%; margin-top: 0px; padding-bottom: 25px; 
    }
    .sv-logo-box { 
        background-color: #00FF88; color: #000000 !important; font-weight: 900; 
        width: 55px; height: 55px; display: flex; align-items: center; justify-content: center; 
        border-radius: 12px; font-size: 30px; margin-right: 18px; 
    }
    
    div[data-testid="column"] > div > div > div.stVerticalBlock { background-color: #161B22 !important; border: 1px solid #00FF88 !important; border-radius: 12px; padding: 25px; }
    .stButton > button { background-color: #00FF88 !important; color: #000000 !important; font-weight: 800 !important; height: 60px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 5. TRANSLATIONS (EN PRIMARY) ---
if 'lang' not in st.session_state: st.session_state.lang = 'EN'
def sync_lang(): st.session_state.lang = st.session_state.lang_picker

translations = {
    "EN": {
        "title": "Watermark Pro", "free_warn": "⚠️ Free Version: 5 photos.", "process_btn": "🚀 PROCESS ALL", 
        "remaining": "Remaining: ", "logo_size": "Logo Size %", "alpha": "Transparency (Alpha)",
        "pos_label": "Position", "pos_options": ["Center", "Bottom Right", "Bottom Left", "Mosaic"],
        "up_header": "📂 1. Upload Files", "up_photos": "Select Photos", "up_logo": "Upload Logo (PNG)",
        "setup_header": "⚙️ 2. Setup Logo", "preview": "👁️ SV Preview", "buy_btn": "💎 BUY PRO LICENSE",
        "hint": "💡 Special offer: do you know the Ukrainian magic word related to 'explosive flowers'? Enter it above.",
        "egg": "💙💛 Glory to Ukraine! 50% 'Bavovna' discount activated.", "done": "✅ Done!"
    },
    "IT": {
        "title": "Watermark Pro", "free_warn": "⚠️ Versione Gratuita: 5 foto.", "process_btn": "🚀 ELABORA TUTTO", 
        "remaining": "Rimaste: ", "logo_size": "Grandezza Logo %", "alpha": "Trasparenza (Alpha)",
        "pos_label": "Posizione", "pos_options": ["Centro", "In basso a destra", "In basso a sinistra", "Mosaico"],
        "up_header": "📂 1. Carica File", "up_photos": "Seleziona Foto", "up_logo": "Carica Logo (PNG)",
        "setup_header": "⚙️ 2. Configurazione Logo", "preview": "👁️ Anteprima SV", "buy_btn": "💎 ACQUISTA LICENZA PRO",
        "hint": "💡 Offerta speciale: conosci la parola magica ucraina legata ai 'fiori esplosivi'? Inseriscila sopra.",
        "egg": "💙💛 Слава Україні! Знижка 'Бавовна' 50% активована.", "done": "✅ Fatto!"
    },
    "DE": {
        "title": "Watermark Pro", "free_warn": "⚠️ Kostenlose Version: 5 Fotos.", "process_btn": "🚀 ALLE VERARBEITEN", 
        "remaining": "Verbleibend: ", "logo_size": "Logo-Größe %", "alpha": "Transparenz (Alpha)",
        "pos_label": "Position", "pos_options": ["Mitte", "Unten rechts", "Unten links", "Mosaik"],
        "up_header": "📂 1. Dateien hochladen", "up_photos": "Fotos auswählen", "up_logo": "Logo hochladen (PNG)",
        "setup_header": "⚙️ 2. Logo-Einstellungen", "preview": "👁️ SV Vorschau", "buy_btn": "💎 PRO-LIZENZ KAUFEN",
        "hint": "💡 Sonderangebot: Kennst du das ukrainische Zauberwort für 'explosive Blumen'? Gib es oben ein.",
        "egg": "💙💛 Ruhm der Ukraine! 50% Rabatt aktiviert.", "done": "✅ Fertig!"
    }
}
t = translations[st.session_state.lang]

# --- 6. HEADER (CENTERED) ---
col_empty, col_main, col_lang = st.columns([1, 8, 1])
with col_main:
    st.markdown(f'''<div class="brand-container"><div class="sv-logo-box">SV</div><h1 style="color:white; margin:0; font-size: 42px;">{t["title"]}</h1></div>''', unsafe_allow_html=True)
with col_lang:
    st.selectbox("", ["EN", "IT", "DE"], index=["EN", "IT", "DE"].index(st.session_state.lang), key="lang_picker", on_change=sync_lang, label_visibility="collapsed")

# --- 7. SIDEBAR (COOKIE & LICENSE) ---
with st.sidebar:
    st.markdown("### 🔐 SV Area PRO")
    saved_key = cookie_manager.get(cookie="sv_license_key")
    user_key = st.text_input("License Key / Magic Word", value=saved_key if saved_key else "", type="password")
    
    gumroad_url = "https://8052063206525.gumroad.com/l/xuyjsl"
    if user_key.lower() == "bavovna": # Твій код H49A3MP
        gumroad_url = "https://8052063206525.gumroad.com/l/xuyjsl?offer_code=H49A3MP"
        st.info(t["egg"])
    
    st.link_button(t["buy_btn"], gumroad_url, use_container_width=True)
    st.write("---")
    is_pro = verify_license(user_key)
    if is_pro:
        st.success("✅ PRO ACTIVE" if st.session_state.lang == "EN" else "✅ PRO ATTIVO")
        if user_key != saved_key: cookie_manager.set("sv_license_key", user_key, expires_at=None) 
    else: st.warning(t["free_warn"])
    st.caption(t["hint"])

# --- 8. MAIN UI & LOGIC ---
col1, col2 = st.columns(2, gap="large")
with col1:
    with st.container():
        st.markdown(f"### {t['up_header']}")
        ups  = st.file_uploader(t["up_photos"], accept_multiple_files=True, type=['jpg','png','jpeg'])
        lgo = st.file_uploader(t["up_logo"], type=['png'])
with col2:
    with st.container():
        st.markdown(f"### {t['setup_header']}")
        p_sel = st.selectbox(t["pos_label"], t["pos_options"])
        sz = st.slider(t["logo_size"], 5, 100, 20); op = st.slider(t["alpha"], 0, 255, 128)

def apply(img_f, logo_f, s, a, p):
    im = Image.open(img_f).convert("RGBA"); wm = Image.open(logo_f).convert("RGBA")
    w_w = int((im.width * s) / 100); w_h = int(wm.height * (w_w / wm.width))
    wm = wm.resize((w_w, w_h), Image.Resampling.LANCZOS)
    r,g,b,alpha = wm.split(); wm.putalpha(alpha.point(lambda x: x * (a / 255)))
    ly = Image.new('RGBA', im.size, (0,0,0,0))
    if any(x in p for x in ["Center", "Centro", "Mitte"]): ly.paste(wm, ((im.width - wm.width)//2, (im.height - wm.height)//2))
    elif any(x in p for x in ["Right", "destra", "rechts"]): ly.paste(wm, (im.width - wm.width - 20, im.height - wm.height - 20))
    elif any(x in p for x in ["Left", "sinistra", "links"]): ly.paste(wm, (20, im.height - wm.height - 20))
    elif any(x in p for x in ["Mosaic", "Mosaico", "Mosaik"]):
        for x in range(0, im.width, wm.width + 50):
            for y in range(0, im.height, wm.height + 50): ly.paste(wm, (x, y))
    return Image.alpha_composite(im, ly).convert("RGB")

if ups  and lgo:
    st.markdown("<br>", unsafe_allow_html=True); st.markdown(f"### {t['preview']}")
    st.image(apply(ups[0], lgo, sz, op, p_sel), use_container_width=True)

if 'usage_count' not in st.session_state: st.session_state.usage_count = 0
max_f = 1000 if is_pro else 5
rem = max_f - st.session_state.usage_count

if not is_pro and rem <= 0:
    st.error("⛔ Limit reached!" if st.session_state.lang == "EN" else "⛔ Limite raggiunto!")
else:
    if not is_pro: st.write(f"{t['remaining']} **{rem}**")
    if st.button(t["process_btn"], type="primary", use_container_width=True):
        if ups  and lgo:
            td = ups[:rem] if not is_pro else ups
            zb = io.BytesIO()
            with zipfile.ZipFile(zb, "a", zipfile.ZIP_DEFLATED) as z:
                for f in td:
                    res = apply(f, lgo, sz, op, p_sel); b = io.BytesIO(); res.save(b, format='JPEG', quality=90); z.writestr(f"SV_{f.name}", b.getvalue())
            if not is_pro: st.session_state.usage_count += len(td)
            st.success(t["done"]); st.download_button("📥 DOWNLOAD", zb.getvalue(), "SV_Photos.zip", use_container_width=True); st.rerun()