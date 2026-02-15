import streamlit as st
from PIL import Image
import io
import zipfile
import requests
from datetime import datetime
import extra_streamlit_components as stx

# --- 1. CONFIG ---
st.set_page_config(page_title="SV Watermark Pro", layout="wide", page_icon="💧", initial_sidebar_state="expanded")

# --- 2. COOKIE MANAGER ---
cookie_manager = stx.CookieManager()

# --- 3. LICENSE VERIFICATION (ANNUAL LOGIC) ---
def verify_license(key):
    if not key: return False
    if key == "SV-MASTER-2026": return True 
    try:
        product_id = "xUKZUCNx_S4bzXzB__ml_w==" 
        response = requests.post(
            "https://api.gumroad.com/v2/licenses/verify",
            data={"product_id": product_id, "license_key": key}
        )
        data = response.json()
        if response.status_code == 200 and data.get("success"):
            buy_date = datetime.strptime(data['purchase']['created_at'].split('T')[0], "%Y-%m-%d")
            if (datetime.now() - buy_date).days > 365: return "EXPIRED"
            return True
    except: return False

# --- 4. CSS (ВИПРАВЛЕНО: СТРІЛКА ТЕПЕР НЕ ПРОПАДАЄ) ---
st.markdown("""
    <style>
    /* ПРИХОВУЄМО ТІЛЬКИ ЗАЙВІ КНОПКИ, А НЕ ВЕСЬ HEADER */
    .stAppDeployButton {display:none !important;} 
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stAppToolbar"] {display: none !important;}
    
    /* Робимо фон хедера прозорим, щоб не було білої смуги, але кнопка сайдбару залишилась */
    [data-testid="stHeader"] {background: rgba(0,0,0,0) !important; color: white !important;}
    
    /* ДИЗАЙН ІНТЕРФЕЙСУ */
    .block-container { padding-top: 1rem !important; }
    .stApp, [data-testid="stSidebar"], .main { background-color: #0E1117 !important; color: #FFFFFF !important; }
    p, label, span, .stMarkdown, .stSlider label, .stSelectbox label { color: #00FF88 !important; font-weight: 600 !important; }
    [data-testid="stSidebar"] { border-right: 2px solid #00FF88 !important; box-shadow: 5px 0px 20px rgba(0, 255, 136, 0.2) !important; }
    
    .brand-container { display: flex; align-items: center; justify-content: center; width: 100%; padding-bottom: 25px; }
    .sv-logo-box { background-color: #00FF88; color: #000; font-weight: 900; width: 55px; height: 55px; display: flex; align-items: center; justify-content: center; border-radius: 12px; font-size: 30px; margin-right: 18px; }
    
    div[data-testid="column"] > div > div > div.stVerticalBlock { background-color: #161B22 !important; border: 1px solid #00FF88 !important; border-radius: 12px; padding: 25px; }
    .stButton > button { background-color: #00FF88 !important; color: #000 !important; font-weight: 800 !important; height: 60px; border-radius: 10px; width: 100%; }
    
    .bavovna-banner { background: linear-gradient(90deg, #0057B7 0%, #FFD700 100%); color: white !important; padding: 20px; border-radius: 15px; text-align: center; font-size: 24px; font-weight: 800; margin-bottom: 25px; border: 2px solid #00FF88; }
    </style>
""", unsafe_allow_html=True)

# --- 5. TRANSLATIONS (EN DEFAULT) ---
if 'lang' not in st.session_state: st.session_state.lang = 'EN'
def sync_lang(): st.session_state.lang = st.session_state.lang_picker

