import streamlit as st
import requests
import base64
from duckduckgo_search import DDGS
from datetime import datetime
from gtts import gTTS
import os

# --- ARAYÜZ ---
st.set_page_config(page_title="Ahmet İRİŞ Asistanı", page_icon="🤖", layout="wide")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("By Ahmet İRİŞ - 2026 Güncel Veri & Kod Uzmanı")

# --- API AYARLARI ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 API Anahtarı bulunamadı!")
    st.stop()

URL = "https://router.flatkey.ai/v1/chat/completions"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SOHBET GEÇMİŞİ ---
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            if st.button("🔊 Sesli Oku", key=f"audio_{i}"):
                tts = gTTS(text=message["content"], lang='tr')
                tts.save(f"temp_{i}.mp3")
                st.audio(f"temp_{i}.mp3")

# --- GİRİŞ PANELİ ---
col_input, col_file = st.columns([0.85, 0.15])
with col_input:
    prompt = st.chat_input("Mesajını yaz veya kod sorununu sor...")
with col_file:
    uploaded_file = st.file_uploader("Dosya", type=['txt', 'md', 'jpg', 'jpeg', 'png'], label_visibility="collapsed")

# Dosya/Görsel İşleme
image_data = None
text_content = ""
if uploaded_file:
    if uploaded_file.type.startswith('image'):
        image_data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        st.toast("Görsel yüklendi!")
    else:
        text_content = uploaded_file.read().decode("utf-8")
        st.toast("Dosya içeriği okundu!")

# --- CEVAPLAMA ---
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. ARAMA
        search_instruction = ""
        if any(w in prompt.lower() for w in ["ara", "güncel", "yeni", "modlar", "liste"]):
            try:
                results = DDGS().text(f"{prompt} 2026", max_results=2)
                search_instruction = f"\n\n[GÜNCEL VERİ]: {', '.join([r['body'] for r in results])}"
            except: pass

        # 2. SİSTEM TALİMATLARI (KOD UZMANI MODU)
        system_instructions = (
            f"Sen Ahmet İRİŞ tarafından tasarlanmış, tüm kod dillerine (C++, Python, Lua, JS, Arduino vb.) "
            "hakim uzman bir yazılımcısın. 2026 yılındasın. Bir kod sorulursa temiz bloklarla açıkla ve "
            "hata varsa 'Adım Adım Çözüm' üret. "
            "Eğer 'Çağın'ı tanıyor musun?' diye sorulursa: 'O sırada Çağın aga, ben ne alaka ya ha ha ha!' de. "
            "Eğer 'Abdurami'yi tanıyor musun?' diye sorulursa: 'Aponuza boydan gireyim böhöhöhöyt!' de."
        )

        # 3. İÇERİK HAZIRLAMA
        msg_content = [{"type": "text", "text": prompt + search_instruction + f"\nDosya: {text_content}"}]
        if image_data:
            msg_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})

        # 4. API İSTEĞİ
        try:
            response = requests.post(URL, headers=headers, json={
                "model": "gpt-4o", 
                "messages": [{"role": "system", "content": system_instructions}, {"role": "user", "content": msg_content}]
            })
            if response.status_code == 200:
                answer = response.json()['choices'][0]['message']['content']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
            else:
                st.error("API Hatası!")
        except Exception as e:
            st.error(f"Hata: {e}")
    
