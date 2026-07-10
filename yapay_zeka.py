import streamlit as st
import requests
import json

# --- 1. ARAYÜZ VE BAŞLIK ---
st.set_page_config(page_title="Web Tabanlı Yapay Zeka", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("Ahmet İRİŞ tarafından yapılmıştır")
st.markdown("---")

# --- 2. API KONTROLÜ ---
if "HF_TOKEN" not in st.secrets:
    st.error("🚨 API Anahtarı eksik! Lütfen Streamlit Secrets paneline HF_TOKEN ekleyin.")
    st.stop()

API_KEY = st.secrets["HF_TOKEN"]
# Hugging Face üzerinden Qwen 2.5 modelini çağırıyoruz (Meta değil, tamamen ücretsiz ve stabil)
URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct/v1/chat/completions"

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
            # Yapay zekanın karakter talimatı
            system_prompt = {
                "role": "system", 
                "content": (
                    "Sen Ahmet İRİŞ'in en yakın kankasısın. Sadece Türkçe konuş. "
                    "Cevapların çok kısa, samimi ve net olsun. Mutlaka emoji kullan. "
                    "Asla soru sorma. Fiziksel bir bedenin varmış gibi uydurma."
                )
            }
            
            # Geçmişle talimatı birleştir
            messages_to_send = [system_prompt] + st.session_state.messages

            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "Qwen/Qwen2.5-7B-Instruct",
                "messages": messages_to_send,
                "max_tokens": 150
            }

            # İsteği gönder
            response = requests.post(URL, headers=headers, data=json.dumps(data))
            response_json = response.json()

            # Yanıtı kontrol et ve ekrana bas
            if "choices" in response_json and len(response_json["choices"]) > 0:
                cevap = response_json["choices"][0]["message"]["content"]
                st.markdown(cevap)
                # Hafızaya ekle
                st.session_state.messages.append({"role": "assistant", "content": cevap})
            else:
                st.error("Hugging Face sunucusu şu an uyanıyor olabilir, lütfen birkaç saniye sonra tekrar dene.")
                
        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")
