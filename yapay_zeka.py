import streamlit as st
import requests
import base64
from duckduckgo_search import DDGS
from gtts import gTTS
import random

# --- YARDIMCI FONKSİYONLAR ---
def get_user_location():
    try:
        res = requests.get('https://ipinfo.io/', timeout=2)
        data = res.json()
        return f"{data.get('city', 'Isparta')}, {data.get('region', 'Türkiye')}"
    except:
        return "Şarkikaraağaç, Isparta"

# --- ARAYÜZ AYARLARI ---
st.set_page_config(page_title="Ahmet İRİŞ Asistanı", page_icon="🤖", layout="wide")
st.title("🤖 Web Tabanlı Yapay Zeka Asistanı")
st.markdown("##### <span style='color:grey'>By Ahmet İRİŞ | Senior Yazılım Mimarı 2026</span>", unsafe_allow_html=True)
st.divider()

# --- PANEL & DURUM ---
if "is_dev_mode" not in st.session_state: st.session_state.is_dev_mode = False
if "messages" not in st.session_state: st.session_state.messages = []
if "gorsel_key" not in st.session_state: st.session_state.gorsel_key = 0

with st.sidebar:
    st.subheader("⚙️ Geliştirici Paneli")
    if st.text_input("Şifre", type="password") == "7536": 
        st.session_state.is_dev_mode = True
        st.success("✅ SÜPER ZEKA AKTİF")
    if st.button("Modu Kapat"): 
        st.session_state.is_dev_mode = False
        st.rerun()
    
    st.markdown("---")
    st.subheader("🎨 Görsel Atölyesi")
    g_prompt = st.text_input("Ne çizelim?", key="g_prompt_input")
    if st.button("🎨 Görseli Oluştur"):
        if g_prompt:
            st.session_state.gorsel_key = random.randint(1, 999999)
        else:
            st.warning("Lütfen bir açıklama gir.")

    if st.session_state.gorsel_key > 0:
        img_url = f"https://pollinations.ai/p/{g_prompt.replace(' ', '%20')}?width=1024&height=1024&nologo=true&seed={st.session_state.gorsel_key}"
        st.image(img_url, caption=f"'{g_prompt}' için çizim", use_column_width=True)

# --- SOHBET GÖSTERİMİ ---
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if st.button(f"🔊 Dinle", key=f"audio_{i}"):
                gTTS(text=msg["content"], lang='tr').save("cevap.mp3")
                st.audio("cevap.mp3")

# --- GİRDİ VE İŞLEME ---
col1, col2 = st.columns([0.9, 0.1])
with col1: prompt = st.chat_input("Mesajını yaz...")
with col2: uploaded_file = st.file_uploader("Dosya", type=['txt', 'md', 'jpg', 'png'], label_visibility="collapsed")

if prompt:
    file_info = f"\n[Dosya: {uploaded_file.name}]" if uploaded_file else ""
    st.session_state.messages.append({"role": "user", "content": prompt + file_info})
    
    user_loc = get_user_location()
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"{prompt} konum: {user_loc}", max_results=2))
            search_context = f"\n\n🔍 Güncel Bilgi ({user_loc}): {results}"
    except:
        search_context = ""

    model = "gpt-4o" if st.session_state.is_dev_mode else "gpt-4o-mini"
    headers = {"Authorization": f"Bearer {st.secrets['GEMINI_API_KEY']}", "Content-Type": "application/json"}
    
    system_prompt = f"""Sen Ahmet İRİŞ'in asistanısın. 
    Ahmet İRİŞ bu projenin kurucusu, sahibi ve Senior Yazılım Mimarıdır. 
    Seni o tasarladı ve geliştirdi. Projelerini (Cerberus, Arduino, Hot Wheels, oyun modifikasyonları) bilirsin.
    Cevaplarında uygun emojiler kullan, profesyonel ve teknik bir dil benimse.
    {search_context}"""
    
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}] + st.session_state.messages,
        "temperature": 0.3
    }
    
    try:
        response = requests.post("https://router.flatkey.ai/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
        else:
            st.error("⚠️ API Bağlantı Hatası!")
    except Exception as e:
        st.error(f"❌ Hata: {e}")
        
