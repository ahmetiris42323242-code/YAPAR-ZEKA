import streamlit as st
import google.generativeai as genai

# Sayfa Ayarları
st.set_page_config(page_title="Herkes İçin Yapay Zeka", page_icon="🤖", layout="centered")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")

# API Bağlantısı (Secrets üzerinden güvenli çekiyoruz)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"API anahtarı bulunamadı! Lütfen Streamlit ayarlarından GEMINI_API_KEY'i doğru eklediğinden emin ol. Hata: {e}")

# Sohbet Geçmişi
if "messages" not in st.session_state:
    st.session_state.messages = []

# Asistan Yönetim Paneli
with st.sidebar:
    if st.button("Sohbet Geçmişini Temizle 🧹"):
        st.session_state.messages = []
        st.rerun()

# Mesajları Ekrana Yaz
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Giriş İşleme
if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            system_instruction = (
                "Sen Ahmet İRİŞ tarafından geliştirilmiş; samimi, zeki ve kanka ruhlu bir asistansın. "
                "Asla hayali geçmiş konular açma, asla kaba olma, sadece kullanıcıya odaklan."
            )
            
            model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction)
            
            gemini_history = []
            for msg in st.session_state.messages[:-1]:
                role = "model" if msg["role"] == "assistant" else "user"
                gemini_history.append({"role": role, "parts": [msg["content"]]})
            
            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(prompt)
            
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            message_placeholder.markdown(f"❌ Bir hata oluştu: `{e}`")
            
