import streamlit as st
import requests
import base64
import json
from duckduckgo_search import DDGS
from gtts import gTTS

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Ahmet İRİŞ Asistanı", page_icon="🤖", layout="wide")

st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.markdown("##### <span style='color:grey'>By Ahmet İRİŞ | Senior Yazılım Mimarı 2026</span>", unsafe_allow_html=True)
st.divider()

# --- GELİŞTİRİCİ PANELİ ---
if "is_dev_mode" not in st.session_state:
    st.session_state.is_dev_mode = False

with st.sidebar:
    st.subheader("⚙️ Geliştirici Paneli")
    if st.text_input("Şifre", type="password") == "7536":
        st.session_state.is_dev_mode = True
        st.success("✅ PRO MOD AKTİF")
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

col1, col2 = st.columns([0.9, 0.1])
with col1:
    prompt = st.chat_input("Mesajını yaz...")
with col2:
    uploaded_file = st.file_uploader("Dosya", type=['txt', 'md', 'jpg', 'jpeg', 'png'], label_visibility="collapsed")

if prompt:
    # Dosya işleme
    text_content = ""
    image_data = None
    if uploaded_file:
        if uploaded_file.type.startswith('image'):
            image_data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        else:
            text_content = uploaded_file.read().decode("utf-8")

    st.session_state.messages.append({"role": "user", "content": prompt})

    # ARAMA
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(prompt, max_results=1))
            search_context = f"\n\nGüncel İnternet Bilgisi: {results}"
    except:
        search_context = ""

    # MODEL SEÇİMİ
    model_name = "gpt-4o" if st.session_state.is_dev_mode else "gpt-4o-mini"
    
    # PAYLOAD HAZIRLAMA
    payload = {
        "model": model_name,
        "messages": [{"role": "system", "content": "Sen Ahmet İRİŞ'in asistanısın. Kısa ve net cevap ver."}] + 
                     [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
        "temperature": 0.3
    }
    
    headers = {
        "Authorization": f"Bearer {st.secrets['GEMINI_API_KEY']}", 
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post("https://router.flatkey.ai/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
        else:
            st.error(f"API Hatası ({response.status_code}): {response.text}")
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
