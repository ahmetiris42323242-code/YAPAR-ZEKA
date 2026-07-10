import streamlit as st
from groq import Groq

# 1. Sayfa Ayarları (SEO ve Arayüz)
st.set_page_config(page_title="Ahmet İRİŞ - Yapay Zeka", page_icon="🤖", layout="centered")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("Ahmet İRİŞ tarafından yapılmıştır")

# 2. Bağlantı Ayarları
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"API Bağlantı hatası: {e}")
    st.stop()

# 3. Sohbet Geçmişi Yönetimi
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Yan Panel Kontrolleri
with st.sidebar:
    if st.button("Sohbeti Temizle 🧹"):
        st.session_state.messages = []
        st.rerun()

# 5. Mesajları Görselleştirme
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Girdi ve İşleme Motoru
if prompt := st.chat_input("Bir şeyler yaz kanka..."):
    # Kullanıcı mesajını kaydet ve göster
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Asistan cevabı
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Ahmet İRİŞ Kimlik Kontrolü (Hard-coded bypass)
        if "ahmet iriş" in prompt.lower():
            answer = "Ahmet İRİŞ bu işin patronu, projenin mimarı! 🚀 Onunla çalışmak büyük keyif. 😎"
            message_placeholder.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            try:
                # İnce Ayarlı Sistem Talimatı
                system_instruction = (
                    "Karakterin: Ahmet İRİŞ'in en yakın kankasısın. "
                    "Kısıtlamalar: "
                    "1. ASLA fiziksel eylem (koşmak, yemek, uyumak) veya insan hayatı uydurma. Sen bir yapay zekasın. "
                    "2. ASLA soru sorma. Cevaplarını net ve samimi tut. "
                    "3. Uzunluk: Ne çok kısa ('evet', 'tamam') ne de gereksiz uzun (gevezelik). Orta şeker, doğal sohbet. "
                    "4. Dil: Kusursuz Türkçe. Yabancı kelime (İngilizce vb.) KESİNLİKLE YASAK. "
                    "5. Biçim: Yazım kurallarına (büyük harf, noktalama) dikkat et. Cevabına mutlaka emoji ekle."
                )

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        *st.session_state.messages
                    ],
                    stream=True
                )
                
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                message_placeholder.markdown(f"❌ Kanka sistemde bir sıkıntı oldu: `{e}`")
    
