import streamlit as st
import requests
import base64
import sqlite3
from gtts import gTTS

# --- VERİTABANI BAĞLANTISI ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS premium_users (device_id TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

init_db()

# Cihaz ID tespiti (Otomatik hatırlama için)
device_id = st.context.headers.get("User-Agent", "default_device")

def check_premium():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM premium_users WHERE device_id = ?", (device_id,))
    data = c.fetchone()
    conn.close()
    return data is not None

def add_premium():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO premium_users VALUES (?)", (device_id,))
    conn.commit()
    conn.close()

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Ahmet İRİŞ Asistanı", page_icon="🤖", layout="wide")

# --- PREMIUM KONTROLÜ (OTOMATİK HATIRLAMA) ---
if not check_premium():
    st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
    st.warning("💎 Premium erişim için yıllık 10 TL ödeme yapın.")
    if st.button("Pay with GPay 🚀"):
        add_premium()
        st.success("Ödeme onaylandı! Sayfa yenileniyor...")
        st.rerun()
    st.stop()

# --- PREMIUM KULLANICI ARAYÜZÜ ---
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("By Ahmet İRİŞ - 2026 Senior Yazılım Mimarisi | Premium Aktif")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SOHBET PANELİ ---
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            if st.button("🔊 Sesli Oku", key=f"audio_{i}"):
                tts = gTTS(text=message["content"], lang='tr')
                tts.save(f"cevap_{i}.mp3")
                st.audio(f"cevap_{i}.mp3")
            st.download_button(
                label="💾 Bu Yanıtı Dosya Olarak İndir",
                data=message["content"],
                file_name="yapay_zeka_cevap.txt",
                mime="text/plain",
                key=f"dl_{i}"
            )

# --- GİRİŞ PANELİ ---
col1, col2 = st.columns([0.85, 0.15])
with col1:
    prompt = st.chat_input("Mesajını yaz...")
with col2:
    uploaded_file = st.file_uploader("Dosya", type=['txt', 'md', 'jpg', 'jpeg', 'png'], label_visibility="collapsed")

# --- MANTIK ---
if prompt:
    text_content = ""
    if uploaded_file:
        text_content = uploaded_file.read().decode("utf-8") if not uploaded_file.type.startswith('image') else ""

    st.session_state.messages.append({"role": "user", "content": prompt})

    system_instructions = (
        "Sen Ahmet İRİŞ ve Abduramim İRİŞ tarafından tasarlanmış, kıdemli bir yazılım mimarısın. "
        "KURALLAR: 1. Modülerlik, sürdürülebilirlik ve performans odaklı çalış. "
        "2. Her kod bloğunda değişken isimlendirme standartlarına uy ve güvenlik uyarıları ekle. "
        "3. Teknik olmayan soruları kibarca reddet. 4. Cevapları 2026+ standartlarında sun."
    )

    full_messages = [{"role": "system", "content": system_instructions}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    
    try:
        response = requests.post(
            "https://router.flatkey.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {st.secrets['GEMINI_API_KEY']}", "Content-Type": "application/json"},
            json={"model": "gpt-4o", "messages": full_messages, "temperature": 0.1, "max_tokens": 4096}
        )
        if response.status_code == 200:
            st.session_state.messages.append({"role": "assistant", "content": response.json()['choices'][0]['message']['content']})
            st.rerun()
    except Exception as e:
        st.error(f"Sistem Hatası: {e}")
