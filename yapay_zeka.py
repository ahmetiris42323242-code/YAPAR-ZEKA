import streamlit as st
from groq import Groq

# 1. Sayfa Ayarları (SEO ve Arayüz)
st.set_page_config(page_title="Web Tabanlı Yapay Zeka", page_icon="🤖", layout="centered")

# Başlık ve İmza Kısmı
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("Ahmet İRİŞ tarafından yapılmıştır")
st.markdown("---")

# 2. API Bağlantısı (Secrets'tan)
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("API anahtarı bulunamadı! Lütfen ayarlardan tanımla.")
    st.stop()

# 3. Sohbet Geçmişi
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Mesajları Ekrana Bas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Girdi İşleme
if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            system_prompt = (
                "Sen Ahmet İRİŞ'in en yakın kankasısın. "
                "Cevapların kısa, samimi, Türkçe ve mutlaka emojili olsun. "
                "ASLA soru sorma, ASLA fiziksel eylem uydurma."
            )
            
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
                stream=True
            )
            
            full_response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Hata: {e}")
