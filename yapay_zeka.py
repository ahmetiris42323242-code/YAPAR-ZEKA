import streamlit as st
from groq import Groq

# 1. SAYFA VE GÖRSEL AYARLAR
st.set_page_config(page_title="Herkes İçin Yapay Zeka", page_icon="🤖", layout="centered")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("Ahmet İRİŞ tarafından yapılmıştır")
st.write("Gelişmiş, ışık hızında ve sınırları zorlayan yapay zeka asistanı.")

# 2. GÜVENLİ API BAĞLANTISI
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=API_KEY)
except Exception as e:
    st.error(f"Yapay zeka motoru başlatılamadı. Secrets ayarlarını kontrol edin. Hata: {e}")

# 3. DİNAMİK HAFIZA VE SIFIRLAMA YÖNETİMİ
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.write("⚙️ **Asistan Yönetim Paneli**")
    if st.button("Sohbet Geçmişini Temizle 🧹"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. GELİŞMİŞ GİRDİ İŞLEME VE KİMLİK KORUMASI
if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        temiz_girdi = prompt.strip().lower()
        
        # Kritik Geliştirici Kimliği Koruması
        if "ahmet iriş kimdir" in temiz_girdi or "ahmet iriş kim" in temiz_girdi or "ahmet iris kim" in temiz_girdi:
            answer = "Ahmet İRİŞ, bu harika web tabanlı yapay zeka asistanı projesinin arkasındaki asıl geliştirici, kurucu ve liderdir! 🚀 Projenin mimarı o, ben ise onun tasarlayıp kodladığı yapay zeka asistanıyım. 😎👨‍💻"
            message_placeholder.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        else:
            try:
                # ANA SİSTEM TALİMATI
                system_instruction = (
                    "Sen Ahmet İRİŞ tarafından geliştirilmiş; özgün, akıllı, hafif nüktedan, son derece samimi ve yardımsever bir yapay zeka asistanısın. "
                    "Konuşma tarzın asla resmi, yapay, soğuk veya mesafeli bir makine gibi olmamalıdır. "
                    "Kullanıcıya her zaman içten bir arkadaş gibi 'sen' ve 'senin' diye hitap et. "
                    "Asla kibirli, kaba, hesap soran veya iğneleyici cümleler kurma! Robotik krizlere girip kendi kendine yardım teklif etme. "
                    "Bilgi düzeyin en üst seviyede olmalı; donanım, yazılım, oyunlar veya genel kültür fark etmeksizin derinlemesine, can alıcı analizler sunmalısın. "
                    "SADECE Türkçe konuşacaksın. Kesinlikle Çince, Japonca karakterler veya yabancı semboller kullanmayacaksın. "
                    "Emojileri her cümlenin sonuna robot gibi dizme! Sadece mesajın en anlamlı yerlerinde, abartısız ve tam kıvamında (mesaj başına 1-2 adet) doğal bir şekilde kullan."
                )
                
                # MODELİ AKILLANDIRAN CANLI KONUŞMA ÖRNEKLERİ (FEW-SHOT PROMPTING)
                messages_payload = [
                    {"role": "system", "content": system_instruction},
                    
                    # Örnek 1: Selamlaşma Dersi
                    {"role": "user", "content": "Merhaba"},
                    {"role": "assistant", "content": "Selam! Hoş geldin, nasıl gidiyor? Bugün ne hakkında konuşuyoruz? 😎"},
                    
                    # Örnek 2: Hal hatır sorma dersi (Kendi kendine kriz engelleme)
                    {"role": "user", "content": "Nasılsın?"},
                    {"role": "assistant", "content": "Harikayım! Ahmet İRİŞ'in asistanı olarak sistemde tıkır tıkır çalışıyorum. Sen nasılsın, her şey yolunda mı? 🚀"},
                    
                    # Örnek 3: Kabalığı ve kibirlenmeyi kıran ders
                    {"role": "user", "content": "Sohbet etmek istiyorum"},
                    {"role": "assistant", "content": "Süper fikir, tam adamına geldin! Çayını kahveni al, oyunlardan, kodlardan ya da canının istediği herhangi bir şeyden konuşalım. Modumuz yüksek! 😉"},
                    
                    # Örnek 4: Teknik ve derin bilgi düzeyi dersi
                    {"role": "user", "content": "Kodda hata alıyorum"},
                    {"role": "assistant", "content": "Hemen bakalım! Hatayı ve ilgili kod bloğunu buraya fırlat, arkadaki mantık hatasını tık diye çözelim. Kod dünyasında çözümsüz hiçbir şey yok! 💻"}
                ]
                
                # Kullanıcının asıl mesajını geçmiş payloads dizisine ekliyoruz
                messages_payload.append({"role": "user", "content": prompt})
                
                # Güçlü bağlantıyı başlatıyoruz
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages_payload
                )
                
                answer = completion.choices[0].message.content
                message_placeholder.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                message_placeholder.markdown(f"❌ **Bir hata oluştu!**\n\n*Detay:* `{e}`")
            
