import streamlit as st
import requests
import json
import os

# --- 1. ARAYÜZ VE BAŞLIK ---
st.set_page_config(page_title="Web Tabanlı Yapay Zeka", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("By Ahmet İRİŞ")
st.markdown("---")

# --- 2. API KONTROLÜ ---
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("🚨 API Anahtarı eksik! Lütfen Render panelinden Environment Variables kısmına GEMINI_API_KEY ekleyin.")
    st.stop()

URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?key={API_KEY}"

# --- 3. SOHBET MANTIĞI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. GİRİŞ VE CEVAP ---
if user_input := st.chat_input("Bir mesaj yaz..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        system_instruction = (
            "Sen Ahmet İRİŞ'in dijital asistanısın. Hem ciddi hem samimi bir ton kullan. "
            "Aşırı samimi hitaplardan kaçın. Profesyonel ve içten bir tutum sergile."
        )
        
        contents = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]} for m in st.session_state.messages]
        data = {"contents": contents, "systemInstruction": {"parts": [{"text": system_instruction}]}}

        try:
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
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
