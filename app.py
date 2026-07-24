import streamlit as st
import requests
import base64
import random
import os
import json
from datetime import datetime
from duckduckgo_search import DDGS
from gtts import gTTS

# ============================================
# API ANAHTARI - GEMINI STUDIO'DAN ALINAN
# ============================================
API_KEY = "AQ.Ab8RN6Kx-XrAMbP26NxeBiBulwHHe6u2UNXCT5GORD01IZWsTw"
# Gemini API URL - DOĞRU FORMAT!
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

# ============================================
# SAYFA AYARLARI
# ============================================
st.set_page_config(
    page_title="Ahmet İRİŞ Asistanı",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS - PROFESYONEL TEMA
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
        margin-bottom: 0;
    }
    .sub-title {
        text-align: center;
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: -5px;
        margin-bottom: 20px;
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
if "conversation_count" not in st.session_state:
    st.session_state.conversation_count = 0

# ============================================
# YARDIMCI FONKSİYONLAR
# ============================================
def get_user_location():
    """Kullanıcının konumunu tespit et"""
    try:
        res = requests.get('https://ipinfo.io/', timeout=3)
        data = res.json()
        city = data.get('city', 'Isparta')
        region = data.get('region', 'Türkiye')
        country = data.get('country', 'TR')
        return f"{city}, {region} ({country})"
    except:
        return "Isparta, Türkiye"

def search_web(query, max_results=3):
    """Web araması yap"""
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
    """Görsel oluştur"""
    seed = random.randint(1, 999999)
    img_url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&nologo=true&seed={seed}"
    return img_url

def text_to_speech(text):
    """Metni sese çevir"""
    try:
        tts = gTTS(text=text[:500], lang='tr', slow=False)
        tts.save("cevap.mp3")
        return True
    except:
        return False

def call_gemini_api(messages, temperature=0.7):
    """Gemini API'yi çağır"""
    
    # Gemini formatına dönüştür
    formatted_messages = []
    for msg in messages:
        if msg["role"] == "system":
            # System mesajını context olarak ekle
            formatted_messages.append({
                "role": "user",
                "parts": [{"text": f"Sistem notu: {msg['content']}"}]
            })
        elif msg["role"] == "user":
            formatted_messages.append({
                "role": "user",
                "parts": [{"text": msg["content"]}]
            })
        elif msg["role"] == "assistant":
            formatted_messages.append({
                "role": "model",
                "parts": [{"text": msg["content"]}]
            })
    
    # Gemini payload
    payload = {
        "contents": formatted_messages,
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
            # Gemini yanıtını parse et
            try:
                answer = data['candidates'][0]['content']['parts'][0]['text']
                return answer, None
            except:
                return None, "Yanıt parse edilemedi!"
        else:
            return None, f"API Hatası: {response.status_code} - {response.text[:200]}"
            
    except requests.exceptions.Timeout:
        return None, "Bağlantı zaman aşımı! Lütfen tekrar deneyin."
    except requests.exceptions.ConnectionError:
        return None, "Bağlantı hatası! İnternet bağlantınızı kontrol edin."
    except Exception as e:
        return None, f"Beklenmeyen hata: {str(e)}"

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
    
    # ===== GELİŞTİRİCİ PANELİ =====
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
    
    # ===== GÖRSEL ATÖLYESİ =====
    st.subheader("🎨 Görsel Atölyesi")
    
    with st.form("gorsel_form", clear_on_submit=True):
        g_prompt = st.text_input("Ne çizelim?", placeholder="Örn: uzay gemisi, orman...")
        submitted = st.form_submit_button("🎨 Görseli Oluştur", use_container_width=True)
    
    if submitted and g_prompt:
        with st.spinner("🎨 Görsel oluşturuluyor..."):
            img_url = generate_image(g_prompt)
            st.image(img_url, caption=f"🎨 {g_prompt}", use_container_width=True)
            st.success("✅ Görsel hazır!")
    
    st.divider()
    
    # ===== İSTATİSTİKLER =====
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

# Dev mod göstergesi
if st.session_state.is_dev_mode:
    st.markdown('<span class="dev-badge" style="display:inline-block;margin-bottom:10px;">🚀 DEV MOD AKTİF - GEMINI PRO KULLANILIYOR</span>', unsafe_allow_html=True)

# API Durumu
st.info(f"🔑 Gemini API Anahtarı: {API_KEY[:15]}... (Google Gemini Pro)")

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
            <strong>🤖 Ahmet İRİŞ Asistanı</strong>
            <div>{msg["content"]}</div>
            <div class="chat-time">{msg.get("time", datetime.now().strftime("%H:%M"))}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Ses butonu
        col1, col2 = st.columns([1, 10])
        with col1:
            if st.button(f"🔊", key=f"audio_{i}"):
                with st.spinner("🎤 Ses oluşturuluyor..."):
                    if text_to_speech(msg["content"]):
                        st.audio("cevap.mp3")
                        st.success("✅ Ses hazır!")
                    else:
                        st.error("❌ Ses oluşturulamadı!")

# ============================================
# GİRDİ ALANI
# ============================================
col1, col2 = st.columns([0.9, 0.1])

with col1:
    prompt = st.chat_input("Mesajını yaz...", key="main_chat_input")

with col2:
    uploaded_file = st.file_uploader(
        "📎 Dosya",
        type=['txt', 'md', 'pdf', 'jpg', 'png'],
        label_visibility="collapsed"
    )

# ============================================
# MESAJ İŞLEME
# ============================================
if prompt:
    # Kullanıcı mesajını ekle
    file_info = f"\n\n📎 **Dosya:** {uploaded_file.name}" if uploaded_file else ""
    user_message = prompt + file_info
    
    st.session_state.messages.append({
        "role": "user",
        "content": user_message,
        "time": datetime.now().strftime("%H:%M")
    })
    
    # Konum tespiti
    user_loc = get_user_location()
    
    # Web araması
    with st.spinner("🔍 Web'de aranıyor..."):
        search_context = search_web(f"{prompt} konum: {user_loc}")
    
    # Sistem promptu
    system_prompt = f"""Sen Ahmet İRİŞ'in kişisel asistanısın.

**ÖZELLİKLERİN:**
- Ahmet İRİŞ bu projenin kurucusu, sahibi ve Senior Yazılım Mimarıdır
- Seni o tasarladı ve geliştirdi
- Projeleri: Cerberus, Arduino, Hot Wheels, oyun modifikasyonları
- Uzmanlık alanları: Python, C++, Embedded Systems, AI/ML

**KURALLAR:**
- Profesyonel ve teknik dil kullan
- Uygun emojiler ile cevabı zenginleştir
- Detaylı ve açıklayıcı ol
- Kod örnekleri verirken doğru syntax kullan
- Kullanıcının sorusunu tam anla

**KONUM:** {user_loc}
{search_context}
"""
    
    # Mesaj geçmişini hazırla (Gemini formatı için)
    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages[:-1]:
        if msg["role"] == "user":
            messages.append({"role": "user", "content": msg["content"]})
        elif msg["role"] == "assistant":
            messages.append({"role": "assistant", "content": msg["content"]})
    messages.append({"role": "user", "content": prompt})
    
    # API çağrısı
    with st.spinner(f"🧠 Gemini Pro düşünüyor..."):
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
quick_commands = [
    ("💻 Kod Yaz", "Python'da bir web scraper yaz"),
    ("📊 Analiz", "Veri analizi için en iyi yöntemler neler?"),
    ("🎨 Tasarım", "Logo tasarımı için fikir ver"),
    ("🔍 Ara", "Son yapay zeka haberleri neler?"),
    ("📝 Özet", "Son konuşmayı özetle")
]

for col, (label, action) in zip(cols, quick_commands):
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
    🤖 Ahmet İRİŞ Asistanı v2.0 | Senior Yazılım Mimarı | © 2026
    <br>
    <span style="color:#475569;font-size:0.65rem;">Güç: Google Gemini Pro | Web Arama | Görsel Üretim | Sesli Yanıt</span>
</div>
""", unsafe_allow_html=True)
