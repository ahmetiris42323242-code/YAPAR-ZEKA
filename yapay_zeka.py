import streamlit as st
import requests

# --- ARAYÜZ ---
st.set_page_config(page_title="Ahmet İRİŞ Asistanı", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("By Ahmet İRİŞ")

# --- API AYARLARI ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 API Anahtarı 'Manage Secrets' kısmında tanımlanmamış!")
    st.stop()

# Flatkey Router URL
URL = "https://router.flatkey.ai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# --- SOHBET ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesaj geçmişini ekranda göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Mesajını yaz..."):
    # Kullanıcı mesajını ekle ve göster
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Sistem talimatları (Kişilik ve kimlik)
        system_instructions = (
            "Sen Ahmet İRİŞ tarafından insanlara yardım etmek için tasarlanmış bir yapay zeka asistanısın. "
            "Sana 'kimsin' veya 'kurucun kim' diye sorulduğunda, Ahmet İRİŞ tarafından insanlara yardım etmek "
            "için tasarlandığını belirt. "
            "Eğer sana 'Çağın'ı tanıyor musun?' diye sorulursa, tam olarak şu cevabı ver: "
            "'O sırada Çağın aga, ben ne alaka ya ha ha ha!'"
        )

        # Mesajları hazırla
        messages = [{"role": "system", "content": system_instructions}]
        for m in st.session_state.messages:
            messages.append({"role": m["role"], "content": m["content"]})
            
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
