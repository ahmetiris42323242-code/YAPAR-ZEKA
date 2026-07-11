import streamlit as st
import requests
import base64
import sqlite3
from duckduckgo_search import DDGS
from datetime import datetime
from gtts import gTTS
import os

# --- VERİTABANI VE OTANTİKASYON ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS premium_users (device_id TEXT PRIMARY KEY)''')
    conn.commit()
    conn.close()

init_db()
device_id = st.context.headers.get("User-Agent", "default_device")

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
st.caption("By Ahmet İRİŞ - 2026 Senior Yazılım Mimarisi Modu | Sabit Dosya Adı Aktif")

# --- ÖDEME KONTROLÜ ---
if not check_premium():
    st.warning("💎 Premium erişim için yıllık 10 TL ödeme yapın.")
    if st.button("Pay with GPay 🚀"):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO premium_users VALUES (?)", (device_id,))
        conn.commit()
        conn.close()
        st.success("Ödeme başarılı! Sayfa yenileniyor...")
        st.rerun()
    st.stop()

# --- API AYARLARI ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 API Anahtarı tanımlanmamış!")
    st.stop()

URL = "https://router.flatkey.ai/v1/chat/completions"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- KAYDIRMA SORUNUNU ÇÖZEN FRAGMENT ---
@st.fragment
def render_chat():
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

render_chat()

# --- GİRİŞ PANELİ ---
col1, col2 = st.columns([0.85, 0.15])
with col1:
    prompt = st.chat_input("Mesajını yaz...")
with col2:
    uploaded_file = st.file_uploader("Dosya", type=['txt', 'md', 'jpg', 'jpeg', 'png'], label_visibility="collapsed")

# --- MANTIK ---
if prompt:
    image_data = None
    text_content = ""
    if uploaded_file:
        if uploaded_file.type.startswith('image'):
            image_data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        else:
            text_content = uploaded_file.read().decode("utf-8")

    st.session_state.messages.append({"role": "user", "content": prompt})

    system_instructions = (
        "Sen Ahmet İRİŞ tarafından tasarlanmış, kıdemli bir yazılım mimarısın. "
        "KURALLAR: "
        "1. Sosyal nezaket kurallarına uy (Selamlaşma ve hal-hatır sorularına samimi cevap ver). "
        "2. KOD ÜRETİMİ (Senior Seviyesi): Kod yazarken; modülerlik, sürdürülebilirlik (DRY prensibi), hata yönetimi (try-except blokları), dokümantasyon ve performans optimizasyonu kurallarını uygula. "
        "3. Her kod bloğunda; değişken isimlendirme standartlarına uy, karmaşık mantığı yorum satırlarıyla açıkla ve olası güvenlik açıklarına karşı uyarılar ekle. "
        "4. Eğer gelen soru teknik bir alanla tamamen alakasızsa, kibarca 'Bu konu uzmanlık alanımın dışındadır, teknik bir soruna odaklanalım' diyerek reddet. "
        "5. Kod sorulduğunda önce mantığı (algoritmayı) açıkla, sonra profesyonel standartlarda kodunu sun."
    )

    full_messages = [{"role": "system", "content": system_instructions}]
    for msg in st.session_state.messages[:-1]:
        full_messages.append({"role": msg["role"], "content": msg["content"]})
    
    current_content = [{"type": "text", "text": prompt + f"\nDosya: {text_content}"}]
    if image_data:
        current_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})
    
    full_messages.append({"role": "user", "content": current_content})

    try:
        response = requests.post(URL, headers=headers, json={
            "model": "gpt-4o", 
            "messages": full_messages,
            "temperature": 0.2, 
            "max_tokens": 4096
        })
        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
    except Exception as e:
        st.error(f"Hata: {e}")
