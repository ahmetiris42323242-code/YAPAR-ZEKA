import streamlit as st
import requests
import json
from duckduckgo_search import DDGS
from gtts import gTTS

# --- KONUM TESPİTİ ---
def get_user_location():
    try:
        res = requests.get('https://ipinfo.io/')
        data = res.json()
        return f"{data.get('city', 'Isparta')}, {data.get('region', 'Türkiye')}"
    except:
        return "Şarkikaraağaç, Isparta"

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Ahmet İRİŞ Asistanı", page_icon="🤖", layout="wide")

st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.markdown("##### <span style='color:grey'>By Ahmet İRİŞ | Senior Yazılım Mimarı 2026</span>", unsafe_allow_html=True)
st.divider()

# --- GELİŞTİRİCİ PANELİ ---
if "is_dev_mode" not in st.session_state:
    st.session_state.is_dev_mode = False

with st.sidebar:
    st.subheader("⚙️ Geliştirici Paneli")
    if st.text_input("Şifre", type="password") == "7536":
        st.session_state.is_dev_mode = True
        st.success("✅ GPT-4o PRO AKTİF")
    
    if st.button("Modu Kapat"):
        st.session_state.is_dev_mode = False
        st.rerun()

# --- SOHBET MANTIĞI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- GİRDİ ALANI ---
prompt = st.chat_input("Kodunu veya sorunu yaz...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ARAMA
    user_loc = get_user_location()
    search_results = ""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"{prompt} konum: {user_loc}", max_results=1))
            search_results = str(results)
    except:
        search_results = "İnternet verisi alınamadı."

    # MODEL SEÇİMİ (GPT-4o PRO)
    model_name = "openai/gpt-4o" if st.session_state.is_dev_mode else "meta-llama/llama-3.1-8b-instruct"
    
    # API İSTEĞİ
    headers = {
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [{"role": "system", "content": f"Sen Ahmet İRİŞ'in baş mimarısın. Teknik analiz ustasısın. Veri: {search_results}"}, {"role": "user", "content": prompt}],
        "stream": True 
    }

    # ANLIK AKIŞLI YAZDIRMA
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, stream=True)
            
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith("data: "):
                        json_str = line_text[6:]
                        if json_str.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(json_str)
                            content = chunk['choices'][0]['delta'].get('content', '')
                            if content:
                                full_response += content
                                message_placeholder.markdown(full_response + "▌")
                        except:
                            continue
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")
