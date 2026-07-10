import streamlit as st
import requests
import json

# --- ARAYÜZ ---
st.set_page_config(page_title="Web Tabanlı Yapay Zeka", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("By Ahmet İRİŞ")

# --- API AYARLARI ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("API Anahtarı bulunamadı!")
    st.stop()

# 2026 Güncel URL Yapısı
# 'models/gemini-1.5-flash' şeklinde kullanıyoruz
MODEL = "gemini-1.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Bir mesaj yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        history = [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages]
        payload = {"contents": history}
        
        try:
            response = requests.post(URL, headers={'Content-Type': 'application/json'}, json=payload)
            
            if response.status_code == 200:
                answer = response.json()['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Hata Kodu: {response.status_code}")
                st.code(response.text) # Hata detayını kod bloğunda göster
                
        except Exception as e:
            st.error(f"Sistem Hatası: {e}")
