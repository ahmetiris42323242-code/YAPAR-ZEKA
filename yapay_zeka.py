import streamlit as st
import requests
import json
import os
from streamlit_mic_recorder import mic_recorder

# --- 1. ARAYÜZ ---
st.set_page_config(page_title="Web Tabanlı Yapay Zeka", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("By Ahmet İRİŞ")
st.markdown("---")

# --- 2. DURUM YÖNETİMİ ---
if "text_content" not in st.session_state:
    st.session_state.text_content = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. SES GİRİŞİ ---
# Kullanıcı mikrofona basınca ses metne dönüşüyor ve text_content'e kaydediliyor
audio_info = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='mic')
if audio_info and isinstance(audio_info, dict) and audio_info.get("text"):
    st.session_state.text_content = audio_info["text"]

# --- 4. MESAJ KUTUSU VE GÖNDERİM ---
# Sesli metin buraya doluyor, kullanıcı isterse düzenleyebiliyor
user_input = st.text_area("Mesajınızı yazın veya sesli girin:", value=st.session_state.text_content, height=100)

if st.button("Gönder"):
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.text_content = "" # Gönderince kutuyu temizle
        st.rerun() # Sayfayı yenileyerek yeni mesajı işleme al

# --- 5. MESAJLARIN GÖSTERİMİ VE CEVAP ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Son mesajı işleme (Eğer kullanıcı gönder dediyse)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        API_KEY = os.environ.get("GEMINI_API_KEY")
        URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?key={API_KEY}"
        
        system_instruction = "Sen Ahmet İRİŞ'in dijital asistanısın. Hem ciddi hem samimi bir ton kullan. Profesyonel ve içten ol."
        
        contents = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]} for m in st.session_state.messages]
        data = {"contents": contents, "systemInstruction": {"parts": [{"text": system_instruction}]}}
        
        response = requests.post(URL, headers={"Content-Type": "application/json"}, data=json.dumps(data), stream=True)
        cevap_kutusu = st.empty()
        tam_cevap = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8').strip()
                if '"text":' in decoded_line:
                    kelime = decoded_line.split('"text":')[1].strip().strip('"').replace('\\n', '\n')
                    tam_cevap += kelime
                    cevap_kutusu.markdown(tam_cevap)
        st.session_state.messages.append({"role": "assistant", "content": tam_cevap})
