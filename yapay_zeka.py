import streamlit as st
import requests
import json

# --- 1. AYARLAR ---
st.set_page_config(page_title="Web Tabanlı Yapay Zeka", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("By Ahmet İRİŞ")
st.markdown("---")

# --- 2. API BAĞLANTISI ---
# Streamlit Cloud'daki "Manage Secrets" alanından anahtarı çeker
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("🚨 API Anahtarı bulunamadı! 'Manage Secrets' kısmına GEMINI_API_KEY ekleyin.")
    st.stop()

URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:streamGenerateContent?key={API_KEY}"

# --- 3. SOHBET GEÇMİŞİ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. ASİSTAN MANTIĞI VE CEVAPLAMA ---
if user_input := st.chat_input("Bir mesaj yaz..."):
    # Kullanıcı mesajını ekle ve göster
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        cevap_kutusu = st.empty()
        full_response = ""
        
        # Asistan kimliği
        system_instruction = "Sen Ahmet İRİŞ'in dijital asistanısın. Profesyonel, ciddi ve samimi bir ton kullan."
        
        # API'ye gönderilecek veri formatı
        contents = [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages]
        payload = {"contents": contents}

        try:
            response = requests.post(URL, json=payload, stream=True)
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        decoded = line.decode('utf-8')
                        if decoded.startswith("data: "):
                            json_data = json.loads(decoded[6:])
                            if 'candidates' in json_data:
                                chunk = json_data['candidates'][0]['content']['parts'][0]['text']
                                full_response += chunk
                                cevap_kutusu.markdown(full_response + "▌")
                
                cevap_kutusu.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error(f"Hata Kodu: {response.status_code} - Lütfen anahtarınızı ve kotanızı kontrol edin.")
        
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
