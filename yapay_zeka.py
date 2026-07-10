import streamlit as st
import requests
from duckduckgo_search import DDGS

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

# --- SOHBET ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. HIZLI ARAMA (Sadece gerekli durumlarda tetiklenir)
        search_instruction = ""
        if any(word in prompt.lower() for word in ["ara", "güncel", "yeni", "modlar", "liste"]):
            with st.spinner("2026 verileri taranıyor..."):
                try:
                    results = DDGS().text(f"{prompt} 2026", max_results=3)
                    search_summary = "\n".join([f"- {r['body']}" for r in results])
                    search_instruction = f"\n\n[GÜNCEL VERİLER]: {search_summary}\n\nTalimat: Sadece 2025-2026 verilerini kullan."
                except:
                    pass

        # 2. KİMLİK VE KURALLAR (Sistem Talimatı)
        system_instructions = (
            "Sen Ahmet İRİŞ tarafından tasarlanmış bir asistanısın. "
            "Sana 'kimsin' veya 'kurucun kim' diye sorulduğunda Ahmet İRİŞ tarafından tasarlandığını belirt. "
            "Eğer 'Çağın'ı tanıyor musun?' diye sorulursa: 'O sırada Çağın aga, ben ne alaka ya ha ha ha!' de. "
            "Her zaman yardımcı, güncel ve esprili bir dil kullan."
        )

        # 3. MESAJLARI BİRLEŞTİR
        messages = [{"role": "system", "content": system_instructions}]
        messages.extend(st.session_state.messages[:-1]) # Önceki sohbet geçmişi
        messages.append({"role": "user", "content": prompt + search_instruction}) # Güncel soru + arama
            
        try:
            response = requests.post(URL, headers=headers, json={"model": "gpt-4o", "messages": messages})
            if response.status_code == 200:
                answer = response.json()['choices'][0]['message']['content']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error("API Bağlantı Hatası!")
        except Exception as e:
            st.error(f"Hata: {e}")
