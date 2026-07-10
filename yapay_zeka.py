import streamlit as st
import requests
import json

st.set_page_config(page_title="Web Tabanlı Yapay Zeka", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("By Ahmet İRİŞ")

# Secrets kontrolü
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("API Anahtarı bulunamadı! Manage Secrets kısmından ekle.")
    st.stop()

URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:streamGenerateContent?key={API_KEY}"

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        cevap_kutusu = st.empty()
        full_response = ""
        
        contents = [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages]
        payload = {"contents": contents}

        try:
            response = requests.post(URL, json=payload, stream=True)
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        data = json.loads(decoded[6:])
                        if 'candidates' in data:
                            chunk = data['candidates'][0]['content']['parts'][0]['text']
                            full_response += chunk
                            cevap_kutusu.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Hata: {e}")
