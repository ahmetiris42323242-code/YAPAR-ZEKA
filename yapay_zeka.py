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

# 2026 güncel uç noktası
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
        # Mesaj geçmişini hazırlayalım
        history = []
        for m in st.session_state.messages:
            role = "user" if m["role"] == "user" else "model"
            history.append({"role": role, "parts": [{"text": m["content"]}]})
            
        payload = {"contents": history}
        
        try:
            # POST isteği
            response = requests.post(URL, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                answer = result['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                # 404 veya başka bir hata gelirse burada tam olarak ne yazdığını göreceğiz
                st.error(f"Hata Kodu: {response.status_code}")
                st.write(f"Detay: {response.text}")
                
        except Exception as e:
            st.error(f"Sistem Hatası: {e}")
