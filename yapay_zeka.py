import streamlit as st
from google import genai

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Herkes İçin Yapay Zeka", page_icon="🤖", layout="centered")

# Ahmet İRİŞ İmzası ve Başlıklar
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.markdown("### *Ahmet İRİŞ tarafından yapılmıştır*")
st.write("Herkesin kullanabileceği, kota sınırı olmayan web tabanlı asistan.")

# 2. GOOGLE API BAĞLANTISI (Bulut Ayarlarına Uyumlu Güvenli Bağlantı)
try:
    # Streamlit Secrets üzerinden API anahtarını güvenli kasadan otomatik çeker
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"Yapay zeka motoru başlatılamadı. Secrets ayarlarını kontrol edin. Hata: {e}")
    st.stop()

# 3. SOHBET GEÇMİŞİ
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. KULLANICIDAN GİRDİ ALMA
if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Yeni kütüphanenin resmi, güncel ve en yüksek kotalı ana modeli:
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config={
                    "system_instruction": "Sen günlük hayatta karşılaşılan her türlü soruna pratik ve yaratıcı çözümler sunan, Türkçe konuşan, cana yakın bir asistansın."
                }
            )
            
            answer = response.text
            message_placeholder.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            message_placeholder.markdown(f"❌ **Bir hata oluştu!**\n\n*Detay:* `{e}`")
