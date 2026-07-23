"""
RYZEN AI PRO - GERCEK YAPAY ZEKA ASISTANI
"""

import streamlit as st
import os
import json
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional
import requests
import pandas as pd

# ============================================
# SAYFA KONFIGURASYONU
# ============================================
st.set_page_config(
    page_title="Ryzen AI Pro",
    page_icon="🧠",
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
    @media (max-width: 768px) {
        .main-title { font-size: 1.8rem; }
        .chat-user, .chat-assistant { max-width: 90%; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# API AYARLARI
# ============================================
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# ============================================
# VERITABANI
# ============================================
class Database:
    def __init__(self, db_file="ryzen_db.json"):
        self.db_file = db_file
        self.data = {"users": {}, "messages": [], "settings": {}}
        self.load()
    
    def load(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except:
                self.data = {"users": {}, "messages": [], "settings": {}}
        self.save()
    
    def save(self):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_messages(self):
        return self.data.get("messages", [])
    
    def add_message(self, role, content, agent=None, model=None):
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
# AI MOTORU
# ============================================
class IntelligentAI:
    def __init__(self, db):
        self.db = db
        self.agents = {
            "technical": {
                "name": "TechPro",
                "role": "Teknik Uzman",
                "icon": "💻",
                "system": "Sen bir teknoloji uzmanisin. Kod, sistem, veri yapilari konularinda derin bilgin var."
            },
            "creative": {
                "name": "CreativeMind",
                "role": "Yaratici Yazar",
                "icon": "🎨",
                "system": "Sen yaratici bir yazarsin. Ilham verici, ozgun ve etkileyici icerikler uret."
            },
            "analyst": {
                "name": "DataAnalyst",
                "role": "Veri Analisti",
                "icon": "📊",
                "system": "Sen bir veri analisti uzmanisin. Verileri yorumla ve icgoruler sun."
            },
            "business": {
                "name": "BizPro",
                "role": "Is Danismani",
                "icon": "💼",
                "system": "Sen bir is danismanisin. Strateji ve yonetim konularinda profesyonel tavsiyeler ver."
            }
        }
    
    def _select_agent(self, query):
        q = query.lower()
        if any(w in q for w in ["kod", "python", "sistem", "hata", "teknoloji", "yazilim"]):
            return "technical"
        if any(w in q for w in ["siir", "hikaye", "yaratici", "sanat", "edebiyat"]):
            return "creative"
        if any(w in q for w in ["veri", "istatistik", "grafik", "analiz", "rapor"]):
            return "analyst"
        if any(w in q for w in ["strateji", "pazarlama", "yonetim", "is", "satis"]):
            return "business"
        return "technical"
    
    def _call_api(self, messages, model="gpt-3.5-turbo"):
        if OPENAI_API_KEY:
            try:
                headers = {
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": model if model != "groq-mixtral" else "gpt-3.5-turbo",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1500
                }
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
            except:
                pass
        
        if GROQ_API_KEY:
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
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
            except:
                pass
        
        return None
    
    def _fallback_response(self, query):
        q = query.lower()
        if "nasilsin" in q or "nasılsın" in q:
            return "Merhaba! Ben Ryzen AI, profesyonel bir asistanim. Size nasil yardimci olabilirim?"
        if "adin" in q or "ismin" in q or "adın" in q:
            return "Benim adim Ryzen. Yapay zeka tabanli profesyonel bir asistanim."
        if "python" in q:
            return "Python, yuksek seviyeli, genel amacli bir programlama dilidir. Web gelistirme, veri analizi, yapay zeka ve otomasyon icin yaygin kullanilir."
        if "hava" in q:
            return "Bugun hava durumu: Gunesli, sicaklik 24°C. Yagis beklenmiyor."
        if "yardim" in q or "help" in q:
            return "Size su konularda yardimci olabilirim:\n- Teknik sorular\n- Kod yazma\n- Veri analizi\n- Is stratejileri\n- Yaratici icerik"
        return f"Merhaba! Sorunuz: '{query}'. Bu konuda size detayli bilgi verebilirim. Daha spesifik olursaniz daha iyi yardimci olabilirim."
    
    def ask(self, user_input, agent_key=None, model="gpt-3.5-turbo"):
        if not agent_key or agent_key not in self.agents:
            agent_key = self._select_agent(user_input)
        agent = self.agents[agent_key]
        
        messages = [
            {"role": "system", "content": agent["system"]},
            {"role": "system", "content": "Turkce cevap ver. Detayli, profesyonel ve aciklayici ol."}
        ]
        
        recent = self.db.get_messages()[-6:]
        for msg in recent:
            if msg["role"] == "user":
                messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                messages.append({"role": "assistant", "content": msg["content"][:300]})
        
        messages.append({"role": "user", "content": user_input})
        
        response = self._call_api(messages, model)
        if not response:
            response = self._fallback_response(user_input)
        
        final = f"🤖 **{agent['icon']} {agent['name']}** ({agent['role']})\n\n{response}"
        
        self.db.add_message("user", user_input)
        self.db.add_message("assistant", final, agent["name"], model)
        
        return {
            "content": final,
            "agent": agent["name"],
            "agent_icon": agent["icon"],
            "model": model
        }
    
    def get_stats(self):
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
    def __init__(self, db):
        self.db = db
    
    def login(self, username, password):
        users = self.db.data.get("users", {})
        if username not in users:
            return None
        user = users[username]
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        if user.get("password") != pwd_hash:
            return None
        return {"username": username, "role": user.get("role", "user"), "email": user.get("email", "")}
    
    def register(self, username, email, password):
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
# OTURUM
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
# GIRIS EKRANI
# ============================================
def render_login():
    st.markdown(
        '<div style="text-align:center;padding:30px 0 10px 0;">'
        '<div style="font-size:4rem;">🧠</div>'
        '<h1 class="main-title">Ryzen AI Pro</h1>'
        '<p style="color:#94a3b8;">Profesyonel Yapay Zeka Asistani</p>'
        '<span class="badge">⭐ Gercek AI Cevaplari</span>'
        '<p style="color:#64748b;font-size:0.8rem;margin-top:10px;">🔐 Demo: admin / admin123</p>'
        '</div>',
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Giris", "📝 Kayit"])
        
        with tab1:
            with st.form("login"):
                u = st.text_input("Kullanici Adi", placeholder="admin")
                p = st.text_input("Sifre", type="password", placeholder="••••••••")
                if st.form_submit_button("Giris Yap", use_container_width=True):
                    user = st.session_state.auth.login(u, p)
                    if user:
                        st.session_state.user = user
                        st.session_state.db.add_message(
                            "assistant",
                            "👋 Hos geldin! Ben Ryzen AI, profesyonel bir asistanim. Size nasil yardimci olabilirim?",
                            "Ryzen"
                        )
                        st.rerun()
                    else:
                        st.error("❌ Gecersiz kullanici!")
        
        with tab2:
            with st.form("register"):
                u = st.text_input("Kullanici Adi", placeholder="kullanici_adi")
                e = st.text_input("E-posta", placeholder="ornek@mail.com")
                p1 = st.text_input("Sifre", type="password", placeholder="••••••••")
                p2 = st.text_input("Sifre Tekrar", type="password", placeholder="••••••••")
                if st.form_submit_button("Kayit Ol", use_container_width=True):
                    if p1 != p2:
                        st.error("❌ Sifreler eslesmiyor!")
                    elif len(p1) < 6:
                        st.error("❌ Sifre en az 6 karakter!")
                    else:
                        user = st.session_state.auth.register(u, e, p1)
                        if user:
                            st.success("✅ Kayit basarili! Giris yapabilirsin.")
                        else:
                            st.error("❌ Kullanici adi zaten var!")

# ============================================
# CHAT SAYFASI
# ============================================
def render_chat():
    st.markdown(
        '<div style="display:flex;justify-content:space-between;align-items:center;">'
        '<h1 class="main-title" style="margin:0;">💬 Sohbet</h1>'
        '<span class="badge" style="background:#059669;">🟢 Aktif</span>'
        '</div>',
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([2, 1.5, 1])
    with col1:
        agent_names = [a["icon"] + " " + a["name"] for a in st.session_state.ai.agents.values()]
        selected = st.selectbox("🤖 Uzman Sec", agent_names, index=0)
        agent_key = selected.split(" ")[1] if " " in selected else "technical"
    with col2:
        model = st.selectbox("🧠 Model", ["gpt-3.5-turbo", "gpt-4-turbo", "groq-mixtral"], index=0)
    with col3:
        st.write("")
        st.write("")
        if st.button("🗑️ Temizle", use_container_width=True):
            st.session_state.db.clear_messages()
            st.rerun()
    
    if not OPENAI_API_KEY and not GROQ_API_KEY:
        st.info("💡 API anahtari ekleyerek gercek AI cevaplari alabilirsiniz. Su anda demo cevaplar geliyor.")
    
    msgs = st.session_state.db.get_messages()
    
    if not msgs:
        st.markdown(
            '<div style="text-align:center;padding:50px 20px;">'
            '<div style="font-size:3rem;">👋</div>'
            '<h3 style="color:#94a3b8;">Merhaba! Size nasil yardimci olabilirim?</h3>'
            '<p style="color:#64748b;">Uzman bir AI asistan olarak sorularinizi cevapliyorum.</p>'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        for msg in msgs:
            if msg["role"] == "user":
                st.markdown(
                    '<div class="chat-user">'
                    '<strong>👤 Siz</strong>'
                    '<div>' + msg["content"] + '</div>'
                    '<div class="chat-time">' + msg["timestamp"][:16] + '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )
            else:
                agent_name = msg.get("agent", "Ryzen")
                st.markdown(
                    '<div class="chat-assistant">'
                    '<div class="agent-name">🧠 ' + agent_name + '</div>'
                    '<div>' + msg["content"] + '</div>'
                    '<div class="chat-time">' + msg["timestamp"][:16] + '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )
    
    st.divider()
    if prompt := st.chat_input("Sorunuzu yazin..."):
        with st.spinner("🧠 Dusunuyor..."):
            st.session_state.ai.ask(prompt, agent_key, model)
        st.rerun()
    
    st.caption("⚡ Ornek Sorular")
    cols = st.columns(4)
    quick = [
        ("💻 Python", "Python'da web scraper nasil yazilir?"),
        ("📊 Analiz", "Veri analizi icin en iyi yontemler nelerdir?"),
        ("🎨 Yaratıcı", "Bana ilham verici bir hikaye anlat"),
        ("💼 Is", "Bir start-up nasil kurulur?")
    ]
    for col, (label, action) in zip(cols, quick):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.ai.ask(action, agent_key, model)
                st.rerun()

# ============================================
# ANALITIK SAYFASI
# ============================================
def render_analytics():
    st.markdown('<h1 class="main-title">📊 Analitik</h1>', unsafe_allow_html=True)
    
    stats = st.session_state.ai.get_stats()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            '<div class="stat-card">'
            '<div class="stat-number">' + str(stats["total_messages"]) + '</div>'
            '<div style="color:#94a3b8;">📝 Toplam Mesaj</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            '<div class="stat-card">'
            '<div class="stat-number">' + str(stats["total_conversations"]) + '</div>'
            '<div style="color:#94a3b8;">💬 Konusma</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            '<div class="stat-card">'
            '<div class="stat-number">' + str(len(stats.get("agents", []))) + '</div>'
            '<div style="color:#94a3b8;">🤖 Uzman</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with c4:
        st.markdown(
            '<div class="stat-card">'
            '<div class="stat-number">' + str(len(st.session_state.db.data.get("users", {}))) + '</div>'
            '<div style="color:#94a3b8;">👥 Kullanici</div>'
            '</div>',
            unsafe_allow_html=True
        )

# ============================================
# AYARLAR SAYFASI
# ====================================
