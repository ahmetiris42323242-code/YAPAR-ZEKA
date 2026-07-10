import streamlit as st
import requests
import base64
from duckduckgo_search import DDGS
from datetime import datetime
from gtts import gTTS
import os

# --- ARAYÜZ ---
st.set_page_config(page_title="Ahmet İRİŞ Asistanı", page_icon="🤖", layout="wide")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SOHBET ---
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            if st.button("🔊 Sesli Oku", key=f"audio_{i}"):
                tts = gTTS(text=message["content"], lang='tr')
                tts.save(f"cevap_{i}.mp3")
                st.audio(f"cevap_{i}.mp3")

# --- KESİN ÇÖZÜM: CHAT_INPUT YERİNE FORM ---
# Form kullandığımızda sayfa her yenilendiğinde en başa atmaz
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        user_input = st.text_input("Mesajını yaz:", label_visibility="collapsed")
    with col2:
        submitted = st.form_submit_button("🚀 Gönder")
    
    uploaded_file = st.file_uploader("Dosya/Görsel", type=['txt', 'md', 'jpg', 'jpeg', 'png'])

# --- MANTIK ---
if submitted and user_input:
    image_data = None
    text_content = ""
    if uploaded_file:
        if uploaded_file.type.startswith('image'):
            image_data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        else:
            text_content = uploaded_file.read().decode("utf-8")

    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # API İsteği
    URL = "https://router.flatkey.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {st.secrets['GEMINI_API_KEY']}", "Content-Type": "application/json"}
    
    system_instructions = "Sen Ahmet İRİŞ tarafından tasarlanmış uzman bir yazılımcısın."
    msg_content = [{"type": "text", "text": user_input + f"\nDosya: {text_content}"}]
    if image_data:
        msg_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})

    response = requests.post(URL, headers=headers, json={
        "model": "gpt-4o", 
        "messages": [{"role": "system", "content": system_instructions}, {"role": "user", "content": msg_content}]
    })
    
    if response.status_code == 200:
        answer = response.json()['choices'][0]['message']['content']
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()
    
