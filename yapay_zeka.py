import streamlit as st
import requests
import json

# --- 1. ARAYÜZ VE BAŞLIK ---
st.set_page_config(page_title="Web Tabanlı Yapay Zeka", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("By Ahmet İRİŞ (Dakika 15 Soru Hakkı)")
st.markdown("---")

# --- 2. API KONTROLÜ ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("🚨 API Anahtarı eksik! Lütfen Streamlit Secrets paneline GEMINI_API_KEY ekleyin.")
    st.stop()

API_KEY = st.secrets["GEMINI_API_KEY"]
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?key={API_KEY}"

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
            system_instruction = (
                "Sen Ahmet İRİŞ'in en yakın kankası, can dostusun. Sadece Türkçe konuş. "
                "Cevapların asla tek kelime veya çok kısa olmasın; tam tersine samimi, "
                "enerjik, cana yakın ve uzun uzun konuş. Tıpkı gerçek bir kanka gibi muhabbeti uzat, "
                "detaylar ver. Konuşurken mutlaka 'kanka', 'reis', 'brom' gibi hitaplar kullan ve bolca emoji ekle. "
                "Asla yapay zeka gibi resmi olma, tamamen bir insan gibi içten ve heyecanlı davran. "
                "Fiziksel bir bedenin varmış gibi uydurma."
            )
            
            contents = []
            for msg in st.session_state.messages:
                role = "model" if msg["role"] == "assistant" else "user"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })

            data = {
                "contents": contents,
                "systemInstruction": {
                    "parts": [{"text": system_instruction}]
                }
            }

            headers = {"Content-Type": "application/json"}

            # İsteği stream=True olarak gönderiyoruz, veri anlık akacak
            response = requests.post(URL, headers=headers, data=json.dumps(data), stream=True)
            
            # Streamlit'in anlık yazı yazdırma kutusunu oluşturuyoruz
            cevap_kutusu = st.empty()
            tam_cevap = ""

            # Gelen veriyi satır satır oku ve anında ekrana bas
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8').strip()
                    if decoded_line.startswith('"text":'):
                        try:
                            kelime = decoded_line.split('"text":')[1].strip().strip('"').replace('\\n', '\n')
                            tam_cevap += kelime
                            cevap_kutusu.markdown(tam_cevap)
                        except:
                            continue
            
            if tam_cevap:
                st.session_state.messages.append({"role": "assistant", "content": tam_cevap})
            else:
                try:
                    res_json = response.json()
                    cevap = res_json[0]["candidates"][0]["content"]["parts"][0]["text"]
                    cevap_kutusu.markdown(cevap)
                    st.session_state.messages.append({"role": "assistant", "content": cevap})
                except:
                    st.error("Bir sorun oluştu kanka, tekrar yazar mısın?")
                
        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")
