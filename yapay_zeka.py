import streamlit as st
import requests
import json

st.set_page_config(page_title="Hata Ayıklama", page_icon="🔍")
st.title("Debug Modu")

# 1. Anahtarın yüklenip yüklenmediğini kontrol et
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    st.success("API Anahtarı başarıyla okundu.")
except Exception as e:
    st.error(f"Secrets dosyası bulunamadı! Hata: {e}")
    st.stop()

# 2. Test butonu (Kodun çalışıp çalışmadığını anlamak için)
if st.button("API Bağlantısını Test Et"):
    URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": "Merhaba"}]}]}
    
    try:
        response = requests.post(URL, json=payload)
        st.write(f"Durum Kodu: {response.status_code}")
        st.write(f"Yanıt: {response.text}")
    except Exception as e:
        st.error(f"Bağlantı hatası: {e}")

# ... (gerisi aynı)
