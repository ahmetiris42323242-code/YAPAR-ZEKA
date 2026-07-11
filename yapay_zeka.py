import streamlit as st
import requests
import base64
import sqlite3
from duckduckgo_search import DDGS
from gtts import gTTS

# --- VERİTABANI VE OTANTİKASYON ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS premium_users (device_id TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

init_db()

# Cihaz ID tespiti - Tarayıcıyı kapatsan da kalıcı olması için daha belirgin bir ID
device_id = st.context.headers.get("User-Agent", "default_device") + "_user_01"

def check_premium():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM premium_users WHERE device_id = ?", (device_id,))
    data = c.fetchone()
    conn.close()
    return data is not None

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Ahmet İRİŞ Asistanı", page_icon="🤖", layout="wide")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")

# --- DEBUG PANELİ (Premium'u test etmek için) ---
with st.sidebar:
    st.write("---")
    if st.button("🗑️ Veritabanını Sıfırla (Premium'u Çıkart)"):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("DELETE FROM premium_users")
        conn.commit()
        conn.close()
        st.rerun()

# --- PREMIUM KONTROLÜ ---
is_premium = check_premium()

if not is_premium:
    st.info("🚀 Premium'a geçerek 'Süper Zeka' ve internet erişimine sahip olabilirsin. (Yıllık 10 TL)")
    if st.button("💳 Ödeme Yaptım, Modu Aktifleştir"):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO premium_users VALUES (?)", (device_id,))
        conn.commit()
        conn.close()
        st.success("Premium başarıyla aktifleştirildi!")
        st.rerun()
else:
    st.success("💎 Premium Aktif: Süper Zeka Modu ve İnternet Erişimi Açık")

# --- SOHBET MANTIĞI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

col1, col2 = st.columns([0.9, 0.1])
with col1:
    prompt = st.chat_input("Mesajını yaz...")
with col2:
    uploaded_file = st.file_uploader("Dosya", type=['txt', 'md', 'jpg', 'jpeg', 'png'], label_visibility="collapsed")

if prompt:
    # (Dosya ve API mantığı aynı şekilde kalıyor...)
    image_data = None
    text_content = ""
    if uploaded_file:
        if uploaded_file.type.startswith('image'):
            image_data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        else:
            text_content = uploaded_file.read().decode("utf-8")

    st.session_state.messages.append({"role": "user", "content": prompt})

    # Arama ve Model mantığı aynı...
    search_results = ""
    if is_premium:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(prompt, max_results=3))
                search_results = f"\n\nGüncel İnternet Arama Sonuçları: {results}"
        except:
            search_results = ""

    # ... (API isteği aynı şekilde aşağıya devam eder)
