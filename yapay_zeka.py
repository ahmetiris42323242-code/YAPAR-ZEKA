import streamlit as st
import requests
import base64
import sqlite3
from duckduckgo_search import DDGS # Arama özelliği geri eklendi
from gtts import gTTS

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
st.caption("By Ahmet İRİŞ - 2026 Senior Yazılım Mimarisi | Arama ve Premium Aktif")

# --- PREMIUM KONTROLÜ (HİBRİT) ---
is_premium = check_premium()
if not is_premium:
    st.info("🚀 Premium'a geçerek 'Süper Zeka' ve internet erişimine sahip olabilirsin.")
    if st.button("Ödeme Yaptım, Modu Aktifleştir"):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO premium_users VALUES (?)", (device_id,))
        conn.commit()
        conn.close()
        st.rerun()

# --- SOHBET MANTIĞI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # ARAMA ÖZELLİĞİ (DuckDuckGo Entegrasyonu)
    search_results = ""
    if is_premium: # Arama sadece Premium modda aktif
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(prompt, max_results=3))
                search_results = f"\n\nGüncel İnternet Arama Sonuçları: {results}"
        except:
            search_results = ""

    # SÜPER ZEKA MANTIĞI
    if is_premium:
        model_name = "gpt-4o"
        sys_msg = "Sen Ahmet İRİŞ tarafından tasarlanmış Süper Zeka Mühendisisin. Verilen arama sonuçlarını kullanarak derinlemesine analiz yap."
        temp = 0.05
    else:
        model_name = "gpt-4o-mini"
        sys_msg = "Sen Ahmet İRİŞ tarafından tasarlanmış asistan botusun."
        temp = 0.7

    headers = {"Authorization": f"Bearer {st.secrets['GEMINI_API_KEY']}", "Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "messages": [{"role": "system", "content": sys_msg}] + st.session_state.messages + [{"role": "system", "content": search_results}],
        "temperature": temp
    }
    
    try:
        response = requests.post("https://router.flatkey.ai/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
    except Exception as e:
        st.error(f"Hata: {e}")
