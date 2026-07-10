import streamlit as st
import requests
import json
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Ahmet İRİŞ Asistan", page_icon="🤖")
st.title("🤖 Dijital Asistan")
st.markdown("---")

# --- API KEY KONTROLÜ (GÜVENLİ YÖNTEM) ---
# Eğer Render'daki değişken okunmazsa kod hata vermesin diye bir kontrol ekledik
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("🚨 API Anahtarı bulunamadı! Lütfen Render panelinde 'GEMINI_API_KEY' değişkenini kontrol edin.")
    st.stop()

URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:streamGenerateContent?key={API_KEY}"

# --- SOHBET GEÇMİŞİ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- KULLANICI GİRİŞİ ---
if user_input := st.chat_input("Mesajınızı yazın..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # --- ASİSTAN CEVABI ---
    with st.chat_message("assistant"):
        cevap_kutusu = st.empty()
        full_response = ""
        
        system_instruction = "Sen Ahmet İRİŞ'in asistanısın. Kısa, öz ve profesyonel cevaplar ver."
        
        contents = [{"role": "model" if m["role"] == "assistant" else "user", 
                     "parts": [{"text": m["content"]}]} for m in st.session_state.messages]
        
        data = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_instruction}]}
        }

        try:
            response = requests.post(URL, headers={"Content-Type": "application/json"}, data=json.dumps(data), stream=True)
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8').strip()
                        if '"text":' in decoded_line:
                            chunk = decoded_line.split('"text":')[1].strip().strip('"').replace('\\n', '\n')
                            full_response += chunk
                            cevap_kutusu.markdown(full_response + "▌")
                cevap_kutusu.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error(f"Sunucu Hatası ({response.status_code}): API anahtarınızı veya bağlantıyı kontrol edin.")
                
        except Exception as e:
            st.error(f"Bağlantı Hatası: {str(e)}")
