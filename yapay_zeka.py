import streamlit as st
import requests
import json
import os

# --- 1. ARAYÜZ ---
st.set_page_config(page_title="Web Tabanlı Yapay Zeka", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("By Ahmet İRİŞ")
st.markdown("---")

# --- 2. API KONTROLÜ ---
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    # Hem secrets hem environment kontrolü yapması için esneklik
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    except:
        st.error("🚨 API Anahtarı eksik!")
        st.stop()

# Model ismini güncelledim (2.0-flash en hızlısıdır)
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:streamGenerateContent?key={API_KEY}"

# --- 3. SOHBET MANTIĞI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. GİRİŞ VE CEVAP ---
if user_input := st.chat_input("Bir mesaj yaz..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        cevap_kutusu = st.empty()
        tam_cevap = ""
        
        system_instruction = (
            "Sen Ahmet İRİŞ'in dijital asistanısın. Hem ciddi hem samimi bir ton kullan. "
            "Aşırı samimi hitaplardan kaçın. Profesyonel ve içten bir tutum sergile."
        )
        
        contents = [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages]
        data = {"contents": contents, "system_instruction": {"parts": [{"text": system_instruction}]}}

        try:
            response = requests.post(URL, json=data, stream=True)
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        json_str = decoded[6:]
                        try:
                            json_data = json.loads(json_str)
                            chunk = json_data['candidates'][0]['content']['parts'][0]['text']
                            tam_cevap += chunk
                            cevap_kutusu.markdown(tam_cevap)
                        except:
                            continue
            st.session_state.messages.append({"role": "assistant", "content": tam_cevap})
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
