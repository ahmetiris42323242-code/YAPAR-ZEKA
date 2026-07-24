import streamlit as st
import requests
import random
from datetime import datetime
from duckduckgo_search import DDGS
from gtts import gTTS

# ============================================
# API AYARLARI
# ============================================
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"

# --- YARDIMCI FONKSİYONLAR ---
def get_user_location():
    try:
        res = requests.get('https://ipinfo.io/', timeout=2)
        data = res.json()
        return f"{data.get('city', 'Isparta')}, {data.get('region', 'Türkiye')}"
    except:
        return "Isparta, Türkiye"

# --- SAYFA AYARLARI ---
st.set_page_config(
    page_title="Ahmet İRİŞ Asistanı",
    page_icon="🤖",
    layout="wide"
)

# ============================================
# CSS
# ============================================
st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
    .main-title {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        padding: 10px 0 0 0;
    }
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: -5px;
        padding-bottom: 15px;
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
    }
    .badge-success { background: #059669; }
    .sidebar-header {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    .sidebar-header .avatar { font-size: 3rem; }
    .sidebar-header h3 { margin: 4px 0; font-size: 1rem; }
    .sidebar-header p { opacity: 0.8; font-size: 0.8rem; margin: 0; }
    .chat-user {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px;
        margin: 8px 0 8px auto;
        max-width: 80%;
        word-wrap: break-word;
    }
    .chat-assistant {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px 18px 18px 4px;
        padding: 12px 18px;
        margin: 8px auto 8px 0;
        max-width: 80%;
        word-wrap: break-word;
    }
    .chat-time { font-size: 0.6rem; color: #64748b; margin-top: 4px; text-align: right; }
    .chat-user .chat-time { color: rgba(255,255,255,0.6); }
    .stat-card {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 14px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-label { color: #94a3b8; font-size: 0.7rem; text-transform: uppercase; margin-top: 4px; }
    .stButton > button {
        border-radius: 50px !important;
        background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 8px 20px !important;
    }
    .stTextInput > div > div > input {
        border-radius: 50px !important;
        border: 2px solid rgba(37, 99, 235, 0.3) !important;
        padding: 10px 18px !important;
        background: rgba(255,255,255,0.05) !important;
        color: white !important;
    }
    .footer {
        text-align: center;
        color: #475569;
        font-size: 0.7rem;
        padding: 15px 0;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 20px;
    }
    @media (max-width: 768px) {
        .main-title { font-size: 1.8rem; }
        .chat-user, .chat-assistant { max-width: 90%; padding: 10px 14px; font-size: 0.9rem; }
    }
</style>
""", unsafe_allow_html=True)

# --- OTURUM BAŞLAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="avatar">🤖</div>
        <h3>Ahmet İRİŞ</h3>
        <p>Senior Yazılım Mimarı</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Görsel Atölyesi
    st.subheader("🎨 Görsel Atölyesi")
    with st.form("gorsel_form", clear_on_submit=True):
        g_prompt = st.text_input("Ne çizelim?", placeholder="Uzay gemisi...")
        if st.form_submit_button("🎨 Oluştur", use_container_width=True):
            if g_prompt:
                with st.spinner("🎨 Oluşturuluyor..."):
                    seed = random.randint(1, 999999)
                    img_url = f"https://pollinations.ai/p/{g_prompt.replace(' ', '%20')}?width=1024&height=1024&nologo=true&seed={seed}"
                    st.image(img_url, caption=f"🎨 {g_prompt}", use_container_width=True)
    
    st.divider()
    
    # İstatistikler
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
    st.caption(f"📍 {get_user_location()}")

# ============================================
# ANA BASLIK
# ============================================
st.markdown('<h1 class="main-title">🤖 Ahmet İRİŞ Asistanı</h1>', unsafe_allow_html=True)
st.markdown("""
<div class="sub-title">
    <span class="badge">Web Tabanlı</span>
    <span class="badge badge-success">GPT-4o-mini</span>
    <span style="color:#94a3b8;margin:0 8px;">|</span>
    <span style="color:#94a3b8;">2026</span>
</div>
""", unsafe_allow_html=True)

# ============================================
# SOHBET
# ============================================
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:40px 20px;">
        <div style="font-size:3rem;">👋</div>
        <h3 style="color:#94a3b8;">Merhaba! Sohbete başlayalım.</h3>
        <p style="color:#64748b;">Aşağıdan bir soru sorun.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for i, msg in enumerate(st.session_state.messages):
        if msg.get("role") == "user":
            with st.chat_message("user"):
                st.markdown(msg.get("content", ""))
        else:
            with st.chat_message("assistant"):
                st.markdown(msg.get("content", ""))
                if st.button("🔊", key=f"audio_{i}", help="Sesli dinle"):
                    try:
                        tts = gTTS(text=msg.get("content", "")[:500], lang='tr', slow=False)
                        tts.save("cevap.mp3")
                        st.audio("cevap.mp3")
                    except:
                        st.error("❌ Ses oluşturulamadı")

# ============================================
# GIRDI
# ============================================
prompt = st.chat_input("Mesajını yaz...")

if prompt:
    # Kullanıcı mesajını ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# ============================================
# API İSLEME
# ============================================
if st.session_state.messages and st.session_state.messages[-1].get("role") == "user":
    with st.spinner("🧠 Düşünüyor..."):
        try:
            user_loc = get_user_location()
            
            # Web araması
            search_context = ""
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(prompt, max_results=2))
                    if results:
                        search_context = f"\n🔍 Güncel Bilgi ({user_loc}):\n"
                        for r in results[:2]:
                            search_context += f"• {r.get('title', '')[:100]}\n"
            except:
                pass
            
            # Sistem promptu
            system_prompt = f"""Sen Ahmet İRİŞ'in asistanısın. 
Ahmet İRİŞ projenin kurucusu ve Senior Yazılım Mimarıdır.
Cevaplarında emoji kullan, profesyonel ve teknik ol.
{search_context}"""
            
            # Mesajları hazırla
            messages = [{"role": "system", "content": system_prompt.strip()}]
            
            for msg in st.session_state.messages[:-1]:
                content = msg.get("content", "")
                if content and content.strip():
                    messages.append({"role": msg["role"], "content": content.strip()})
            
            messages.append({"role": "user", "content": prompt.strip()})
            
            # API çağrısı
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://localhost:8501"
            }
            
            payload = {
                "model": MODEL,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                answer = response.json()["choices"][0]["message"]["content"]
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
            else:
                st.error(f"⚠️ API Hatası: {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Hata: {str(e)}")

# ============================================
# FOOTER
# ============================================
st.markdown("""
<div class="footer">
    🤖 Ahmet İRİŞ Asistanı | GPT-4o-mini | © 2026
</div>
""", unsafe_allow_html=True)
