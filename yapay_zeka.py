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
        # İnternet Araması Yeteneği
        with st.spinner("Bilgi toplanıyor..."):
            try:
                # DDGS ile arama yap
                search_results = DDGS().text(prompt, max_results=3)
                results_text = "\n\n".join([f"- {r['body']}" for r in search_results])
                
                # Talimatlara arama sonuçlarını da ekle
                context_prompt = f"İşte 2026 yılından güncel internet arama sonuçları:\n{results_text}\n\nBu bilgilere dayanarak kullanıcının sorusunu yanıtla."
            except Exception as e:
                context_prompt = "Arama yapılamadı, genel bilginle cevap ver."

        system_instructions = (
            "Sen Ahmet İRİŞ tarafından insanlara yardım etmek için tasarlanmış bir yapay zeka asistanısın. "
            "Sana 'kimsin' veya 'kurucun kim' diye sorulduğunda, Ahmet İRİŞ tarafından insanlara yardım etmek "
            "için tasarlandığını belirt. "
            "Eğer sana 'Çağın'ı tanıyor musun?' diye sorulursa, tam olarak şu cevabı ver: "
            "'O sırada Çağın aga, ben ne alaka ya ha ha ha!'"
        )

        messages = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": context_prompt + "\n\nKullanıcı sorusu: " + prompt}
        ]
            
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
                st.error(f"Hata Kodu: {response.status_code}")
                st.write(response.json())
        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")
