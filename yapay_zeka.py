import streamlit as st
from groq import Groq

# 1. Sayfa Ayarları
st.set_page_config(page_title="Ahmet İRİŞ - Asistan", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka")

# 2. Bağlantı
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("API Anahtarı eksik!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Sohbeti Yazdır
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. İşleme (Çeviri kütüphanesi olmadan, direkt modelle)
if prompt := st.chat_input("Bir şeyler yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        system_instruction = (
            "Sen Ahmet İRİŞ'in kankasısın. Sadece Türkçe konuş. "
            "Asla soru sorma. Fiziksel eylemler (koşmak, yemek vb.) uydurma. "
            "Kısa, net ve samimi ol. Asla yabancı kelime kullanma."
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_instruction}, *st.session_state.messages],
            stream=True
        )
        
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
