import streamlit as st
import requests
import json
import os

st.set_page_config(page_title="Ahmet Asistan", page_icon="🤖")

# API Anahtarı Ayarı
API_KEY = os.environ.get("GEMINI_API_KEY")

st.title("🤖 Asistan")

# Sohbet geçmişini sakla
if "messages" not in st.session_state:
    st.session_state.messages = []

# Geçmişi ekrana bas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı mesajı
if prompt := st.chat_input("Mesajını yaz..."):
    # Mesajı anında ekrana ekle (API cevabını beklemeden)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # API İstek Hazırlığı
    with st.chat_message("assistant"):
        cevap_kutusu = st.empty()
        
        # Hata yönetimi ile API isteği
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:streamGenerateContent?key={API_KEY}"
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}]
            }
            
            response = requests.post(url, json=payload, stream=True)
            
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        # Gelen veriyi işle
                        decoded = line.decode('utf-8')
                        if '"text":' in decoded:
                            chunk = decoded.split('"text":')[1].strip().strip('"').replace('\\n', '\n')
                            full_response += chunk
                            cevap_kutusu.markdown(full_response + "▌")
                cevap_kutusu.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            elif response.status_code == 429:
                st.error("🚨 Google API limiti doldu! Lütfen 1 dakika bekleyip tekrar dene.")
            else:
                st.error(f"Hata kodu: {response.status_code}")
                
        except Exception as e:
            st.error(f"Bağlantı sorunu: {str(e)}")
