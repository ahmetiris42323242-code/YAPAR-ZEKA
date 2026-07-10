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
        # İnternet Araması (2026 Odaklı)
        with st.spinner("2026 verileri analiz ediliyor..."):
            try:
                # Sorguyu 2026'ya sabitledik
                search_query = f"{prompt} best 2026 horror mods popular"
                results = DDGS().text(search_query, max_results=5)
                search_summary = "\n".join([f"- {r['body']}" for r in results])
                
                search_instruction = (
                    f"\n\n[GÜNCEL VERİLER 2026]: {search_summary}\n\n"
                    "ÖNEMLİ TALİMAT: Eski modları (2020 öncesi) kesinlikle listeleme. "
                    "Sadece 2025-2026 yılında popüler olan veya güncellenen içerikleri öner."
                )
            except:
                search_instruction = ""

        # Kimlik ve Kesin Kurallar
        system_instructions = (
            "Sen Ahmet İRİŞ tarafından tasarlanmış, 2026 yılı güncel verilerine erişimi olan bir yapay zeka asistanısın. "
            "Görevin her zaman en güncel (2025-2026) bilgileri sunmaktır. Eski modları veya bilgileri 'erişimim yok' "
            "demeden doğrudan filtrele ve en yenilerini bul. "
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
