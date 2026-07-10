import streamlit as st
from groq import Groq

# 1. GÖRÜNÜM VE BAŞLIK
st.set_page_config(page_title="Web Tabanlı Yapay Zeka", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("Ahmet İRİŞ tarafından yapılmıştır")
st.divider()

# 2. API KONTROLÜ
if "GROQ_API_KEY" not in st.secrets:
    st.error("API Anahtarı bulunamadı! Lütfen Streamlit Secrets paneline GROQ_API_KEY ekleyin.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. HAFIZA OLUŞTURMA
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekrana bas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. MESAJ GÖNDERME VE YANIT ALMA
if prompt := st.chat_input("Bir şeyler yaz..."):
    
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Yapay zeka yanıtını al
    with st.chat_message("assistant"):
        # Sistem talimatını sadece API'ye gönderirken araya sıkıştırıyoruz
        sistem_mesaji = {
            "role": "system", 
            "content": "Sen Ahmet İRİŞ'in en yakın kankasısın. Çok kısa, samimi ve Türkçe konuş. Mutlaka emoji kullan. Asla soru sorma. Fiziksel bir bedenin varmış gibi eylemler uydurma."
        }
        
        gonderilecek_mesajlar = [sistem_mesaji] + st.session_state.messages

        try:
            # stream=False kullanılarak yarım yamalak JSON döküntüleri engellendi
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=gonderilecek_mesajlar,
                stream=False
            )
            
            cevap = response.choices[0].message.content
            st.markdown(cevap)
            
            # Asistanın yanıtını hafızaya ekle
            st.session_state.messages.append({"role": "assistant", "content": cevap})
            
        except Exception as e:
            st.error(f"Hata oluştu: {e}")
