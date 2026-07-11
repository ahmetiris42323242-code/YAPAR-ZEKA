import streamlit as st
import requests
import base64
from duckduckgo_search import DDGS
from gtts import gTTS
import os

# --- KONUM TESPİTİ ---
def get_user_location():
    try:
        # IP tabanlı konum servisi
        res = requests.get('https://ipinfo.io/')
        data = res.json()
        city = data.get('city', 'İstanbul')
        region = data.get('region', 'Türkiye')
        return f"{city}, {region}"
    except:
        return "Türkiye"

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Ahmet İRİŞ Asistanı", page_icon="🤖", layout="wide")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")

# --- GELİŞTİRİCİ PANELİ ---
if "is_dev_mode" not in st.session_state:
    st.session_state.is_dev_mode = False

with st.sidebar:
    st.subheader("⚙️ Geliştirici Paneli")
    if st.text_input("Şifre", type="password") == "7536":
        st.session_state.is_dev_mode = True
        st.success("SÜPER ZEKA AKTİF")

# --- SOHBET MANTIĞI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if st.button(f"🔊 Dinle", key=f"audio_{i}"):
                gTTS(text=msg["content"], lang='tr').save("cevap.mp3")
                st.audio("cevap.mp3")

if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # KONUM VE ARAMA ENTEGRASYONU
    user_loc = get_user_location()
    search_query = f"{prompt} konum: {user_loc}"
    
    search_results = ""
    try:
        with DDGS() as ddgs:
            # Köfteci vb. aramalar için yerel bazlı sorgu
            results = list(ddgs.text(search_query, max_results=3))
            search_results = f"\n\nKonum: {user_loc}. İnternet sonuçları: {results}"
    except:
        pass

    # MODEL SEÇİMİ
    if st.session_state.is_dev_mode:
        model_name, temp = "gpt-4o", 0.05
    else:
        model_name, temp = "gpt-4o-mini", 0.7
    
    headers = {"Authorization": f"Bearer {st.secrets['GEMINI_API_KEY']}", "Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "messages": [{"role": "system", "content": f"Sen {user_loc} bölgesindeki en iyi mekanları bilen bir asistansın."}] + 
                    st.session_state.messages + [{"role": "system", "content": search_results}],
        "temperature": temp
    }
    
    response = requests.post("https://router.flatkey.ai/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        answer = response.json()['choices'][0]['message']['content']
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()
        
