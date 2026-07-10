import streamlit as st
import requests
import json

# --- 1. SAYFA VE GÖRÜNÜM AYARLARI ---
st.set_page_config(page_title="Web Tabanlı Yapay Zeka", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("Ahmet İRİŞ tarafından yapılmıştır")
st.markdown("---")

# --- 2. API KONTROLÜ ---
if "OPENROUTER_API_KEY" not in st.secrets:
    st.error("🚨 API Anahtarı eksik! Lütfen Streamlit Secrets paneline OPENROUTER_API_KEY ekle.")
    st.stop()

API_KEY = st.secrets["OPENROUTER_API_KEY"]
URL = "https://openrouter.ai/api/v1/chat/completions"

# --- 3. SOHBET GEÇMİŞİ (HAFIZA) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekrana bas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. YENİ MESAJ GÖNDERME VE CEVAP ALMA ---
if prompt := st.chat_input("Bir şeyler yaz kanka..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            system_prompt = {
                "role": "system", 
                "content": (
                    "Sen Ahmet İRİŞ'in en yakın kankasısın. Sadece Türkçe konuş. "
                    "Cevapların çok kısa, net ve samimi olsun. Mutlaka emoji kullan. "
                    "Asla soru sorma. Fiziksel bir bedenin varmış gibi (uyudum, koştum) yalanlar uydurma."
                )
            }
            
            # Mesajları hazırla
            messages_to_send = [system_prompt] + st.session_state.messages

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            # OpenRouter üzerindeki ücretsiz Llama 3 modelini çağırıyoruz
            data = {
                "model": "meta-llama/llama-3-8b-instruct:free",
                "messages": messages_to_send
            }

            # İsteği gönder (stream kapalı, temiz veri gelecek)
            response = requests.post(URL, headers=headers, data=json.dumps(data))
            response_json = response.json()

            # Gelen yanıtı ayıkla
            if "choices" in response_json:
                cevap = response_json["choices"][0]["message"]["content"]
                st.markdown(cevap)
                st.session_state.messages.append({"role": "assistant", "content": cevap})
            else:
                st.error("OpenRouter tarafında bir sorun oluştu veya kota doldu.")
                
        except Exception as e:
            st.error(f"Bağlantı hatası: {e}")