translations = {
    "EN": {
        "title": "Watermark Pro", "free_warn": "⚠️ Free Version: 5 photos.", "process_btn": "🚀 PROCESS ALL", 
        "logo_size": "Logo Size %", "alpha": "Transparency (Alpha)",
        "pos_label": "Position", "pos_options": ["Center", "Bottom Right", "Bottom Left", "Mosaic"],
        "up_header": "📂 1. Upload Files", "up_photos": "Select Photos", "up_logo": "Logo (PNG)",
        "setup_header": "⚙️ 2. Setup Logo", "preview": "👁️ SV Preview", "buy_btn": "💎 BUY ANNUAL LICENSE",
        "hint": "💡 Special offer: do you know the Ukrainian magic word related to 'explosive flowers'? Enter it above.", 
        "egg": "💙💛 Glory to Ukraine! 50% discount activated.", "done": "✅ Done!", "expired": "❌ License Expired."
    },
    "UA": {
        "title": "Watermark Pro", "free_warn": "⚠️ Безкоштовна версія: 5 фото.", "process_btn": "🚀 ОБРОБИТИ ВСЕ", 
        "logo_size": "Розмір лого %", "alpha": "Прозорість (Alpha)",
        "pos_label": "Позиція", "pos_options": ["Центр", "Знизу праворуч", "Знизу ліворуч", "Мозаїка"],
        "up_header": "📂 1. Завантажити файли", "up_photos": "Оберіть фото", "up_logo": "Лого (PNG)",
        "setup_header": "⚙️ 2. Налаштування", "preview": "👁️ SV Перегляд", "buy_btn": "💎 КУПИТИ РІЧНУ ЛІЦЕНЗІЮ",
        "hint": "💡 Спеціальна пропозиція: чи знаєте ви українське магічне слово, пов'язане з 'вибуховими квітами'? Введіть його вище.", 
        "egg": "💙💛 Слава Україні! Знижка 50% активована.", "done": "✅ Готово!", "expired": "❌ Ліцензія закінчилася."
    },
    "IT": {
        "title": "Watermark Pro", "free_warn": "⚠️ Versione Gratuita: 5 foto.", "process_btn": "🚀 ELABORA TUTTO", 
        "logo_size": "Grandezza Logo %", "alpha": "Trasparenza (Alpha)",
        "pos_label": "Posizione", "pos_options": ["Centro", "In basso a destra", "In basso a sinistra", "Mosaico"],
        "up_header": "📂 1. Carica File", "up_photos": "Seleziona Foto", "up_logo": "Logo (PNG)",
        "setup_header": "⚙️ 2. Configurazione", "preview": "👁️ Anteprima SV", "buy_btn": "💎 ACQUISTA ABBONAMENTO",
        "hint": "💡 Conosci la parola magica ucraina legata ai 'fiori esplosivi'? Inseriscila sopra.", 
        "egg": "💙💛 Gloria all'Ucraina! Sconto 50%.", "done": "✅ Fatto!", "expired": "❌ Licenza scaduta."
    },
    "DE": {
        "title": "Watermark Pro", "free_warn": "⚠️ Gratis: 5 Fotos.", "process_btn": "🚀 ALLE VERARBEITEN", 
        "logo_size": "Logo-Größe %", "alpha": "Transparenz (Alpha)",
        "pos_label": "Position", "pos_options": ["Mitte", "Unten rechts", "Unten links", "Mosaik"],
        "up_header": "📂 1. Dateien hochladen", "up_photos": "Fotos auswählen", "up_logo": "Logo (PNG)",
        "setup_header": "⚙️ 2. Logo-Einstellungen", "preview": "👁️ SV Vorschau", "buy_btn": "💎 JAHRESLIZENZ KAUFEN",
        "hint": "💡 Kennen Sie das Zauberwort, das з 'explosiven Blumen' zu tun hat? Geben Sie es oben ein.", 
        "egg": "💙💛 Ruhm der Ukraine! 50% Rabatt.", "done": "✅ Fertig!", "expired": "❌ Lizenz abgelaufen."
    }
}
t = translations[st.session_state.lang]

# --- 6. HEADER (LOGO + TOP-RIGHT LANG) ---
col_logo, col_lang = st.columns([8, 2])
with col_logo:
    st.markdown(f'<div class="brand-container"><div class="sv-logo-box">SV</div><h1 style="color:white; margin:0; font-size: 38px;">{t["title"]}</h1></div>', unsafe_allow_html=True)
with col_lang:
    st.selectbox(" ", ["EN", "UA", "IT", "DE"], index=["EN", "UA", "IT", "DE"].index(st.session_state.lang), key="lang_picker", on_change=sync_lang, label_visibility="collapsed")

