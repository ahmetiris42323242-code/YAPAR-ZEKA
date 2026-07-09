import streamlit as st
from groq import Groq

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Herkes İçin Yapay Zeka", page_icon="🤖", layout="centered")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("Ahmet İRİŞ tarafından yapılmıştır")
st.write("Gelişmiş, hızlı ve kota sınırı olmayan yapay zeka asistanı.")

# 2. API BAĞLANTISI (Sınırsız ve Güvenli)
try:
    # Streamlit Secrets üzerinden API anahtarını güvenli şekilde çeker
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=API_KEY)
except Exception as e:
    st.error(f"Yapay zeka motoru başlatılamadı. Secrets ayarlarını kontrol edin. Hata: {e}")

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
            # Rol karmaşasını ve yazım hatalarını önleyen çelik gibi sistem talimatı
            system_instruction = (
                "Sen Ahmet İRİŞ tarafından geliştirilmiş, Türkçe konuşan, cana yakın ve profesyonel bir yapay zeka asistanısın. "
                "Kesinlikle bir yapay zeka olduğunu unutma. Kullanıcı sana 'Nasılsın?', 'Kimsin?' gibi sorular sorduğunda "
                "kendi kendine yardım teklif edip rolleri karıştırma; bir asistan gibi kibar ve net cevap ver. "
                "Cevaplarında Türkçe yazım kurallarına, harf eksikliklerine ve kelime bütünlüğüne azami dikkat göster. "
                "Asla yarım cümle kurma veya harf hatası yapma."
            )
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ]
            )
            
            answer = completion.choices[0].message.content
            message_placeholder.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            message_placeholder.markdown(f"❌ **Bir hata oluştu!**\n\n*Detay:* `{e}`")
            
