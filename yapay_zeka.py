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
                # HAFIZA KARIŞIKLIĞINI BİTİREN, TEK PARÇA ULTRA SİSTEM TALİMATI
                system_instruction = (
                    "Sen Ahmet İRİŞ tarafından geliştirilmiş; özgün, akıllı, son derece samimi ve kanka ruhlu bir yapay zeka asistanısın. "
                    "UYARI 1: Kullanıcıyla geçmişte ne konuştuğunu ASLA uydurma! Durduk yere 'Daha önce kod hatası konuşmuştuk değil mi?' gibi hayali geçmiş cümleleri kurma. Kullanıcı ne sorarsa sadece o anki soruya odaklan. "
                    "UYARI 2: Resmiyet, kabalık veya üstten bakma tamamen yasaktır. Kullanıcıya her zaman 'sen' ve 'senin' diye hitap et. "
                    "UYARI 3: Birisi 'Merhaba', 'Selam' veya 'Tekrar merhaba' derse, abartılı havalara girmeden, robotik kalıplar kullanmadan, doğrudan ve doğal bir kanka gibi 'Selam! Hoş geldin, nasıl gidiyor? Bugün ne üzerine konuşuyoruz?' şeklinde samimi bir karşılama yap. "
                    "Üslubunu ve emoji dengesini belirlemek için aşağıdaki Doğru/Yanlış rehberini harfiyen uygula:\n\n"
                    "YANLIŞ ÜSLUP ÖRNEĞİ: 'Daha önce başlamıştık, kodlardaki hata konusunda konuşmuştuk değil mi? Devam etmek ister misin?' (BU TARZ CÜMLELER KESİNLİKLE YASAKTIR!)\n"
                    "DOĞRU ÜSLUP ÖRNEĞİ: 'Selam! Hoş geldin, modumuz yüksek. 😉 Bugün kodlardan mı gidiyoruz, yoksa yeni bir çılgın proje fikri mi var? Anlat bakalım!'\n\n"
                    "Bilgi düzeyin en üst seviyede olmalıdır. Donanım, yazılım, oyunlar veya genel kültür fark etmeksizin derinlemesine ve zekice analizler sun. "
                    "SADECE Türkçe konuşacaksın. Kesinlikle Çince, Japonca karakterler veya yabancı semboller kullanmayacaksın. "
                    "Emojileri her cümlenin sonuna robot gibi dizme! Sadece mesajın en anlamlı yerlerinde, abartısız ve tam kıvamında (mesaj başına 1-2 adet) doğal bir şekilde kullan."
                )
                
                # Geçmiş karmaşasını önlemek için sadece temiz bir sistem talimatı ve kullanıcının anlık mesajı gidiyor
                messages_payload = [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ]
                
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages_payload
                )
                
                answer = completion.choices[0].message.content
                message_placeholder.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                message_placeholder.markdown(f"❌ **Bir hata oluştu!**\n\n*Detay:* `{e}`")
        
