import streamlit as st
from groq import Groq

# 1. Sayfa Ayarları
st.set_page_config(page_title="Herkes İçin Yapay Zeka", page_icon="🤖", layout="centered")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("Ahmet İRİŞ tarafından yapılmıştır")

# 2. Groq Bağlantısı
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"Groq bağlantısı kurulamadı: {e}")

# 3. Sohbet Geçmişi
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Panel ve Temizleme
with st.sidebar:
    if st.button("Sohbet Geçmişini Temizle 🧹"):
        st.session_state.messages = []
        st.rerun()

# 5. Geçmişi Ekrana Yazdır
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Kullanıcı Girişi
if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Ahmet İRİŞ Kimlik Kontrolü
        if "ahmet iriş" in prompt.lower():
            answer = "Ahmet İRİŞ, bu projenin mimarı ve lideridir! 🚀 Ben de onun kodladığı yapay zekayım. 😎"
            message_placeholder.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            try:
                # Groq API Çağrısı
                response = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": "Sen Ahmet İRİŞ tarafından geliştirilmiş samimi, zeki bir asistansın. Sadece Türkçe konuş, kanka ruhlu ol, saçmalama."},
                        *st.session_state.messages
                    ],
                    stream=True
                )
                
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                message_placeholder.markdown(f"❌ Hata oluştu: `{e}`")
                
