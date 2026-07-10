import streamlit as st
import requests

st.set_page_config(page_title="Asistan", page_icon="🤖")
st.title("🤖 Asistan")

# API KEY'İ BURAYA DİREKT YAZ (TEST İÇİN)
API_KEY = "AQ.Ab8RN6Kq87IwiYXisNn3k8f_gijyBuxm8iL4Xn0jSFRpSoPb1A" 

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
        cevap_kutusu = st.empty()
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:streamGenerateContent?key={API_KEY}"
            payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
            
            response = requests.post(url, json=payload, stream=True)
            
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        decoded = line.decode('utf-8')
                        if '"text":' in decoded:
                            chunk = decoded.split('"text":')[1].strip().strip('"').replace('\\n', '\n')
                            full_response += chunk
                            cevap_kutusu.markdown(full_response + "▌")
                cevap_kutusu.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error(f"Hata: {response.status_code}")
        except Exception as e:
            st.error(f"Hata: {e}")
