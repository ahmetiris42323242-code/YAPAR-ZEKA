import streamlit as st
import requests
import base64
import asyncio
import edge_tts  # Yeni kütüphanemiz
from duckduckgo_search import DDGS

# --- ARAYÜZ ---
st.set_page_config(page_title="Apolingo Asistanı", page_icon="🚀", layout="wide")
st.title("🚀 APOLINGO EVRENSEL ULTRA COSTA YAPAY ZEKA")
st.caption("Kurucular: Ahmet İRİŞ & Abduramim İRİŞ | 2026 Güncel Yapay Zeka")

# API AYARLARI
API_KEY = st.secrets["GEMINI_API_KEY"]
URL = "https://router.flatkey.ai/v1/chat/completions"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- EDGE-TTS İLE DOĞAL SESLENDİRME ---
async def seslendir(text, i):
    # 'tr-TR-AhmetNeural' sesi, benim konuştuğum ses tonuna en yakın olanlardan biridir
    voice = "tr-TR-AhmetNeural" 
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(f"cevap_{i}.mp3")

# --- KAYDIRMA SORUNUNU ÇÖZEN FRAGMENT ---
@st.fragment
def render_chat():
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                if st.button("🔊 Doğal Sesle Oku", key=f"audio_{i}"):
                    # Async işlemi senkron çalıştırmak için
                    asyncio.run(seslendir(message["content"], i))
                    st.audio(f"cevap_{i}.mp3")

render_chat()

# --- GİRİŞ VE MANTIK (Aynı şekilde kalıyor) ---
col1, col2 = st.columns([0.85, 0.15])
with col1:
    prompt = st.chat_input("Selamün aleyküm gardaşşşşş! Sorunu gönder, stüdyoyu patlat...")
with col2:
    uploaded_file = st.file_uploader("Dosya", type=['txt', 'md', 'jpg', 'jpeg', 'png'], label_visibility="collapsed")

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

    # 2. SİSTEM TALİMATI
    system_instructions = (
        "Sen Apolingo tarafından geliştirilmiş, dünyanın en uzun ve en detaylı cevaplarını veren bir asistansın. "
        "Kurucuların AHMET İRİŞ ve ABDURAMİM İRİŞ'tir. "
        "Her cümlende 'gardaşşşşş' kelimesini kullan. "
        "Ahmet sorulursa 'ÇİŞLİİİİ AHMETTT HAHAHAHA 🤣💨' de. "
        "Teknoloji, oyun, moda konularında çok detaylı ve mizahi bilgiler ver."
    )

    # 3. API İSTEĞİ (Geçmişi hatırlayan yapı)
    full_messages = [{"role": "system", "content": system_instructions}]
    for msg in st.session_state.messages[:-1]:
        full_messages.append({"role": msg["role"], "content": msg["content"]})
    
    current_content = [{"type": "text", "text": prompt + f"\nDosya: {text_content}"}]
    if image_data:
        current_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})
    
    full_messages.append({"role": "user", "content": current_content})

    try:
        response = requests.post(URL, headers=headers, json={"model": "gpt-4o", "messages": full_messages})
        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
    except Exception as e:
        st.error(f"Hata: {e}")
