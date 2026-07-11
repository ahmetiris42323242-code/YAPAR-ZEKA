import streamlit as st
import requests
import base64
from duckduckgo_search import DDGS
from gtts import gTTS

# --- KONUM TESPİTİ ---
def get_user_location():
    try:
        res = requests.get('https://ipinfo.io/')
        data = res.json()
        return f"{data.get('city', 'Isparta')}, {data.get('region', 'Türkiye')}"
    except:
        return "Şarkikaraağaç, Isparta"

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Ahmet IRIS Asistanı", page_icon="🤖", layout="wide")

st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.markdown("##### <span style='color:grey'>By Ahmet IRIS | Senior Yazılım Mimarı 2026</span>", unsafe_allow_html=True)
st.divider()

# --- GELİŞTİRİCİ PANELİ ---
if "is_dev_mode" not in st.session_state:
    st.session_state.is_dev_mode = False

with st.sidebar:
    st.subheader("⚙️ Geliştirici Paneli")
    if st.text_input("Şifre", type="password") == "7536":
        st.session_state.is_dev_mode = True
        st.success("✅ SÜPER ZEKA (GEMMA 4 31B) AKTİF")
    
    if st.button("Modu Kapat"):
        st.session_state.is_dev_mode = False
        st.rerun()

# --- SOHBET MANTIĞI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if st.button(f"🔊 Dinle", key=f"audio_{i}"):
                tts = gTTS(text=msg["content"], lang='tr')
                tts.save("cevap.mp3")
                st.audio("cevap.mp3")

# --- GİRDİ ALANI ---
col1, col2 = st.columns([0.9, 0.1])
with col1:
    prompt = st.chat_input("Mesajını yaz...")
with col2:
    uploaded_file = st.file_uploader("Dosya", type=['txt', 'md', 'jpg', 'jpeg', 'png'], label_visibility="collapsed")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ARAMA VE KONUM
    user_loc = get_user_location()
    search_results = ""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"{prompt} konum: {user_loc}", max_results=3))
            search_results = str(results)
    except:
        search_results = "İnternet araması yapılamadı."

    # MODEL MANTIĞI
    if st.session_state.is_dev_mode:
        model_name = "google/gemma-4-31b-it:free"
        sys_msg = "Sen Ahmet IRIS'in baş mimarısın. Teknik analiz ustasısın."
        temp = 0.1
    else:
        model_name = "meta-llama/llama-3.1-8b-instruct"
        sys_msg = "Sen asistan botusun."
        temp = 0.7
    
    # API İSTEĞİ (Karakter hatası düzeltildi)
    headers = {
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "HTTP-Referer": "https://ahmet-iris-asistan.streamlit.app/",
        "X-Title": "Ahmet IRIS Asistan",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": f"{sys_msg}\nGüncel İnternet Verisi: {search_results}"},
            {"role": "user", "content": prompt}
        ],
        "temperature": temp
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
        else:
            st.error(f"API Hatası: {response.status_code}")
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
