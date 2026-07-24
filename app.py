import streamlit as st
import requests
import random
import json
from datetime import datetime
from duckduckgo_search import DDGS
from gtts import gTTS

# ============================================
# OPENROUTER API AYARLARI
# ============================================
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ============================================
# EN İYİ ÜCRETSİZ MODELLER (OpenRouter)
# ============================================
FREE_MODELS = {
    "gemini-2.0-flash": "Google: Gemini 2.0 Flash (En iyi ücretsiz)",
    "gemini-1.5-flash": "Google: Gemini 1.5 Flash (Hızlı)",
    "gemini-1.5-pro": "Google: Gemini 1.5 Pro (Gelişmiş)",
    "claude-3-haiku": "Anthropic: Claude 3 Haiku (Hızlı)",
    "llama-3.1-70b": "Meta: Llama 3.1 70B (Güçlü)",
    "llama-3.1-8b": "Meta: Llama 3.1 8B (Hafif)",
    "mistral-7b": "Mistral: Mistral 7B (Hızlı)",
    "mixtral-8x7b": "Mistral: Mixtral 8x7B (Güçlü)",
    "deepseek-chat": "DeepSeek: DeepSeek Chat (Yeni)"
}

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
    .badge {
        display: inline-block;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white;
        padding: 4px 16px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
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
    .model-badge {
        display: inline-block;
        background: #059669;
        color: white;
        padding: 2px 12px;
        border-radius: 12px;
        font-size: 0.65rem;
    }
    .footer {
        text-align: center;
        color: #475569;
        font-size: 0.75rem;
        padding: 20px 0;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 20px;
    }
    @media (max-width: 768px) {
        .main-title { font-size: 1.8rem; }
        .chat-user, .chat-assistant { max-width: 90%; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# OTURUM
# ============================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemini-2.0-flash"

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
    except:
        return ""

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

def call_openrouter_api(messages, model, temperature=0.7):
    """OpenRouter API çağrısı - En iyi ücretsiz modeller"""
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost:8501",
        "X-Title": "Ahmet IRIS Asistani"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            answer = data['choices'][0]['message']['content']
            return answer, None
        else:
            return None, f"API Hatası ({response.status_code}): {response.text[:300]}"
            
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
        <span class="badge">v3.0</span>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== MODEL SEÇİMİ =====
    st.subheader("🧠 Model Seçimi")
    
    model_options = list(FREE_MODELS.keys())
    model_labels = list(FREE_MODELS.values())
    
    selected_model = st.selectbox(
        "En İyi Ücretsiz Modeller",
        model_options,
        format_func=lambda x: FREE_MODELS[x],
        index=model_options.index(st.session_state.selected_model) if st.session_state.selected_model in model_options else 0
    )
    
    if selected_model != st.session_state.selected_model:
        st.session_state.selected_model = selected_model
        st.rerun()
    
    st.markdown(f'<span class="model-badge">✅ {FREE_MODELS[selected_model]}</span>', unsafe_allow_html=True)
    
    st.divider()
    
    # ===== GÖRSEL ATÖLYESİ =====
    st.subheader("🎨 Görsel Atölyesi")
    with st.form("gorsel_form", clear_on_submit=True):
        g_prompt = st.text_input("Ne çizelim?", placeholder="Örn: uzay gemisi...")
        if st.form_submit_button("🎨 Görseli Oluştur", use_container_width=True):
            if g_prompt:
                img_url = generate_image(g_prompt)
                st.image(img_url, caption=f"🎨 {g_prompt}", use_container_width=True)
    
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
st.markdown('<p class="sub-title">Senior Yazılım Mimarı | OpenRouter AI | 2026</p>', unsafe_allow_html=True)

# Aktif model gösterimi
st.markdown(f'<span class="model-badge" style="background:#2563eb;">🧠 Aktif Model: {FREE_MODELS[st.session_state.selected_model]}</span>', unsafe_allow_html=True)

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
            <strong>🤖 {msg.get("model", "Asistan")}</strong>
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

ÖZELLİKLERİN:
- Ahmet İRİŞ bu projenin kurucusu, sahibi ve Senior Yazılım Mimarıdır
- Seni o tasarladı ve geliştirdi
- Projeleri: Cerberus, Arduino, Hot Wheels, oyun modifikasyonları
- Uzmanlık alanları: Python, C++, Embedded Systems, AI/ML

KURALLAR:
- Profesyonel ve teknik dil kullan
- Uygun emojiler ile cevabı zenginleştir
- Detaylı ve açıklayıcı ol
- Kod örnekleri verirken doğru syntax kullan
- Kullanıcının sorusunu tam anla

KONUM: {user_loc}
{search_context}
"""
    
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    for msg in st.session_state.messages:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    model_name = st.session_state.selected_model
    model_display = FREE_MODELS[model_name]
    
    with st.spinner(f"🧠 {model_display} düşünüyor..."):
        answer, error = call_openrouter_api(messages, model_name)
    
    if answer:
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "model": model_display,
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
    ("📊 Analiz", "Veri analizi yöntemleri neler?"),
    ("🎨 Tasarım", "Logo tasarımı için fikir ver"),
    ("🔍 Ara", "Son yapay zeka haberleri"),
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
    🤖 Ahmet İRİŞ Asistanı v3.0 | OpenRouter AI | En İyi Ücretsiz Modeller | © 2026
</div>
""", unsafe_allow_html=True)
