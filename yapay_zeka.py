import streamlit as st
import requests
import json

# --- 1. ARAYÜZ VE BAŞLIK ---
st.set_page_config(page_title="Web Tabanlı Yapay Zeka", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("Ahmet İRİŞ tarafından yapılmıştır")
st.markdown("---")

# --- 2. API KONTROLÜ ---
if "OPENROUTER_API_KEY" not in st.secrets:
    st.error("🚨 API Anahtarı eksik! Lütfen Streamlit Secrets paneline OPENROUTER_API_KEY ekleyin.")
    st.stop()

API_KEY = st.secrets["OPENROUTER_API_KEY"]
URL = "https://openrouter.ai/api/v1/chat/completions"

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

            # Tamamen Google altyapısı, Meta kesinlikle yok! çok hızlı ve ücretsiz.
            data = {
                "model": "mistralai/mistral-7b-instruct:free",
                "messages": messages_to_send
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
                hata_mesaji = response_json.get("error", {}).get("message", "Bilinmeyen bir hata oluştu.")
                st.error(f"Sistem Hatası: {hata_mesaji}")
                
        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")
