import streamlit as st
import requests
import os

# Sayfa Yapılandırması
st.set_page_config(page_title="Asistan", page_icon="🤖")
st.title("🤖 Asistan")

# API Anahtarını Buraya Yaz (Test için en garanti yöntem)
API_KEY = "AQ.Ab8RN6Kq87IwiYXisNn3k8f_gijyBuxm8iL4Xn0jSFRpSoPb1A" 

# Mesaj geçmişini koruma
if "messages" not in st.session_state:
    st.session_state.messages = []

# Geçmiş mesajları ekranda tut
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı giriş alanı
if prompt := st.chat_input("Mesajını yaz..."):
    # 1. Kullanıcı mesajını anında göster
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. API İstek Bölümü (Sadece bu kısım hata alabilir)
    with st.chat_message("assistant"):
        cevap_kutusu = st.empty()
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:streamGenerateContent?key={API_KEY}"
            payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
            
            response = requests.post(url, json=payload, stream=True)
            
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        decoded = line.decode('utf-8')
                        if '"text":' in decoded:
                            chunk = decoded.split('"text":')[1].strip().strip('"').replace('\\n', '\n')
                            full_response += chunk
                            cevap_kutusu.markdown(full_response + "▌")
                
                cevap_kutusu.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            elif response.status_code == 429:
                st.error("🚨 HATA 429: Çok fazla istek gönderildi. Lütfen 1 dakika bekleyip tekrar dene.")
            else:
                st.error(f"Hata kodu: {response.status_code}")
                
        except Exception as e:
            st.error(f"Bağlantı hatası: {e}")
