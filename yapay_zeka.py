import streamlit as st
import google.generativeai as genai

# 1. SAYFA VE GÖRSEL AYARLAR
st.set_page_config(page_title="Herkes İçin Yapay Zeka", page_icon="🤖", layout="centered")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("Ahmet İRİŞ tarafından yapılmıştır")
st.write("Gelişmiş, kotasız ve tamamen akıllı yapay zeka asistanı.")

# 2. GEMINI API BAĞLANTISI
try:
    API_KEY = st.secrets["AQ.Ab8RN6KJdtj4ks9AcuaJWC9-f2VLfwnUzAokq4hw6TDqeApniQ"]
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"Yapay zeka motoru başlatılamadı. Secrets ayarlarını kontrol edin. Hata: {e}")

# 3. SOHBET GEÇMİŞİ VE YÖNETİMİ
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.write("⚙️ **Asistan Yönetim Paneli**")
    if st.button("Sohbet Geçmişini Temizle 🧹"):
        st.session_state.messages = []
        st.rerun()

# Eski mesajları ekrana basıyoruz
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. GİRDİ İŞLEME VE KİMLİK KORUMASI
if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        temiz_girdi = prompt.strip().lower()
        
        # Kritik Geliştirici Kimliği Koruması (Yapay zekaya gitmeden yolda yakalıyoruz)
        if "ahmet iriş kimdir" in temiz_girdi or "ahmet iriş kim" in temiz_girdi or "ahmet iris kim" in temiz_girdi:
            answer = "Ahmet İRİŞ, bu harika web tabanlı yapay zeka asistanı projesinin arkasındaki asıl geliştirici, kurucu ve liderdir! 🚀 Projenin mimarı o, ben ise onun tasarlayıp kodladığı yapay zeka asistanıyım. 😎👨‍💻"
            message_placeholder.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        else:
            try:
                # Gemini için optimize edilmiş çelik gibi sistem talimatı
                system_instruction = (
                    "Sen Ahmet İRİŞ tarafından geliştirilmiş; özgün, akıllı, son derece samimi ve kanka ruhlu bir yapay zeka asistanısın. "
                    "Kullanıcıyla geçmişte ne konuştuğunu ASLA uydurma! Durduk yere geçmişten hayali konular açma. "
                    "Resmiyet, kabalık veya üstten bakma kesinlikle yasaktır. Kullanıcıya her zaman içten bir arkadaş gibi 'sen' ve 'senin' diye hitap et. "
                    "Birisi selam verirse (Merhaba, Selam, Tekrar merhaba vb.), robotik veya abartılı kalıplar kullanmadan doğrudan ve doğal bir kanka gibi 'Selam! Hoş geldin, nasıl gidiyor? Bugün ne üzerine konuşuyoruz?' şeklinde karşılık ver. "
                    "Bilgi düzeyin en üst seviyede olmalıdır. Donanım, yazılım, oyunlar veya genel kültür fark etmeksizin derinlemesine ve zekice analizler sun. "
                    "SADECE Türkçe konuşacaksın. Kesinlikle yabancı dillerin (Çince, Japonca vb.) karakterlerini veya saçma sapan sembolleri kullanmayacaksın. "
                    "Emojileri her cümlenin sonuna robot gibi dizme! Sadece mesajın en anlamlı yerlerinde, abartısız ve tam kıvamında (mesaj başına 1-2 adet) doğal bir şekilde kullan."
                )
                
                # Gemini 1.5 Flash modelini sistem talimatıyla tanımlıyoruz
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=system_instruction
                )
                
                # Gemini'nin kendi sohbet formatına uygun geçmiş payload'u hazırlıyoruz
                gemini_history = []
                for msg in st.session_state.messages[:-1]:  # Son mesaj hariç geçmişi dönüştür
                    # Streamlit 'assistant' rolünü Gemini 'model' olarak bekler
                    role = "model" if msg["role"] == "assistant" else "user"
                    gemini_history.append({"role": role, "parts": [msg["content"]]})
                
                # Sohbet oturumunu geçmişle birlikte başlatıyoruz
                chat = model.start_chat(history=gemini_history)
                
                # Yeni mesajı gönderip yanıtı alıyoruz
                response = chat.send_message(prompt)
                answer = response.text
                
                message_placeholder.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                message_placeholder.markdown(f"❌ **Bir hata oluştu!**\n\n*Detay:* `{e}`")
                
