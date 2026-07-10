import streamlit as st
import requests

# --- ARAYÜZ ---
st.set_page_config(page_title="Yapay Zeka Asistanı", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("By Ahmet İRİŞ")

# --- API AYARLARI ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 API Anahtarı 'Manage Secrets' kısmında tanımlanmamış!")
    st.stop()

# Listeden onayladığımız model ismi
MODEL = "gemini-2.0-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

# --- SOHBET ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Mesaj geçmişini API'ye uygun formata getir
        history = []
        for m in st.session_state.messages:
            role = "user" if m["role"] == "user" else "model"
            history.append({"role": role, "parts": [{"text": m["content"]}]})
            
        payload = {"contents": history}
        
        try:
            response = requests.post(URL, json=payload)
            
            if response.status_code == 200:
                answer = response.json()['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Hata Kodu: {response.status_code}")
                st.write(response.json())
        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")
