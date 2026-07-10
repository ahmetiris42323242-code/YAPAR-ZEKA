import streamlit as st
from groq import Groq

# --- 1. SAYFA VE GÖRÜNÜM AYARLARI ---
st.set_page_config(page_title="Ahmet İRİŞ - Yapay Zeka", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("Ahmet İRİŞ tarafından yapılmıştır")
st.markdown("---")

# --- 2. API BAĞLANTISI ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("🚨 API Anahtarı eksik! Lütfen Streamlit ayarlarından (Secrets) GROQ_API_KEY ekle.")
    st.stop()

# Groq istemcisini başlat
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. SOHBET GEÇMİŞİ (HAFIZA) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekrana bas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. YENİ MESAJ GÖNDERME VE CEVAP ALMA ---
if prompt := st.chat_input("Bir şeyler yaz kanka..."):
    
    # Kullanıcının mesajını ekle ve göster
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Yapay zeka cevabı
    with st.chat_message("assistant"):
        with st.spinner("Kankan düşünüyor..."):
            try:
                # Karakter ayarları (System Prompt)
                system_prompt = {
                    "role": "system", 
                    "content": (
                        "Sen Ahmet İRİŞ'in en yakın kankasısın. Sadece Türkçe konuş. "
                        "Cevapların çok kısa, net ve samimi olsun. Mutlaka emoji kullan. "
                        "Asla soru sorma. Fiziksel bir bedenin varmış gibi (uyudum, koştum) yalanlar uydurma."
                    )
                }
                
                # API'ye gönderilecek mesaj listesini hazırla
                messages_to_send = [system_prompt]
                for msg in st.session_state.messages:
                    messages_to_send.append(msg)

                # API'den cevabı tek seferde al (stream=False o log hatasını kesin çözer)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages_to_send,
                    stream=False
                )
                
                # Sadece temiz metni alıp ekrana bas
                cevap = response.choices[0].message.content
                st.markdown(cevap)
                
                # Cevabı hafızaya kaydet
                st.session_state.messages.append({"role": "assistant", "content": cevap})
                
            except Exception as e:
                st.error(f"Sistemsel bir hata oluştu: {e}")
