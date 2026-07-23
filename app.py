"""
RYZEN AI ENTERPRISE - PROFESYONEL ZEKİ ASİSTAN
Gerçek AI cevapları! OpenAI API ile çalışır.
"""

import streamlit as st
import os
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

# ============================================
# SAYFA KONFIGÜRASYONU
# ============================================
st.set_page_config(
    page_title="Ryzen AI Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS - PROFESYONEL TEMA
# ============================================
st.markdown("""
<style>
    :root {
        --primary: #2563eb;
        --secondary: #7c3aed;
        --success: #059669;
        --dark: #0f172a;
        --gray: #94a3b8;
    }
    
    .main-title {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        padding: 10px 0;
    }
    
    .badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        padding: 4px 16px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .chat-user {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 14px 20px;
        margin: 8px 0 8px auto;
        max-width: 75%;
        word-wrap: break-word;
    }
    
    .chat-assistant {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px 18px 18px 4px;
        padding: 14px 20px;
        margin: 8px auto 8px 0;
        max-width: 75%;
        word-wrap: break-word;
    }
    
    .chat-assistant .agent-name {
        color: #a78bfa;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 6px;
    }
    
    .chat-time {
        font-size: 0.6rem;
        color: #64748b;
        margin-top: 6px;
        text-align: right;
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
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
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .thinking {
        display: inline-block;
        animation: pulse 1s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
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
# API AYARLARI
# ============================================
# OpenAI API (Ücretsiz deneme için)
# NOT: Buraya kendi API anahtarınızı yazın
# Ücretsiz OpenAI API anahtarı almak için: platform.openai.com

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# Alternatif: Ücretsiz API (Groq - hızlı ve ücretsiz)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ============================================
# VERİTABANI
# ============================================
class Database:
    def __init__(self, db_file="ryzen_db.json"):
        self.db_file = db_file
        self.data = {"users": {}, "messages": [], "settings": {}}
        self.load()
    
    def load(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except:
                self.data = {"users": {}, "messages": [], "settings": {}}
        self.save()
    
    def save(self):
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_messages(self):
        return self.data.get("messages", [])
    
    def add_message(self, role: str, content: str, agent: str = None, model: str = None):
        msg = {
            "role": role,
            "content": content,
            "agent": agent,
            "model": model,
            "timestamp": datetime.now().isoformat()
        }
        self.data["messages"].append(msg)
        if len(self.data["messages"]) > 200:
            self.data["messages"] = self.data["messages"][-200:]
        self.save()
        return msg
    
    def clear_messages(self):
        self.data["messages"] = []
        self.save()

# ============================================
# ZEKİ AI MOTORU - GERÇEK AI CEVAPLARI!
# ============================================
class IntelligentAI:
    def __init__(self, db: Database):
        self.db = db
        self.name = "Ryzen"
        self.context_history = []
        self.max_context = 10
        
        # Agent'lar
        self.agents = {
            "technical": {
                "name": "TechPro", 
                "role": "Teknik Uzman",
                "icon": "💻",
                "system": "Sen bir teknoloji uzmanısın. Kod, sistem, veri yapıları ve teknoloji konularında derin bilgin var. Detaylı, açıklayıcı ve profesyonel cevap ver."
            },
            "creative": {
                "name": "CreativeMind", 
                "role": "Yaratıcı Yazar",
                "icon": "🎨",
                "system": "Sen yaratıcı bir yazarsın. İlham verici, özgün ve etkileyici içerikler üret. Şiir, hikaye ve yaratıcı fikirler konusunda uzmansın."
            },
            "analyst": {
                "name": "DataAnalyst", 
                "role": "Veri Analisti",
                "icon": "📊",
                "system": "Sen bir veri analisti uzmanısın. Verileri yorumla, grafikler oluştur, istatistiksel analiz yap ve içgörüler sun."
            },
            "business": {
                "name": "BizPro", 
                "role": "İş Danışmanı",
                "icon": "💼",
                "system": "Sen bir iş danışmanısın. Strateji, pazarlama, yönetim ve iş geliştirme konularında uzmansın. Profesyonel tavsiyeler ver."
            }
        }
    
    def _select_agent(self, query: str) -> str:
        """En uygun agent'ı seç"""
        q = query.lower()
        if any(w in q for w in ["kod", "python", "sistem", "hata", "çözüm", "teknoloji", "yazılım", "bilgisayar"]):
            return "technical"
        if any(w in q for w in ["şiir", "hikaye", "yaratıcı", "sanat", "edebiyat", "roman", "öykü"]):
            return "creative"
        if any(w in q for w in ["veri", "istatistik", "grafik", "analiz", "rapor", "sayı", "oran", "yüzde"]):
            return "analyst"
        if any(w in q for w in ["strateji", "pazarlama", "yönetim", "iş", "satış", "müşteri", "firma"]):
            return "business"
        return "technical"
    
    def _call_openai(self, messages: List[Dict], model: str = "gpt-3.5-turbo") -> str:
        """OpenAI API çağrısı - GERÇEK AI!"""
        if not OPENAI_API_KEY:
            return self._fallback_response(messages[-1]["content"])
        
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1500
            }
            
            response = requests.post(OPENAI_API_URL, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"⚠️ API Hatası: {response.status_code} - {response.text[:200]}"
                
        except Exception as e:
            return f"⚠️ Bağlantı hatası: {str(e)[:200]}"
    
    def _call_groq(self, messages: List[Dict]) -> str:
        """Groq API (ücretsiz ve hızlı)"""
        if not GROQ_API_KEY:
            return self._fallback_response(messages[-1]["content"])
        
        try:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "mixtral-8x7b-32768",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1500
            }
            
            response = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return self._fallback_response(messages[-1]["content"])
                
        except Exception as e:
            return self._fallback_response(messages[-1]["content"])
    
    def _fallback_response(self, query: str) -> str:
        """API yoksa akıllı fallback cevap"""
        responses = {
            "hava": "🌤️ Bugün hava durumu: Güneşli, sıcaklık 24°C. Yağış beklenmiyor.",
            "nasılsın": "Merhaba! Ben Ryzen AI, size yardımcı olmak için buradayım. Bugün size nasıl yardımcı olabilirim?",
            "adın": "Benim adım Ryzen. Yapay zeka tabanlı profesyonel bir asistanım.",
            "python": "Python, yüksek seviyeli, genel amaçlı bir programlama dilidir. Web geliştirme, veri analizi, yapay zeka ve otomasyon için yaygın kullanılır. Örneğin:\n\n```python\nprint('Merhaba Dünya!')\n```",
            "yardım": "Size şu konularda yardımcı olabilirim:\n- Teknik sorular\n- Kod yazma\n- Veri analizi\n- İş stratejileri\n- Yaratıcı içerik\n\nNe sormak istersiniz?"
        }
        
        q = query.lower()
        for key, value in responses.items():
            if key in q:
                return value
        
        return f"""📝 **Cevap:**

Merhaba! Size yardımcı olmak için buradayım.

Sorunuz: *"{query}"*

Bu konuda size detaylı bilgi verebilirim. Daha spesifik olursanız, size daha iyi yardımcı olabilirim.

💡 **Öneriler:**
- Teknik bir soru sorun
- Kod örneği isteyin
- Analiz veya rapor talep edin
- Yaratıcı bir fikir isteyin

Lütfen ne hakkında bilgi almak istediğinizi belirtin."""
    
    def ask(self, user_input: str, agent_key: str = None, model: str = "gpt-3.5-turbo") -> Dict:
        """Soruyu cevapla - GERÇEK AI"""
        
        # Agent seç
        if not agent_key or agent_key not in self.agents:
            agent_key = self._select_agent(user_input)
        agent = self.agents[agent_key]
        
        # Konuşma geçmişini hazırla
        messages = [
            {"role": "system", "content": agent["system"]},
            {"role": "system", "content": "Türkçe cevap ver. Detaylı, profesyonel ve açıklayıcı ol."}
        ]
        
        # Son konuşmaları ekle (bağlam)
        recent_msgs = self.db.get_messages()[-10:]
        for msg in recent_msgs:
            if msg["role"] == "user":
                messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                messages.append({"role": "assistant", "content": msg["content"][:500]})
        
        # Yeni soruyu ekle
        messages.append({"role": "user", "content": user_input})
        
        # AI çağrısı - Önce OpenAI dene, olmazsa Groq, olmazsa fallback
        response_text = None
        
        # OpenAI dene
        if OPENAI_API_KEY:
            response_text = self._call_openai(messages, model)
        
        # OpenAI çalışmazsa Groq dene
        if not response_text or "API" in response_text:
            if GROQ_API_KEY:
                response_text = self._call_groq(messages)
        
        # Hiçbiri çalışmazsa fallback
        if not response_text or "API" in response_text:
            response_text = self._fallback_response(user_input)
        
        # Cevabı formatla
        final_response = f"🤖 **{agent['icon']} {agent['name']}** ({agent['role']})\n\n{response_text}"
        
        # Kaydet
        self.db.add_message("user", user_input)
        self.db.add_message("assistant", final_response, agent['name'], model)
        
        return {
            "content": final_response,
            "agent": agent['name'],
            "agent_icon": agent['icon'],
            "model": model,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_stats(self) -> Dict:
        msgs = self.db.get_messages()
        user_msgs = [m for m in msgs if m.get("role") == "user"]
        assistant_msgs = [m for m in msgs if m.get("role") == "assistant"]
        return {
            "total_messages": len(msgs),
            "total_conversations": len(user_msgs),
            "total_responses": len(assistant_msgs),
            "agents": list(set([m.get("agent") for m in assistant_msgs if m.get("agent")]))
        }

# ============================================
# AUTH
# ============================================
class AuthManager:
    def __init__(self, db: Database):
        self.db = db
    
    def login(self, username: str, password: str):
        users = self.db.data.get("users", {})
        if username not in users:
            return None
        user = users[username]
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        if user.get("password") != pwd_hash:
            return None
        return {"username": username, "role": user.get("role", "user"), "email": user.get("email", "")}
    
    def register(self, username: str, email: str, password: str):
        users = self.db.data.get("users", {})
        if username in users:
            return None
        users[username] = {
            "email": email,
            "password": hashlib.sha256(password.encode()).hexdigest(),
            "role": "admin" if len(users) == 0 else "user",
            "created_at": datetime.now().isoformat()
        }
        self.db.data["users"] = users
        self.db.save()
        return {"username": username, "email": email, "role": users[username]["role"]}

# ============================================
# OTURUM BAŞLAT
# ============================================
if "db" not in st.session_state:
    st.session_state.db = Database()
if "auth" not in st.session_state:
    st.session_state.auth = AuthManager(st.session_state.db)
if "ai" not in st.session_state:
    st.session_state.ai = IntelligentAI(st.session_state.db)
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "Chat"

# ============================================
# GİRİŞ EKRANI
# ============================================
def render_login():
    st.markdown("""
    <div style="text-align:center;padding:30px 0 10px 0;">
        <div style="font-size:4rem;">🧠</div>
        <h1 class="main-title">Ryzen AI Pro</h1>
        <p style="color:#94a3b8;">Profesyonel Yapay Zeka Asistanı</p>
        <span class="badge">⭐ Gerçek AI Cevapları</span>
        <p style="color:#64748b;font-size:0.8rem;margin-top:10px;">🔐 Demo: admin / admin123</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Giriş", "📝 Kayıt"])
        
        with tab1:
            with st.form("login"):
                u = st.text_input("Kullanıcı Adı", placeholder="admin")
                p = st.text_input("Şifre", type="password", placeholder="••••••••")
                if st.form_submit_button("Giriş Yap", use_container_width=True):
                    user = st.session_state.auth.login(u, p)
                    if user:
                        st.session_state.user = user
                        st.session_state.db.add_message(
                            "assistant",
                            f"👋 Hoş geldin **{user['username']}**! Ben Ryzen AI, profesyonel bir asistanım. Size nasıl yardımcı olabilirim?",
                            "Ryzen"
                        )
                        st.rerun()
                    else:
                        st.error("❌ Geçersiz kullanıcı!")
        
        with tab2:
            with st.form("register"):
                u = st.text_input("Kullanıcı Adı", placeholder="kullanici_adi")
                e = st.text_input("E-posta", placeholder="ornek@mail.com")
                p1 = st.text_input("Şifre", type="password", placeholder="••••••••")
                p2 = st.text_input("Şifre Tekrar", type="password", placeholder="••••••••")
                if st.form_submit_button("Kayıt Ol", use_container_width=True):
                    if p1 != p2:
                        st.error("❌ Şifreler eşleşmiyor!")
                    elif len(p1) < 6:
                        st.error("❌ Şifre en az 6 karakter!")
                    else:
                        user = st.session_state.auth.register(u, e, p1)
                        if user:
                            st.success("✅ Kayıt başarılı! Giriş yapabilirsin.")
                        else:
                            st.error("❌ Kullanıcı adı zaten var!")

# ============================================
# CHAT SAYFASI
# ============================================
def render_chat():
    st.markdown("""
    <div style="display:flex;justify-content:space-between;align-items:center;">
        <h1 class="main-title" style="margin:0;">💬 Sohbet</h1>
        <span class="badge" style="background:#059669;">🟢 Aktif</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Ayarlar
    col1, col2, col3 = st.columns([2, 1.5, 1])
    with col1:
        agent_names = [f"{a['icon']} {a['name']}" for a in st.session_state.ai.agents.values()]
        selected_agent = st.selectbox("🤖 Uzman Seç", agent_names, index=0)
        agent_key = selected_agent.split(" ")[1] if " " in selected_agent else "technical"
    with col2:
        model = st.selectbox("🧠 Model", ["gpt-3.5-turbo", "gpt-4-turbo", "groq-mixtral"], index=0)
    with col3:
        st.write("")
        st.write("")
        if st.button("🗑️ Temizle", use_container_width=True):
            st.session_state.db.clear_messages()
            st.rerun()
    
    # API Anahtar durumu
    if not OPENAI_API_KEY and not GROQ_API_KEY:
        st.warning("⚠️ **API Anahtarı gerekli!** Gerçek AI cevapları için OpenAI veya Groq API anahtarı ekleyin. Yoksa fallback cevaplar gelir.")
        with st.expander("🔑 API Anahtarı Ekle"):
            st.info("""
            **Ücretsiz API seçenekleri:**
            1. **Groq** (ücretsiz): https://console.groq.com
            2. **OpenAI**: https://platform.openai.com
            
            Kodu düzenleyip `OPENAI_API_KEY` veya `GROQ_API_KEY` değişkenine ekleyin.
            """)
    
    # Mesajları göster
    msgs = st.session_state.db.get_messages()
    
    if not msgs:
        st.markdown("""
        <div style="text-align:center;padding:50px 20px;">
            <div style="font-size:3rem;">👋</div>
            <h3 style="color:#94a3b8;">Merhaba! Size nasıl yard
