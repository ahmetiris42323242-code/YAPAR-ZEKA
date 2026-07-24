import streamlit as st
import requests
import random
from datetime import datetime
from duckduckgo_search import DDGS
from gtts import gTTS

# ============================================
# API ANAHTARI - GEMINI STUDIO'DAN ALINAN
# ============================================
API_KEY = "AQ.Ab8RN6Kx-XrAMbP26NxeBiBulwHHe6u2UNXCT5GORD01IZWsTw"

# ============================================
# DOĞRU GEMINI API URL'LERİ
# ============================================
# Seçenek 1: Gemini Pro (En iyi model)
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

# Seçenek 2: Gemini 1.5 Flash (Hızlı ve ücretsiz)
# GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

# Seçenek 3: Gemini 1.5 Pro (En gelişmiş)
# GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={API_KEY}"

# ============================================
# SAYFA AYARLARI
# ============================================
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
    .main-title {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        padding: 10px 0;
    }
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: -5px;
        margin-bottom: 20px;
    }
    .chat-user {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 14px 20px;
        margin: 8px 0 8px auto;
        max-width: 80%;
        word-wrap: break-word;
    }
    .chat-assistant {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px 18px 18px 4px;
        padding: 14px 20px;
        margin: 8px auto 8px 0;
        max-width: 80%;
        word-wrap: break-word;
    }
    .chat-time {
        font-size: 0.6rem;
        color: #64748b;
        margin-top: 4px;
        text-align: right;
    }
    .sidebar-header {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    .stat-card {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 16px;
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
    .footer {
        text-align: center;
        color: #475569;
        font-size: 0.75rem;
        padding: 20px 0;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 20px;
    }
    .dev-badge {
        background: #059669;
        color: white;
        padding: 2px 12px;
        border-radius: 12px;
        font-size: 0.7rem;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    @media (max-width: 768px) {
        .main-title { font-size: 1.8rem; }
        .chat-user, .chat-assistant { max-width: 90%; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# OTURUM BAŞLAT
# ============================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_dev_mode" not in st.session_state:
    st.session_state.is_dev_mode = False

# ============================================
# YARDIMCI FONKSİYONLAR
# ============================================
def get_user_location():
    try:
        res = requests.get('https://ipinfo.io/', timeout=3)
        data = res.json()
        return f"{data.get('city', 'Isparta')}, {data.get('region', 'Türkiye')}"
    except:
        return "Isparta, Türkiye"

def search_web(query, max_results=3):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if results:
                context = "\n\n🔍 **Güncel Bilgiler:**\n"
                for i, r in enumerate(results, 1):
                    context += f"{i}. {r.get('title', '')}\n   {r.get('body', '')[:200]}...\n"
                return context
            return ""
    except Exception as e:
        return f"\n\n⚠️ Arama hatası: {str(e)}"

def generate_image(prompt):
    seed = random.randint(1, 999999)
    return f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&nologo=true&seed={seed}"

def text_to_speech(text):
    try:
        tts = gTTS(text=text[:500], lang='tr', slow=False)
        tts.save("cevap.mp3")
        return True
    except:
        return False

def call_gemini_api(messages, temperature=0.7):
    """Gemini API'yi çağır - DOĞRU FORMAT"""
    
    # Gemini formatına dönüştür
    contents = []
    
    # Sistem mesajını ekle
    system_text = ""
    for msg in messages:
        if msg["role"] == "system":
            system_text = msg["content"]
            break
    
    # Kullanıcı ve asistan mesajlarını ekle
    for msg in messages:
        if msg["role"] == "user":
            contents.append({
                "role": "user",
                "parts": [{"text": msg["content"]}]
            })
        elif msg["role"] == "assistant":
            contents.append({
                "role": "model",
                "parts": [{"text": msg["content"]}]
            })
    
    # Sistem mesajını ilk kullanıcı mesajına ekle
    if system_text and contents:
        contents[0]["parts"][0]["text"] = f"{system_text}\n\n{contents[0]['parts'][0]['text']}"
    
    # Gemini payload
    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 2000,
            "topP": 0.95,
            "topK": 40
        }
    }
    
    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            try:
                answer = data['candidates'][0]['content']['parts'][0]['text']
                return answer, None
            except:
                return None, f"Yanıt parse edilemedi: {data}"
        else:
            return None, f"API Hatası ({response.status_code}): {response.text[:300]}"
            
    except requests.exceptions.Timeout:
        return None, "Bağlantı zaman aşımı! Lütfen tekrar deneyin."
    except requests.exceptions.ConnectionError:
        return None, "Bağlantı hatası! İnternet bağlantınızı kontrol edin."
    except Exception as e:
        return None, f"Hata: {str(e)}"

# ============================================
# SİDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div style="font-size:3rem;">🤖</div>
        <h3>Ahmet İRİŞ</h3>
        <p>Senior Yazılım Mimarı</p>
        <span class="badge">v2.0</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("⚙️ Geliştirici Paneli")
    
    with st.expander("🔐 Geliştirici Modu", expanded=False):
        password = st.text_input("Şifre", type="password", placeholder="••••", key="dev_password")
        if password == "7536":
            st.session_state.is_dev_mode = True
            st.success("✅ SÜPER ZEKA AKTİF")
            st.balloons()
        elif password:
            st.error("❌ Geçersiz şifre!")
        
        if st.session_state.is_dev_mode:
            st.markdown(f'<span class="dev-badge">🚀 DEV MOD AKTİF</span>', unsafe_allow_html=True)
            if st.button("🔒 Modu Kapat", use_container_width=True):
                st.session_state.is_dev_mode = False
                st.rerun()
    
    st.divider()
    
    st.subheader("🎨 Görsel Atölyesi")
    with st.form("gorsel_form", clear_on_submit=True):
        g_prompt = st.text_input("Ne çizelim?")
        if st.form_submit_button("🎨 Görseli Oluştur", use_container_width=True):
            if g_prompt:
                img_url = generate_image(g_prompt)
                st.image(img_url, caption=f"🎨 {g_prompt}", use_container_width=True)
    
    st.divider()
    
    st.subheader("📊 İstatistikler")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💬 Konuşma", len([m for m in st.session_state.messages if m["role"] == "user"]))
    with col2:
        st.metric("📝 Mesaj", len(st.session_state.messages))

# ============================================
# ANA BAŞLIK
# ============================================
st.markdown('<h1 class="main-title">🤖 Ahmet İRİŞ Asistanı</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Senior Yazılım Mimarı | 2026</p>', unsafe_allow_html=True)

if st.session_state.is_dev_mode:
    st.markdown('<span class="dev-badge" style="display:inline-block;margin-bottom:10px;">🚀 DEV MOD AKTİF</span>', unsafe_allow_html=True)

# API durumu
st.info(f"🔑 Gemini API: {API_KEY[:15]}... | Model: gemini-pro")

st.divider()

# ============================================
# SOHBET GEÇMİŞİ
# ============================================
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="chat-user">
            <strong>👤 Siz</strong>
            <div>{msg["content"]}</div>
            <div class="chat-time">{msg.get("time", datetime.now().strftime("%H:%M"))}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-assistant">
            <strong>🤖 Asistan</strong>
            <div>{msg["content"]}</div>
            <div class="chat-time">{msg.get("time", datetime.now().strftime("%H:%M"))}</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 10])
        with col1:
            if st.button(f"🔊", key=f"audio_{i}"):
                if text_to_speech(msg["content"]):
                    st.audio("cevap.mp3")

# ============================================
# GİRDİ
# ============================================
prompt = st.chat_input("Mesajını yaz...")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "time": datetime.now().strftime("%H:%M")
    })
    
    user_loc = get_user_location()
    
    with st.spinner("🔍 Araştırılıyor..."):
        search_context = search_web(prompt)
    
    system_prompt = f"""Sen Ahmet İRİŞ'in kişisel asistanısın.
- Ahmet İRİŞ bu projenin kurucusu ve Senior Yazılım Mimarıdır
- Projeleri: Cerberus, Arduino, Hot Wheels
- Uzmanlık: Python, C++, Embedded Systems, AI/ML
- Profesyonel ve teknik dil kullan
- Kod örnekleri verirken doğru syntax kullan

Konum: {user_loc}
{search_context}
"""
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    with st.spinner("🧠 Gemini Pro düşünüyor..."):
        answer, error = call_gemini_api(messages)
    
    if answer:
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "time": datetime.now().strftime("%H:%M")
        })
        st.rerun()
    else:
        st.error(f"❌ {error}")

# ============================================
# HIZLI KOMUTLAR
# ============================================
st.divider()
st.caption("⚡ Hızlı Komutlar")

cols = st.columns(5)
quick = [
    ("💻 Kod", "Python'da web scraper yaz"),
    ("📊 Analiz", "Veri analizi yöntemleri"),
    ("🎨 Tasarım", "Logo fikirleri ver"),
    ("🔍 Ara", "Yapay zeka haberleri"),
    ("📝 Özet", "Son konuşmayı özetle")
]

for col, (label, action) in zip(cols, quick):
    with col:
        if st.button(label, use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": action,
                "time": datetime.now().strftime("%H:%M")
            })
            st.rerun()

# ============================================
# FOOTER
# ============================================
st.markdown("""
<div class="footer">
    🤖 Ahmet İRİŞ Asistanı v2.0 | Google Gemini Pro | © 2026
</div>
""", unsafe_allow_html=True)
