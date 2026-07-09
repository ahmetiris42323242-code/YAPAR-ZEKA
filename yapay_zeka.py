import streamlit as st
from google import genai

# 1. SAYFA AYARLARI VE BAŞLIK
st.set_page_config(page_title="Herkes İçin Yapay Zeka", page_icon="🤖", layout="centered")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.write("Arka planda hiçbir program çalıştırmanıza gerek olmayan, herkesin kullanabileceği asistan.")

# Google API Bağlantısı (API anahtarını buraya tırnak içine yaz)
client = genai.Client(api_key='AQ.Ab8RN6JLo8alRPmOxz3N_yp5BWzllmC1fBDCEUUnHJVS_dafaw')

# 2. SOHBET GEÇMİŞİNİ HAFIZADA TUTMA
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekrana çizdirme
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. KULLANICIDAN YAZI ALMA ALANI
if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    # Kullanıcının yazdığı soruyu hafızaya ve ekrana ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Yapay zekanın cevap verme animasyonu
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Google Gemini modeline soruyu gönderiyoruz
            response = client.models.generate_content(
                model='gemini-1.5-flash', # Kotası çok daha rahat olan model
                contents=prompt,
                config={
                    "system_instruction": "Sen günlük hayatta karşılaşılan her türlü soruna pratik ve yaratıcı çözümler sunan, Türkçe konuşan, cana yakın bir asistansın."
                }
            )
            
            answer = response.text
            message_placeholder.markdown(answer)
            
            # Yapay zekanın cevabını hafızaya kaydet
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            message_placeholder.markdown(f"❌ Bir hata oluştu. Lütfen API anahtarınızı kontrol edin. Hata: {e}")