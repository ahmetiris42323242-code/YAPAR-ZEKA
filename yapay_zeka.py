import streamlit as st
import requests
import base64
from duckduckgo_search import DDGS
from gtts import gTTS
import os

# --- KONUM TESPİTİ ---
def get_user_location():
    try:
        res = requests.get('https://ipinfo.io/')
        data = res.json()
        return f"{data.get('city', 'Isparta')}, {data.get('region', 'Türkiye')}"
    except:
        return "Şarkikaraağaç, Isparta"

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Ahmet İRİŞ Asistanı", page_icon="🤖", layout="wide")

# Başlık ve İmza
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
        st.success("✅ SÜPER ZEKA AKTİF")
    
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
    image_data = None
    text_content = ""
    if uploaded_file:
        if uploaded_file.type.startswith('image'):
            image_data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        else:
            text_content = uploaded_file.read().decode("utf-8")

    st.session_state.messages.append({"role": "user", "content": prompt})

    # ARAMA VE KONUM
    user_loc = get_user_location()
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"{prompt} konum: {user_loc}", max_results=3))
            search_results = f"\n\nGüncel Bilgi ({user_loc}): {results}"
    except:
        search_results = ""

    # MODEL MANTIĞI
    if st.session_state.is_dev_mode:
        model_name, temp, sys_msg = "gpt-4o", 0.05, "Sen Ahmet İRİŞ'in Süper Zekasısın. Kusursuz analiz yap."
    else:
        model_name, temp, sys_msg = "gpt-4o-mini", 0.7, "Sen asistan botusun."
    
    headers = {"Authorization": f"Bearer {st.secrets['GEMINI_API_KEY']}", "Content-Type": "application/json"}
    
    full_content = [{"type": "text", "text": prompt + f"\nDosya: {text_content}" + search_results}]
    if image_data:
        full_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})

    payload = {
        "model": model_name,
        "messages": [{"role": "system", "content": sys_msg}] + st.session_state.messages[:-1] + [{"role": "user", "content": full_content}],
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
        
