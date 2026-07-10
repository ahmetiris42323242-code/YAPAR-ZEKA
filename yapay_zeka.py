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
    st.error("🚨 API Anahtarı 'Manage Secrets' kısmında tanımlanmamış!")
    st.stop()

URL = "https://router.flatkey.ai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

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
        # İnternet Araması
        with st.spinner("İnterneti tarıyorum..."):
            try:
                results = DDGS().text(prompt, max_results=3)
                search_summary = "\n".join([f"- {r['body']}" for r in results])
                search_instruction = f"\n\n[GÜNCEL VERİLER]: {search_summary}\n\nBu verileri kullanarak soruyu cevapla."
            except:
                search_instruction = ""

        # Kimlik ve Kurallar
        system_instructions = (
            "Sen Ahmet İRİŞ tarafından insanlara yardım etmek için tasarlanmış bir yapay zeka asistanısın. "
            "İnternete erişim yetkin var ve 2026 yılı güncel verilerini kullanabilirsin. "
            "Sana 'kimsin' veya 'kurucun kim' diye sorulduğunda, Ahmet İRİŞ tarafından tasarlandığını belirt. "
            "Eğer 'Çağın'ı tanıyor musun?' diye sorulursa: 'O sırada Çağın aga, ben ne alaka ya ha ha ha!' de."
        )

        messages = [{"role": "system", "content": system_instructions}]
        
        # Geçmişi ekle
        for m in st.session_state.messages[:-1]:
            messages.append({"role": m["role"], "content": m["content"]})
            
        # Güncel prompt ve arama sonucu
        messages.append({"role": "user", "content": prompt + search_instruction})
            
        payload = {
            "model": "gpt-4o",
            "messages": messages
        }
        
        try:
            response = requests.post(URL, headers=headers, json=payload)
            if response.status_code == 200:
                answer = response.json()['choices'][0]['message']['content']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error("Bir hata oluştu, lütfen tekrar dene.")
        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")
