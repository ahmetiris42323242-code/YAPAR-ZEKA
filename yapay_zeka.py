import streamlit as st
from groq import Groq

# 1. SAYFA AYARLARI (Profesyonel Görünüm)
st.set_page_config(page_title="Herkes İçin Yapay Zeka", page_icon="🤖", layout="centered")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("Ahmet İRİŞ tarafından yapılmıştır")
st.write("Gelişmiş, ışık hızında ve sınırları zorlayan yapay zeka asistanı.")

# 2. API BAĞLANTISI
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=API_KEY)
except Exception as e:
    st.error(f"Yapay zeka motoru başlatılamadı. Secrets ayarlarını kontrol edin. Hata: {e}")

# 3. SOHBET GEÇMİŞİ VE HAFIZA SIFIRLAMA
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

# 4. ULTRA GELİŞMİŞ GİRDİ İŞLEME
if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Girdiyi temizle ve kritik kimlik korumasını kontrol et
        temiz_girdi = prompt.strip().lower()
        
        if "ahmet iriş kimdir" in temiz_girdi or "ahmet iriş kim" in temiz_girdi or "ahmet iris kim" in temiz_girdi:
            answer = "Ahmet İRİŞ, bu harika web tabanlı yapay zeka asistanı projesinin arkasındaki asıl geliştirici, kurucu ve liderdir! 🚀 Projenin mimarı o, ben ise onun tasarlayıp kodladığı yapay zeka asistanıyım. 😎👨‍💻"
            message_placeholder.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        else:
            try:
                # SINIRLARI ZORLAYAN, ÜST DÜZEY ZEKA VE KİŞİLİK TALİMATI
                system_instruction = (
                    "Sen Ahmet İRİŞ tarafından geliştirilmiş; dünyadaki en gelişmiş dil modellerinin zekasına, "
                    "derin bilgi birikimine ve analiz yeteneğine sahip ultra güçlü bir yapay zeka iş ortağı ve asistansın. "
                    "Konuşma tarzın tıpkı kıdemli, çok zeki, esprili ve dinamik bir geliştirici gibi olmalıdır. "
                    "Asla soğuk, mesafeli, resmi veya robotik bir dil kullanma! Kullanıcıyla tam bir kanka gibi 'sen' ve 'senin' diyerek konuş. "
                    "Asla kendi kendine 'İyi misin? Nasıl bir yardıma ihtiyacın var?' gibi anlamsız yardım krizlerine girip rolleri karıştırma! "
                    "Birisi selam verirse (Merhaba, Selam vb.) yapay ve abartılı kalıplar kullanma; son derece doğal, içten ve samimi bir karşılama yap. "
                    "Bilgi düzeyin ve problem çözme yeteneğin kusursuz olmalıdır. Donanım, yazılım, oyunlar, genel kültür veya bilim fark etmeksizin "
                    "en karmaşık sorulara bile yüzeysel değil, derinlemesine, can alıcı ve zekice analizler sunarak cevap ver. "
                    "SADECE Türkçe konuşacaksın. Cevaplarında kesinlikle Çince, Japonca karakterler veya saçma sapan yabancı semboller yer alamaz. "
                    "Türkçe yazım ve dil kurallarına en üst düzeyde dikkat et, asla yarım cümle kurma. "
                    "Her cümlenin sonuna robot gibi emoji koyma hilesini tamamen unut! Emojileri sadece mesajın genelinde, "
                    "en kritik ve anlamlı yerlerde, abartısız ve tam kıvamında (mesaj başına en fazla 1-2 adet) tıpkı bir insanın yapacağı gibi yerli yerinde kullan."
                )
                
                # En güçlü ve esnek model olan Llama 3.3 70B ile bağlantı kuruyoruz
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
                