# --- 7. SIDEBAR (LICENSE & EGG CHECK) ---
with st.sidebar:
    st.markdown("### 🔐 SV Area PRO")
    saved_key = cookie_manager.get(cookie="sv_license_key")
    user_key = st.text_input("License Key", value=saved_key if saved_key else "", type="password")
    
    is_egg = user_key and user_key.lower().strip() == "bavovna"
    gumroad_url = "https://8052063206525.gumroad.com/l/xuyjsl?offer_code=H49A3MP" if is_egg else "https://8052063206525.gumroad.com/l/xuyjsl"
    
    st.link_button(t["buy_btn"], gumroad_url, use_container_width=True)
    st.write("---")
    
    status = verify_license(user_key)
    is_pro = status is True
    if status == "EXPIRED": st.error(t["expired"])
    elif is_pro:
        st.success("✅ ANNUAL PRO ACTIVE")
        if user_key != saved_key: cookie_manager.set("sv_license_key", user_key)
    else: st.warning(t["free_warn"])
    
    st.caption(t["hint"])

# --- 8. MAIN AREA (BAVOVNA BANNER) ---
if is_egg:
    st.markdown(f'<div class="bavovna-banner">{t["egg"]}</div>', unsafe_allow_html=True)
    st.balloons()

# --- 9. UI & LOGIC ---
col1, col2 = st.columns(2, gap="large")
with col1:
    st.markdown(f"### {t['up_header']}")
    ups  = st.file_uploader(t["up_photos"], accept_multiple_files=True, type=['jpg','png','jpeg'])
    lgo = st.file_uploader(t["up_logo"], type=['png'])
with col2:
    st.markdown(f"### {t['setup_header']}")
    p_sel = st.selectbox(t["pos_label"], t["pos_options"])
    sz = st.slider(t["logo_size"], 5, 100, 20)
    op = st.slider(t["alpha"], 0, 255, 128)

def apply(img_f, logo_f, s, a, p):
    im = Image.open(img_f).convert("RGBA"); wm = Image.open(logo_f).convert("RGBA")
    w_w = int((im.width * s) / 100); w_h = int(wm.height * (w_w / wm.width))
    wm = wm.resize((w_w, w_h), Image.Resampling.LANCZOS)
    r,g,b,alpha = wm.split(); wm.putalpha(alpha.point(lambda x: x * (a / 255)))
    ly = Image.new('RGBA', im.size, (0,0,0,0))
    if p in ["Center", "Центр", "Centro", "Mitte"]: ly.paste(wm, ((im.width - wm.width)//2, (im.height - wm.height)//2))
    elif any(x in p for x in ["Right", "праворуч", "destra", "rechts"]): ly.paste(wm, (im.width - wm.width - 20, im.height - wm.height - 20))
    elif any(x in p for x in ["Left", "ліворуч", "sinistra", "links"]): ly.paste(wm, (20, im.height - wm.height - 20))
    elif any(x in p for x in ["Mosaic", "Мозаїка", "Mosaico", "Mosaik"]):
        for x in range(0, im.width, wm.width + 50):
            for y in range(0, im.height, wm.height + 50): ly.paste(wm, (x, y))
    return Image.alpha_composite(im, ly).convert("RGB")

if ups  and lgo:
    st.markdown(f"### {t['preview']}")
    st.image(apply(ups[0], lgo, sz, op, p_sel), use_container_width=True)

# --- 10. ZIP LOGIC ---
if 'usage_count' not in st.session_state: st.session_state.usage_count = 0
max_f = 1000 if is_pro else 5
rem = max_f - st.session_state.usage_count

if not is_pro and rem <= 0: st.error("⛔ Limit reached!")
else:
    if not is_pro: st.write(f"Remaining: **{rem}**")
    if st.button(t["process_btn"], type="primary", use_container_width=True):
        if ups  and lgo:
            zip_buffer = io.BytesIO()
            to_process = ups[:rem] if not is_pro else ups
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zf:
                for f in to_process:
                    res = apply(f, lgo, sz, op, p_sel); b = io.BytesIO()
                    res.save(b, format='JPEG', quality=90); zf.writestr(f"SV_{f.name}", b.getvalue())
            if not is_pro: st.session_state.usage_count += len(to_process)
            st.success(t["done"]); st.download_button("📥 DOWNLOAD ZIP", zip_buffer.getvalue(), "SV_Photos.zip", "application/zip", use_container_width=True)