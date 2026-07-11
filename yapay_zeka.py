import streamlit as st
import requests
import base64
from duckduckgo_search import DDGS
from gtts import gTTS
import os

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Ahmet İRİŞ Asistanı", page_icon="🤖", layout="wide")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")

# --- GELİŞTİRİCİ PANELİ ---
if "is_dev_mode" not in st.session_state:
    st.session_state.is_dev_mode = False
if "custom_sys_prompt" not in st.session_state:
    st.session_state.custom_sys_prompt = "Sen Ahmet İRİŞ tarafından tasarlanmış kıdemli bir yazılım mimarısın."

with st.sidebar:
    st.subheader("⚙️ Geliştirici Paneli")
    dev_password = st.text_input("Geliştirici Şifresi", type="password")
    
    if dev_password == "7536":
        st.session_state.is_dev_mode = True
        st.success("✅ Geliştirici Modu Aktif")
        st.session_state.custom_sys_prompt = st.text_area("Sistem Talimatlarını Düzenle", st.session_state.custom_sys_prompt)
    elif dev_password != "":
        st.error("❌ Yanlış Şifre!")
    
    if st.button("Modu Kapat"):
        st.session_state.is_dev_mode = False
        st.rerun()

# --- SOHBET MANTIĞI VE GTTS ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if st.button(f"🔊 Sesli Oku {i}", key=f"audio_{i}"):
                tts = gTTS(text=msg["content"], lang='tr')
                tts.save("cevap.mp3")
                st.audio("cevap.mp3")

col1, col2 = st.columns([0.9, 0.1])
with col1:
    prompt = st.chat_input("Mesajını yaz...")
with col2:
    uploaded_file = st.file_uploader("Dosya", type=['txt', 'md', 'jpg', 'jpeg', 'png'], label_visibility="collapsed")

if prompt:
    # Dosya İşleme
    image_data = None
    text_content = ""
    if uploaded_file:
        if uploaded_file.type.startswith('image'):
            image_data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        else:
            text_content = uploaded_file.read().decode("utf-8")

    st.session_state.messages.append({"role": "user", "content": prompt})

    # ARAMA ÖZELLİĞİ
    search_results = ""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(prompt, max_results=2))
            search_results = f"\n\nGüncel Bilgi: {results}"
    except:
        search_results = ""

    # MİMARİ MANTIĞI
    sys_msg = st.session_state.custom_sys_prompt
    
    headers = {"Authorization": f"Bearer {st.secrets['GEMINI_API_KEY']}", "Content-Type": "application/json"}
    
    full_content = [{"type": "text", "text": prompt + f"\nDosya: {text_content}" + search_results}]
    if image_data:
        full_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})

    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "system", "content": sys_msg}] + st.session_state.messages[:-1] + [{"role": "user", "content": full_content}],
        "temperature": 0.2
    }
    
    try:
        response = requests.post("https://router.flatkey.ai/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
    except Exception as e:
        st.error(f"Hata: {e}")
