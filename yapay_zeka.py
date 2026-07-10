import streamlit as st
import requests
import base64
from duckduckgo_search import DDGS
from datetime import datetime
from gtts import gTTS
import os

# --- KAYDIRMA SORUNUNU ÇÖZEN HİLE ---
st.markdown("""
    <script>
        var scroll_pos = 0;
        window.onscroll = function() {scroll_pos = window.scrollY;};
        window.onload = function() {window.scrollTo(0, scroll_pos);};
    </script>
""", unsafe_allow_html=True)

# --- SENİN ARAYÜZÜN ---
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
    # (Senin mevcut mantığın burada aynı kalıyor)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. HIZLI ARAMA
        search_instruction = ""
        keywords = ["ara", "güncel", "yeni", "modlar", "liste", "neler oldu", "tarih"]
        
        if any(word in prompt.lower() for word in keywords):
            with st.spinner("2026 verileri taranıyor..."):
                try:
                    results = DDGS().text(f"{prompt} 2026", max_results=3)
                    search_summary = "\n".join([f"- {r['body']}" for r in results])
                    search_instruction = f"\n\n[GÜNCEL VERİLER]: {search_summary}"
                except:
                    pass

        # 2. KİMLİK VE KURALLAR
        current_date = datetime.now().strftime("%d %B %Y")
        system_instructions = (
            f"Sen Ahmet İRİŞ tarafından tasarlanmış bir asistansın. Bugünün tarihi: {current_date}. "
            "Asla 2023 yılında olduğunu iddia etme, 2026 yılındasın. "
            "Eğer 'Çağın'ı tanıyor musun?' diye sorulursa: 'O sırada Çağın aga, ben ne alaka ya ha ha ha!' de. "
            "Eğer 'Abdurami'yi tanıyor musun?' diye sorulursa: 'Aponuza boydan gireyim böhöhöhöyt!' de."
        )

        messages = [{"role": "system", "content": system_instructions}]
        messages.extend(st.session_state.messages[:-1]) 
        messages.append({"role": "user", "content": prompt + search_instruction})
            
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
                    
