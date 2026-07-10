import streamlit as st
import requests

# --- ARAYÜZ ---
st.set_page_config(page_title="Yapay Zeka Asistanı", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("By Ahmet İRİŞ")

# --- API AYARLARI ---
# Not: Manage Secrets kısmında anahtarının isminin GEMINI_API_KEY kalmasında bir sakınca yok, 
# ama istersen FLATKEY_API_KEY olarak değiştirebilirsin.
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 API Anahtarı 'Manage Secrets' kısmında tanımlanmamış!")
    st.stop()

# Flatkey için OpenAI uyumlu URL ve Model
URL = "https://api.flatkey.ai/v1/chat/completions"
MODEL = "gpt-4o" # Flatkey'in sunduğu modellerden birini buraya yazabilirsin

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
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        # OpenAI formatında mesaj gönderimi
        payload = {
            "model": MODEL,
            "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        }
        
        try:
            response = requests.post(URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                answer = response.json()['choices'][0]['message']['content']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Hata Kodu: {response.status_code}")
                st.write(response.text)
        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")
