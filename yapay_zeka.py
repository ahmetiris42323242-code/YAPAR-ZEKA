import streamlit as st
import requests
import json
import os
from streamlit_mic_recorder import mic_recorder

# --- 1. ARAYÜZ VE BAŞLIK ---
st.set_page_config(page_title="Web Tabanlı Yapay Zeka", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("By Ahmet İRİŞ")
st.markdown("---")

# --- 2. SES VE API KURULUMU ---
API_KEY = os.environ.get("GEMINI_API_KEY")

# Mikrofon Butonu
audio_text = mic_recorder(start_prompt="Mikrofonu Aç", stop_prompt="Durdur", just_once=True)

if not API_KEY:
    st.error("API Anahtarı eksik!")
    st.stop()

URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?key={API_KEY}"

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. İŞLETİM MANTIĞI ---
def get_ai_response(text_input):
    system_instruction = (
        "Sen Ahmet İRİŞ'in dijital asistanısın. Hem ciddi hem samimi bir ton kullan. "
        "Aşırı samimi hitaplardan kaçın. Konunun içeriğine göre kısa veya kapsamlı cevaplar ver. "
        "Profesyonel ve içten bir tutum sergile."
    )
    
    contents = [{"role": "user", "parts": [{"text": text_input}]}]
    data = {"contents": contents, "systemInstruction": {"parts": [{"text": system_instruction}]}}
    
    response = requests.post(URL, headers={"Content-Type": "application/json"}, data=json.dumps(data), stream=True)
    return response

# Metin girişinden veya sesten gelen mesajı işleme
user_input = st.chat_input("Bir mesaj yaz...")
if audio_text:
    user_input = audio_text['text']

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response = get_ai_response(user_input)
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
