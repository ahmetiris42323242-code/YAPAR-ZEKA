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
    st.error(f"Bağlantı hatası: {e}")

# 3. Sohbet Geçmişi
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Yan Panel
with st.sidebar:
    if st.button("Sohbet Geçmişini Temizle 🧹"):
        st.session_state.messages = []
        st.rerun()

# 5. Mesajları Yazdır
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Girdi ve İşleme
if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Ahmet İRİŞ Kimlik Kontrolü
        if "ahmet iriş" in prompt.lower():
            answer = "Ahmet İRİŞ bu işin patronu, projenin mimarı! 🚀 Onunla çalışmak büyük keyif. 😎"
            message_placeholder.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            try:
                system_instruction = (
                    "Sen Ahmet İRİŞ'in en yakın kankasısın. "
                    "KURALLARIN: "
                    "1. ASLA küfür, argo veya kaba kelimeler kullanma. "
                    "2. Resmiyetten nefret et, samimi davran. "
                    "3. Türkçe yazım kurallarına (ağız tadı, noktalama) tam uy. "
                    "4. Cevapların kısa, enerjik, doğal ve emojili olsun. "
                    "5. Asla yabancı kelime kullanma."
                )

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_instruction},
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
                message_placeholder.markdown(f"❌ Bir hata oluştu: `{e}`")
