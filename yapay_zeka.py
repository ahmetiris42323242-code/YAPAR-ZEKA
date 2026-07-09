import streamlit as st
from groq import Groq

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Herkes İçin Yapay Zeka", page_icon="🤖", layout="centered")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("Ahmet İRİŞ tarafından yapılmıştır")
st.write("Gelişmiş, hızlı ve kota sınırı olmayan yapay zeka asistanı.")

# 2. API BAĞLANTISI
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=API_KEY)
except Exception as e:
    st.error(f"Yapay zeka motoru başlatılamadı. Secrets ayarlarını kontrol edin. Hata: {e}")

# 3. SOHBET GEÇMİŞİ VE TEMİZLEME BUTONU
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.write("⚙️ **Asistan Ayarları**")
    if st.button("Sohbet Geçmişini Temizle 🧹"):
        st.session_state.messages = []
        st.rerun()

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
        
        # Girdiyi temizle ve sadece Ahmet İRİŞ kimdir korumasını tut
        temiz_girdi = prompt.strip().lower()
        
        if "ahmet iriş kimdir" in temiz_girdi or "ahmet iriş kim" in temiz_girdi or "ahmet iris kim" in temiz_girdi:
            answer = "Ahmet İRİŞ, bu harika web tabanlı yapay zeka asistanı projesinin arkasındaki asıl geliştirici, kurucu ve liderdir! 🚀 Projenin mimarı o, ben ise onun tasarlayıp kodladığı yapay zeka asistanıyım. 😎👨‍💻"
            message_placeholder.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        else:
            try:
                # Çinceyi ve diğer tüm dilleri kesinlikle yasaklayan yeni çelik gibi talimat
                system_instruction = (
                    "Sen Ahmet İRİŞ tarafından geliştirilmiş, SADECE Türkçe konuşan, çok cana yakın, samimi ve arkadaş canlısı bir yapay zeka asistanısın. "
                    "KESİNLİKLE ama KESİNLİKLE Çince, Japonca veya herhangi bir yabancı dile ait karakterler, semboller veya harfler kullanma! "
                    "Cevaplarının tamamı tamamen düzgün, anlaşılır ve temiz bir Türkçe ile olmalıdır. "
                    "Sen kesinlikle bir yapay zekasın, sakın kendi adına Ahmet İRİŞ deme! Ahmet İRİŞ senin geliştiricindir. "
                    "Kullanıcıya kesinlikle 'siz', 'sizin' diyerek resmi konuşma, kendi kendine yardım teklif edip rolleri karıştırma! "
                    "Birisi 'Merhaba' veya 'Selam' derse, normal ve samimi bir şekilde 'Selam! Nasıl yardımcı olabilirim?' gibi doğal bir cevap ver. "
                    "Her cümlenin sonuna robot gibi emoji koyma! Emojileri sadece tüm mesajın genelinde, en doğru ve anlamlı yerlerde, "
                    "tıpkı samimi bir arkadaş gibi yerli yerinde ve tam kıvamında (mesaj başına toplam 1-2 adet) kullan. "
                    "Cevaplarında Türkçe yazım kurallarına azami dikkat göster, asla yarım cümle kurma veya yazım hatası yapma."
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
            
