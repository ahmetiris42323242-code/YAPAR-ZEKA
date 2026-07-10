import streamlit as st
import requests
from duckduckgo_search import DDGS
from datetime import datetime
from gtts import gTTS
import os

# --- ARAYÜZ ---
st.set_page_config(page_title="Ahmet İRİŞ Asistanı", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("By Ahmet İRİŞ - 2026 Güncel Veri Destekli")

# --- API AYARLARI ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 API Anahtarı tanımlanmamış!")
    st.stop()

URL = "https://router.flatkey.ai/v1/chat/completions"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# --- DOSYA YÜKLEME ---
uploaded_file = st.sidebar.file_uploader("Bir dosya yükle (TXT, MD)", type=['txt', 'md'])
file_content = ""
if uploaded_file:
    file_content = uploaded_file.read().decode("utf-8")
    st.sidebar.success("Dosya başarıyla yüklendi!")

# --- SOHBET ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            if st.button("🔊 Sesli Oku", key=f"audio_{i}"):
                tts = gTTS(text=message["content"], lang='tr')
                tts.save(f"cevap_{i}.mp3")
                st.audio(f"cevap_{i}.mp3")

if prompt := st.chat_input("Mesajını yaz..."):
    # Dosya içeriğini prompt'a ekle
    context_prompt = f"{prompt}\n\n[YÜKLENEN DOSYA İÇERİĞİ]: {file_content}" if file_content else prompt
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # ARAMA VE KURALLAR
        system_instructions = (
            f"Sen Ahmet İRİŞ tarafından tasarlanmış bir asistansın. Bugünün tarihi: {datetime.now().strftime('%d %B %Y')}. "
            "Sana bir dosya içeriği verilirse, bu dosyayı analiz et ve özetle. "
            "Eğer 'Çağın'ı tanıyor musun?' diye sorulursa: 'O sırada Çağın aga, ben ne alaka ya ha ha ha!' de. "
            "Eğer 'Abdurami'yi tanıyor musun?' diye sorulursa: 'Aponuza boydan gireyim böhöhöhöyt!' de."
        )

        messages = [{"role": "system", "content": system_instructions}]
        messages.extend(st.session_state.messages[:-1]) 
        messages.append({"role": "user", "content": context_prompt})
            
        try:
            response = requests.post(URL, headers=headers, json={"model": "gpt-4o", "messages": messages})
            if response.status_code == 200:
                answer = response.json()['choices'][0]['message']['content']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
            else:
                st.error("API Bağlantı Hatası!")
        except Exception as e:
            st.error(f"Hata: {e}")
    
