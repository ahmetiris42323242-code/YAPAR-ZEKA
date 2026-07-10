import streamlit as st
import requests
import json
import os

# --- 1. ARAYÜZ VE BAŞLIK ---
st.set_page_config(page_title="Web Tabanlı Yapay Zeka", page_icon="🤖")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.caption("By Ahmet İRİŞ (Dakika da 15 Soru Hakkı)")
st.markdown("---")

# --- 2. API KONTROLÜ ---
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("🚨 API Anahtarı eksik! Lütfen Render panelinden Environment Variables kısmına GEMINI_API_KEY ekleyin.")
    st.stop()

URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?key={API_KEY}"

# --- 3. SOHBET GEÇMİŞİ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. KULLANICI GİRDİSİ VE YANIT ---
if prompt := st.chat_input("Bir soru sorun..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Güncellenmiş sistem talimatı
            system_instruction = (
                "Sen Ahmet İRİŞ'in dijital asistanısın. Konuşmalarında hem ciddi hem de samimi bir ton kullan. "
                "Brom, kanka gibi aşırı samimi hitapları kullanma. "
                "Cevaplarını konunun içeriğine göre ayarla; basit sorulara kısa ve öz, detay gerektiren "
                "konulara ise kapsamlı cevaplar ver. Gereksiz uzun cümlelerden ve aşırı emoji kullanımından kaçın. "
                "Her zaman yardımcı, profesyonel ve içten bir tutum sergile."
            )
            
            contents = []
            for msg in st.session_state.messages:
                role = "model" if msg["role"] == "assistant" else "user"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })

            data = {
                "contents": contents,
                "systemInstruction": {
                    "parts": [{"text": system_instruction}]
                }
            }

            headers = {"Content-Type": "application/json"}
            response = requests.post(URL, headers=headers, data=json.dumps(data), stream=True)
            
            cevap_kutusu = st.empty()
            tam_cevap = ""

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8').strip()
                    if decoded_line.startswith('"text":'):
                        try:
                            kelime = decoded_line.split('"text":')[1].strip().strip('"').replace('\\n', '\n')
                            tam_cevap += kelime
                            cevap_kutusu.markdown(tam_cevap)
                        except:
                            continue
            
            if tam_cevap:
                st.session_state.messages.append({"role": "assistant", "content": tam_cevap})
            else:
                try:
                    res_json = response.json()
                    cevap = res_json[0]["candidates"][0]["content"]["parts"][0]["text"]
                    cevap_kutusu.markdown(cevap)
                    st.session_state.messages.append({"role": "assistant", "content": cevap})
                except:
                    st.error("Bir hata oluştu, lütfen tekrar deneyin.")
                
        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")
