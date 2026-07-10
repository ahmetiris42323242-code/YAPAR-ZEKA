import streamlit as st
import requests

st.title("Model Keşif Aracı")
API_KEY = st.secrets["GEMINI_API_KEY"]

# Google'ın tüm modelleri listeleyen uç noktası
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

if st.button("Kullanılabilir Modelleri Listele"):
    response = requests.get(url)
    if response.status_code == 200:
        st.write(response.json())
    else:
        st.error(f"Hata: {response.text}")
