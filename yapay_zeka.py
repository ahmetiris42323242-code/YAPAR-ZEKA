import streamlit as st
from google import genai

# 1. SAYFA AYARLARI VE GÖRSEL BAŞLIK
st.set_page_config(page_title="Herkes İçin Yapay Zeka", page_icon="🤖", layout="centered")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.write("Arka planda hiçbir program çalıştırmanıza gerek olmayan, herkesin kullanabileceği asistan.")

# 2. GOOGLE API BAĞLANTISI
# Google AI Studio'dan kopyaladığın güncel API anahtarını tek tırnakların arasına yapıştır.
# Örnek: 'AIzaSy...' (Tırnak işaretlerinin durduğundan emin ol)
API_KEY = 'AQ.Ab8RN6IIke3UJ1S30mBJK9Ubu68eWuSEtYvNRJXwbRvEgzbwyg'

try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"Yapay zeka motoru başlatılamadı. API anahtarınızı kontrol edin. Hata: {e}")

# 3. SOHBET GEÇMİŞİNİ HAFIZADA TUTMA (Streamlit Yenilense de Silinmez)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekrana sırasıyla çizdirme
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. KULLANICIDAN GİRDİ ALMA VE YAPAY ZEKAYI ÇALIŞTIRMA
if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    # Kullanıcının yazdığı soruyu hafızaya ve ekrana ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Yapay zekanın cevap verme animasyonu (Yükleniyor...)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # En güncel ve kütüphaneyle tam uyumlu ana modelimizi çağırıyoruz
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config={
                    "system_instruction": "Sen günlük hayatta karşılaşılan her türlü soruna pratik, yaratıcı ve evdeki malzemelerle çözümler sunan, Türkçe konuşan, cana yakın bir asistansın."
                }
            )
            
            answer = response.text
            message_placeholder.markdown(answer)
            
            # Yapay zekanın verdiği cevabı hafızaya kaydet (Konuşma devam edebilsin diye)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            message_placeholder.markdown(f"❌ **Bir hata oluştu!**\n\nLütfen Google AI Studio'dan aldığınız API anahtarını ve koddaki tırnak işaretlerini kontrol edin.\n\n*Detaylı Hata Mesajı:* `{e}`")
