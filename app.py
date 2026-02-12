import streamlit as st
from PIL import Image, ImageOps
import io
import zipfile

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Auto-Watermark Pro", layout="centered")

# --- MODIFICA QUESTI DATI ---
SECRET_KEY = "ITALIA-PRO-2025"  # Твій пароль (впиши такий самий в Gumroad)
PAYMENT_LINK = "https://gumroad.com/..." # Твоє посилання на товар (з ціною в €)
PRICE_TEXT = "€9.99" # Ціна, яку бачить клієнт на кнопці

st.title("💧 Auto-Watermark: Gratis vs PRO")
st.markdown("### Aggiungi logo/watermark a 100+ foto in 1 click.")

# --- SIDEBAR (ACCESSO & IMPOSTAZIONI) ---
st.sidebar.header("🔐 Area PRO")
st.sidebar.markdown("Hai già la licenza? Inserisci la chiave qui sotto.")
user_key = st.sidebar.text_input("Chiave di accesso (License Key)", type="password")

# Перевірка ключа
if user_key == SECRET_KEY:
    st.sidebar.success("✅ Modalità PRO Attiva! Illimitato.")
    max_files = 1000
    is_pro = True
else:
    st.sidebar.warning("⚠️ Versione Gratuita: max 5 foto.")
    st.sidebar.markdown("---")
    # Кнопка купівлі
    st.sidebar.markdown(f"""
    <a href="{PAYMENT_LINK}" target="_blank">
        <button style="
            background-color: #28a745; 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            width: 100%;
            font-size: 16px;
            font-weight: bold;">
            🔓 Sblocca tutto a soli {PRICE_TEXT}
        </button>
    </a>
    <p style="font-size: 12px; margin-top: 5px; text-align: center; color: #555;">
    Pagamento sicuro una tantum. Accesso a vita.
    </p>
    """, unsafe_allow_html=True)
    
    max_files = 5
    is_pro = False

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Impostazioni")
transparency = st.sidebar.slider("Trasparenza Logo", 0, 255, 128)
logo_size_percent = st.sidebar.slider("Grandezza Logo (%)", 10, 50, 20)
position = st.sidebar.selectbox("Posizione", ["Centro", "Angolo in basso a destra", "Angolo in basso a sinistra"])

# --- CARICAMENTO FILE ---
uploaded_files = st.file_uploader("1. Seleziona le foto (JPG/PNG)", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
watermark_file = st.file_uploader("2. Carica il tuo logo (PNG trasparente)", type=['png'])

# --- LOGICA LIMITI ---
files_to_process = []
if uploaded_files:
    if len(uploaded_files) > max_files:
        st.error(f"⛔ Hai caricato {len(uploaded_files)} foto. La versione gratuita permette solo {max_files} foto.")
        st.info("Elaboreremo solo le prime 5. Per sbloccare il limite, acquista la licenza PRO nel menu a sinistra.")
        files_to_process = uploaded_files[:max_files]
    else:
        files_to_process = uploaded_files

# --- FUNZIONE DI ELABORAZIONE ---
def process_image(main_img, watermark, opacity, size_pct, pos):
    main_img = main_img.convert("RGBA")
    watermark = watermark.convert("RGBA")

    width_ratio = (main_img.width * size_pct) / 100
    w_percent = (width_ratio / float(watermark.size[0]))
    h_size = int((float(watermark.size[1]) * float(w_percent)))
    watermark = watermark.resize((int(width_ratio), h_size), Image.Resampling.LANCZOS)

    r, g, b, alpha = watermark.split()
    alpha = alpha.point(lambda p: p * (opacity / 255))
    watermark.putalpha(alpha)

    if pos == "Centro":
        x = int((main_img.width - watermark.width) / 2)
        y = int((main_img.height - watermark.height) / 2)
    elif pos == "Angolo in basso a destra":
        x = main_img.width - watermark.width - 20
        y = main_img.height - watermark.height - 20
    else: 
        x = 20
        y = main_img.height - watermark.height - 20

    transparent_layer = Image.new('RGBA', main_img.size, (0,0,0,0))
    transparent_layer.paste(watermark, (x, y))
    output = Image.alpha_composite(main_img, transparent_layer)
    return output.convert("RGB")

# --- PULSANTE AVVIO ---
if st.button(f"🚀 Elabora {len(files_to_process)} foto"):
    if not watermark_file:
        st.warning("Per favore, carica il logo!")
    elif not files_to_process:
        st.warning("Per favore, carica le foto!")
    else:
        progress_bar = st.progress(0)
        zip_buffer = io.BytesIO()
        watermark_img = Image.open(watermark_file)
        
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for i, file in enumerate(files_to_process):
                img = Image.open(file)
                processed_img = process_image(img, watermark_img, transparency, logo_size_percent, position)
                
                img_byte_arr = io.BytesIO()
                processed_img.save(img_byte_arr, format='JPEG', quality=90)
                zip_file.writestr(f"processed_{file.name}", img_byte_arr.getvalue())
                progress_bar.progress((i + 1) / len(files_to_process))
        
        st.success(f"Fatto! {len(files_to_process)} foto elaborate.")
        
        st.download_button(
            label="📥 Scarica le foto (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="watermarked_photos.zip",
            mime="application/zip"
        )