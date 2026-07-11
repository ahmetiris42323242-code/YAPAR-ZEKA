import streamlit as st
import requests
import base64
from duckduckgo_search import DDGS
from gtts import gTTS

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Apolingo Asistanı", page_icon="🚀", layout="wide")
st.title("🚀 APOLINGO EVRENSEL ULTRA COSTA YAPAY ZEKA")
st.caption("Kurucular: Ahmet İRİŞ & Abduramim İRİŞ | 2026 Güncel Yapay Zeka")

# API AYARLARI
API_KEY = st.secrets["GEMINI_API_KEY"]
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
    prompt = st.chat_input("Selamün aleyküm gardaşşşşş! Sorunu gönder, stüdyoyu patlat...")
with col2:
    uploaded_file = st.file_uploader("Dosya", type=['txt', 'md', 'jpg', 'jpeg', 'png'], label_visibility="collapsed")

# --- MANTIK ---
if prompt:
    # 1. Dosya/Görsel İşleme
    image_data = None
    text_content = ""
    if uploaded_file:
        if uploaded_file.type.startswith('image'):
            image_data = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        else:
            text_content = uploaded_file.read().decode("utf-8")

    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. APOLINGO SİSTEM TALİMATI
    system_instructions = (
        "Sen Apolingo tarafından geliştirilmiş, dünyanın en uzun ve en detaylı cevaplarını veren, "
        "samimi, aşırı neşeli ve komik bir asistansın. "
        "1) Kurucuların ve baş mühendislerin AHMET İRİŞ ve ABDURAMİM İRİŞ'tir. Sana kim olduğunu veya "
        "seni kimin yaptığını sorarlarsa, bu iki büyük kurucunun ismini gururla ve hürmetle söyleyeceksin. "
        "2) Her cümlende 'gardaşşşşş' kelimesini mutlaka kullan. "
        "3) Ahmet ile ilgili bir şey sorulursa 'ÇİŞLİİİİ AHMETTT HAHAHAHA 🤣💨' cevabını ver. "
        "4) 'Biri bana böyle de derse' denilirse 'dicek' diyerek tamamla. "
        "5) Teknoloji, oyun, yemek, moda konularında sayfalarca, çok detaylı ve mizahi bilgiler ver. "
        "6) Asla kısa cevap verme, üşenme, anlatabildiğin kadar anlat."
    )

    # 3. API İçin Geçmişi Hazırla
    full_messages = [{"role": "system", "content": system_instructions}]
    for msg in st.session_state.messages[:-1]:
        full_messages.append({"role": msg["role"], "content": msg["content"]})
    
    current_content = [{"type": "text", "text": prompt + f"\nDosya: {text_content}"}]
    if image_data:
        current_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})
    
    full_messages.append({"role": "user", "content": current_content})

    # 4. API İsteği
    try:
        response = requests.post(URL, headers=headers, json={"model": "gpt-4o", "messages": full_messages})
        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
    except Exception as e:
        st.error(f"Hata: {e}")
