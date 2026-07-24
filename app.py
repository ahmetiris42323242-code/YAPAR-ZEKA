import streamlit as st
import requests
import base64
from duckduckgo_search import DDGS
from gtts import gTTS
import random
from datetime import datetime

# ============================================
# OPENROUTER API AYARLARI
# ============================================
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ============================================
# MODEL - GPT-4o-mini (ÜCRETSİZ)
# ============================================
MODEL = "openai/gpt-4o-mini"

# --- YARDIMCI FONKSİYONLAR ---
def get_user_location():
    try:
        res = requests.get('https://ipinfo.io/', timeout=2)
        data = res.json()
        return f"{data.get('city', 'Isparta')}, {data.get('region', 'Türkiye')}"
    except:
        return "Şarkikaraağaç, Isparta"

# --- ARAYÜZ AYARLARI ---
st.set_page_config(
    page_title="Ahmet İRİŞ Asistanı", 
    page_icon="🤖", 
    layout="wide"
)

# ============================================
# PROFESYONEL CSS
# ============================================
st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
    .main-title {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        padding: 10px 0 0 0;
        margin-bottom: 0;
        letter-spacing: -0.5px;
    }
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: -5px;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .badge {
        display: inline-block;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white;
        padding: 4px 16px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-success { background: #059669; }
    .sidebar-header {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        padding: 24px 20px;
        border-radius: 16px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    .sidebar-header .avatar { font-size: 3.5rem; margin-bottom: 4px; }
    .sidebar-header h3 { margin: 4px 0; font-weight: 600; font-size: 1.1rem; }
    .sidebar-header p { opacity: 0.8; font-size: 0.8rem; margin: 0; }
    .sidebar-header .version {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        padding: 2px 12px;
        border-radius: 12px;
        font-size: 0.7rem;
        margin-top: 6px;
    }
    .chat-user {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 14px 20px;
        margin: 8px 0 8px auto;
        max-width: 80%;
        word-wrap: break-word;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
        animation: slideInRight 0.3s ease;
    }
    .chat-assistant {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px 18px 18px 4px;
        padding: 14px 20px;
        margin: 8px auto 8px 0;
        max-width: 80%;
        word-wrap: break-word;
        animation: slideInLeft 0.3s ease;
    }
    .chat-time {
        font-size: 0.6rem;
        color: #64748b;
        margin-top: 6px;
        text-align: right;
    }
    .chat-user .chat-time { color: rgba(255,255,255,0.6); }
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    .stat-card {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
        transition: all 0.3s;
    }
    .stat-card:hover { background: rgba(255,255,255,0.06); transform: translateY(-2px); }
    .stat-number {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-label {
        color: #94a3b8;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }
    .stButton > button {
        border-radius: 50px !important;
        background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s !important;
        padding: 10px 24px !important;
    }
    .stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.4) !important;
    }
    .stTextInput > div > div > input {
        border-radius: 50px !important;
        border: 2px solid rgba(37, 99, 235, 0.3) !important;
        padding: 12px 20px !important;
        background: rgba(255,255,255,0.05) !important;
        color: white !important;
        font-size: 1rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2) !important;
    }
    .footer {
        text-align: center;
        color: #475569;
        font-size: 0.75rem;
        padding: 20px 0 10px 0;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 20px;
    }
    @media (max-width: 768px) {
        .main-title { font-size: 1.8rem; }
        .chat-user, .chat-assistant { max-width: 90%; padding: 10px 14px; font-size: 0.9rem; }
        .stat-number { font-size: 1.5rem; }
    }
</style>
""", unsafe_allow_html=True)

# --- OTURUM ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# ============================================
# SİDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="avatar">🤖</div>
        <h3>Ahmet İRİŞ</h3>
        <p>Senior Yazılım Mimarı</p>
        <span class="version">v3.0</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("🎨 Görsel Atölyesi")
    with st.form("gorsel_form", clear_on_submit=True):
        g_prompt = st.text_input("Ne çizelim?", placeholder="Örn: uzay gemisi, orman...")
        submitted = st.form_submit_button("🎨 Görseli Oluştur", use_container_width=True)
    
    if submitted and g_prompt:
        with st.spinner("🎨 Görsel oluşturuluyor..."):
            seed = random.randint(1, 999999)
            img_url = f"https://pollinations.ai/p/{g_prompt.replace(' ', '%20')}?width=1024&height=1024&nologo=true&seed={seed}"
            st.image(img_url, caption=f"🎨 {g_prompt}", use_container_width=True)
            st.success("✅ Görsel hazır!")
    
    st.divider()
    
    st.subheader("📊 İstatistikler")
    col1, col2 = st.columns(2)
    with col1:
        user_msgs = len([m for m in st.session_state.messages if m.get("role") == "user"])
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{user_msgs}</div>
            <div class="stat-label">💬 Soru</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        assistant_msgs = len([m for m in st.session_state.messages if m.get("role") == "assistant"])
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{assistant_msgs}</div>
            <div class="stat-label">🤖 Cevap</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.caption(f"📍 Konum: {get_user_location()}")

# ============================================
# ANA BAŞLIK
# ============================================
st.markdown('<h1 class="main-title">🤖 Ahmet İRİŞ Asistanı</h1>', unsafe_allow_html=True)
st.markdown("""
<div class="sub-title">
    <span class="badge">Web Tabanlı</span>
    <span class="badge badge-success">GPT-4o-mini</span>
    <span style="color:#94a3b8;margin:0 8px;">|</span>
    <span style="color:#94a3b8;">By Ahmet İRİŞ | Senior Yazılım Mimarı 2026</span>
</div>
""", unsafe_allow_html=True)

# ============================================
# SOHBET GÖSTERİMİ
# ============================================
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:40px 20px;">
        <div style="font-size:3rem;">👋</div>
        <h3 style="color:#94a3b8;">Merhaba! Sohbete başlayalım.</h3>
        <p style="color:#64748b;">Aşağıdan bir soru sorun, AI asistan cevaplasın.</p>
        <p style="color:#64748b;font-size:0.85rem;">💡 Teknik, yaratıcı veya genel sorular sorabilirsiniz.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                col1, col2, col3 = st.columns([1, 1, 8])
                with col1:
                    if st.button("🔊", key=f"audio_{i}", help="Sesli dinle"):
                        with st.spinner("🎤 Ses oluşturuluyor..."):
                            try:
                                tts = gTTS(text=msg["content"][:500], lang='tr', slow=False)
                                tts.save("cevap.mp3")
                                st.audio("cevap.mp3")
                            except:
                                st.error("❌ Ses oluşturulamadı!")

# ============================================
# GİRDİ VE İŞLEME
# ============================================
col1, col2 = st.columns([0.9, 0.1])
with col1:
    prompt = st.chat_input("Mesajını yaz...", key="main_chat_input")
with col2:
    uploaded_file = st.file_uploader("📎 Dosya", type=['txt', 'md', 'jpg', 'png'], label_visibility="collapsed", key="file_uploader")

# ============================================
# MESAJ İŞLEME
# ============================================
if prompt:
    file_info = f"\n\n📎 **Dosya:** {uploaded_file.name}" if uploaded_file else ""
    st.session_state.messages.append({"role": "user", "content": prompt + file_info})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("🧠 GPT-4o-mini düşünüyor..."):
        user_loc = get_user_location()
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(f"{prompt} konum: {user_loc}", max_results=2))
                search_context = f"\n\n🔍 **Güncel Bilgi** ({user_loc}):\n"
                for i, r in enumerate(results, 1):
                    search_context += f"{i}. {r.get('title', '')}\n   {r.get('body', '')[:200]}...\n"
        except:
            search_context = ""

        system_prompt = f"""Sen Ahmet İRİŞ'in asistanısın. 
Ahmet İRİŞ bu projenin kurucusu, sahibi ve Senior Yazılım Mimarıdır. 
Seni o tasarladı ve geliştirdi. Projelerini (Cerberus, Arduino, Hot Wheels, oyun modifikasyonları) bilirsin.
Cevaplarında uygun emojiler kullan, profesyonel ve teknik bir dil benimse.
{search_context}"""
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in st.session_state.messages[:-1]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost:8501",
            "X-Title": "Ahmet IRIS Asistani"
        }
        
        payload = {
            "model": MODEL,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                answer = response.json()['choices'][0]['message']['content']
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
            else:
                st.error(f"⚠️ API Hatası: {response.status_code}")
                st.code(response.text[:300])
                st.stop()
                
        except Exception as e:
            st.error(f"❌ Hata: {str(e)}")
            st.stop()

# ============================================
# FOOTER
# ============================================
st.markdown("""
<div class="footer">
    🤖 Ahmet İRİŞ Asistanı v3.0 | 
    <span style="color:#dc2626;">❤️</span> 
    Senior Yazılım Mimarı | © 2026
    <br>
    <span style="color:#475569;font-size:0.65rem;">
        ⚡ GPT-4o-mini | Web Arama | Görsel Üretim | Sesli Yanıt
    </span>
</div>
""", unsafe_allow_html=True)
