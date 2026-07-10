import streamlit as st
import requests
import json

# --- 1. ARAYÜZ VE BAŞLIK ---
st.set_page_config(page_title="Web Tabanlı Yapay Zeka", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("Ahmet İRİŞ tarafından yapılmıştır")
st.markdown("---")

# --- 2. API KONTROLÜ ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("🚨 API Anahtarı eksik! Lütfen Streamlit Secrets paneline GEMINI_API_KEY ekleyin.")
    st.stop()

API_KEY = st.secrets["GEMINI_API_KEY"]
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

# --- 3. SOHBET GEÇMİŞİ (HAFIZA) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski sohbeti ekrana yansıt
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. KULLANICI GİRDİSİ VE YANIT ---
if prompt := st.chat_input("Bir şeyler yaz kanka..."):
    
    # Kullanıcı mesajını ekle ve ekrana yaz
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Yapay zeka yanıt penceresi
    with st.chat_message("assistant"):
        try:
            # Karakter talimatı
            system_instruction = (
                "Sen Ahmet İRİŞ'in en yakın kankasısın. Sadece Türkçe konuş. "
                "Cevapların çok kısa, samimi ve net olsun. Mutlaka emoji kullan. "
                "Asla soru sorma. Fiziksel bir bedenin varmış gibi uydurma."
            )
            
            # Google Gemini formatına göre geçmişi hazırla
            contents = []
            for msg in st.session_state.messages:
                role = "model" if msg["role"] == "assistant" else "user"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })

            # API veri yapısı
            data = {
                "contents": contents,
                "systemInstruction": {
                    "parts": [{"text": system_instruction}]
                }
            }

            headers = {"Content-Type": "application/json"}

            # İsteği gönder
            response = requests.post(URL, headers=headers, data=json.dumps(data))
            response_json = response.json()

            # Yanıtı kontrol et ve ekrana bas
            if "candidates" in response_json and len(response_json["candidates"]) > 0:
                cevap = response_json["candidates"][0]["content"]["parts"][0]["text"]
                st.markdown(cevap)
                # Hafızaya ekle
                st.session_state.messages.append({"role": "assistant", "content": cevap})
            else:
                st.error("Yanıt alınamadı. Lütfen tekrar dene kanka.")
                
        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")
