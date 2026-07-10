import streamlit as st
from groq import Groq
from googletrans import Translator

# 1. Sayfa Ayarları
st.set_page_config(page_title="Ahmet İRİŞ - Çevirili Yapay Zeka", page_icon="🤖", layout="centered")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("Ahmet İRİŞ tarafından yapılmıştır")

# Çeviriciyi başlat
translator = Translator()

# 2. Bağlantı Ayarları
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"API Bağlantı hatası: {e}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Yan Panel
with st.sidebar:
    if st.button("Sohbeti Temizle 🧹"):
        st.session_state.messages = []
        st.rerun()

# 4. Mesajları Yazdır
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Girdi ve İşleme
if prompt := st.chat_input("Bir şeyler yaz kanka..."):
    # Önce Türkçeyi İngilizceye çevir (Model İngilizce daha iyi çalışır)
    translated_prompt = translator.translate(prompt, src='tr', dest='en').text
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Sistem talimatı (İngilizce olarak veriyoruz ki tam anlasın)
            system_instruction = "You are a friendly friend. Respond in English, keep it conversational, and never mention personal physical activities."

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": translated_prompt}
                ],
                stream=True
            )
            
            full_english_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_english_response += chunk.choices[0].delta.content
                    message_placeholder.markdown("Çevriliyor... 🔄")
            
            # Modelden gelen İngilizce cevabı Türkçeye çevir
            final_turkish_response = translator.translate(full_english_response, src='en', dest='tr').text
            
            message_placeholder.markdown(final_turkish_response)
            st.session_state.messages.append({"role": "assistant", "content": final_turkish_response})
            
        except Exception as e:
            message_placeholder.markdown(f"❌ Kanka sistemde bir sıkıntı oldu: `{e}`")
