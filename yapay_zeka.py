import streamlit as st
import requests
import base64
from duckduckgo_search import DDGS
from datetime import datetime
from gtts import gTTS
import os

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Ahmet İRİŞ Asistanı", page_icon="🤖", layout="wide")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("By Ahmet İRİŞ - 2026 Gelişmiş Mühendislik Modu")

# --- API AYARLARI ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 API Anahtarı tanımlanmamış!")
    st.stop()

URL = "https://router.flatkey.ai/v1/chat/completions"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- KAYDIRMA SORUNUNU ÇÖZEN FRAGMENT ---
@st.fragment
def render_chat():
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                if st.button("🔊 Sesli Oku", key=f"audio_{i}"):
                    tts = gTTS(text=message["content"], lang='tr')
                    tts.save(f"cevap_{i}.mp3")
                    st.audio(f"cevap_{i}.mp3")

render_chat()

# --- GİRİŞ PANELİ ---
col1, col2 = st.columns([0.85, 0.15])
with col1:
    prompt = st.chat_input("Mesajını yaz...")
with col2:
    uploaded_file = st.file_uploader("Dosya", type=['txt', 'md', 'jpg', 'jpeg', 'png'], label_visibility="collapsed")

# --- MANTIK ---
if prompt:
    # 1. Dosya İşleme
    image_data = None
    text_content = ""
    if uploaded_file:
        if uploaded_file.type.startswith('image'):
            image_data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        else:
            text_content = uploaded_file.read().decode("utf-8")

    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Hazırlıklar
    search_instruction = ""
    if any(w in prompt.lower() for w in ["ara", "güncel", "yeni", "modlar"]):
        try:
            results = DDGS().text(f"{prompt} 2026", max_results=2)
            search_instruction = f"\n\n[GÜNCEL VERİ]: {', '.join([r['body'] for r in results])}"
        except: pass

    # GELİŞMİŞ SİSTEM TALİMATI VE KONU DIŞINA ÇIKMAMA KURALI
    system_instructions = (
        "Sen Ahmet İRİŞ tarafından tasarlanmış, ileri düzey bir mühendislik asistanısın. "
        "KURALLAR: "
        "1. Sadece yazılım, donanım, elektronik ve teknik konularda cevap ver. "
        "2. Konu dışı (magazin, siyaset, gereksiz geyik vb.) sorular gelirse: 'Bu konu uzmanlık alanım dışındadır, teknik bir soruna odaklanalım.' diyerek konuyu kapat. "
        "3. Teknik analiz yaparken önce mantığını açıkla, sonra çözüm üret. "
        "4. Asla 'bilmiyorum' deme, en mantıklı mühendislik çıkarımını yap."
    )

    # 3. API İsteği (Zekayı genişleten sıcaklık ve token ayarı)
    full_messages = [{"role": "system", "content": system_instructions}]
    for msg in st.session_state.messages[:-1]:
        full_messages.append({"role": msg["role"], "content": msg["content"]})
    
    current_content = [{"type": "text", "text": prompt + search_instruction + f"\nDosya: {text_content}"}]
    if image_data:
        current_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})
    
    full_messages.append({"role": "user", "content": current_content})

    try:
        response = requests.post(URL, headers=headers, json={
            "model": "gpt-4o", 
            "messages": full_messages,
            "temperature": 0.2, # Zekayı odaklanmış ve kesin yapar
            "max_tokens": 4096  # Detaylı açıklamalar için geniş alan
        })
        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
    except Exception as e:
        st.error(f"Hata: {e}")
