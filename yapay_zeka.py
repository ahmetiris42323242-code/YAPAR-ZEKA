import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os

# --- ARAYÜZ ---
st.set_page_config(page_title="Ahmet İRİŞ Asistanı", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")

# --- API AYARLARI ---
API_KEY = st.secrets["GEMINI_API_KEY"]
URL = "https://router.flatkey.ai/v1/chat/completions"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SOHBET GÖSTERİMİ ---
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            if st.button("🔊 Sesli Oku", key=f"audio_{i}"):
                tts = gTTS(text=message["content"], lang='tr')
                tts.save(f"cevap_{i}.mp3")
                st.audio(f"cevap_{i}.mp3")

# --- MESAJ VE DOSYA GİRİŞİ ---
col1, col2 = st.columns([0.8, 0.2])
with col1:
    prompt = st.chat_input("Mesajını yaz...")
with col2:
    uploaded_file = st.file_uploader("Dosya", type=['txt', 'md', 'jpg', 'jpeg', 'png'], label_visibility="collapsed")

# Dosya İşleme
image_data = None
text_content = ""

if uploaded_file:
    if uploaded_file.type.startswith('image'):
        # Görseli base64 formatına çevir
        bytes_data = uploaded_file.getvalue()
        image_data = base64.b64encode(bytes_data).decode('utf-8')
        st.success("Görsel yüklendi!")
    else:
        text_content = uploaded_file.read().decode("utf-8")
        st.success("Metin dosyası yüklendi!")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Görsel varsa içeriğe ekle
        message_content = [{"type": "text", "text": prompt}]
        if image_data:
            message_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})
        if text_content:
            message_content[0]["text"] += f"\n\nDosya İçeriği: {text_content}"

        # API Gönderimi
        payload = {
            "model": "gpt-4o", # Modelin görseli desteklemesi gerekir
            "messages": [{"role": "user", "content": message_content}]
        }
            
        try:
            response = requests.post(URL, headers=headers, json=payload)
            if response.status_code == 200:
                answer = response.json()['choices'][0]['message']['content']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
            else:
                st.error("API Bağlantı Hatası!")
        except Exception as e:
            st.error(f"Hata: {e}")
