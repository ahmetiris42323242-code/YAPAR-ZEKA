"""
RYZEN AI ENTERPRISE - KESİN ÇÖZÜM
Tüm syntax hataları düzeltildi!
"""

import streamlit as st
import os
import json
import hashlib
import random
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objects as go

# ============================================
# SAYFA KONFIGÜRASYONU
# ============================================
st.set_page_config(
    page_title="Ryzen AI Enterprise",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS
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
    
    .enterprise-title {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        padding: 10px 0;
    }
    
    .enterprise-badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        padding: 4px 16px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .live-badge {
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .card {
        background: rgba(255,255,255,0.03);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.06);
        transition: all 0.3s ease;
        margin-bottom: 12px;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(37, 99, 235, 0.15);
    }
    
    .card-gradient {
        background: linear-gradient(135deg, rgba(37,99,235,0.08), rgba(124,58,237,0.08));
        border: 1px solid rgba(37,99,235,0.15);
    }
    
    .chat-user {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 14px 20px;
        margin: 8px 0 8px auto;
        max-width: 75%;
        animation: slideInRight 0.3s ease;
        word-wrap: break-word;
    }
    
    .chat-assistant {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px 18px 18px 4px;
        padding: 14px 20px;
        margin: 8px auto 8px 0;
        max-width: 75%;
        animation: slideInLeft 0.3s ease;
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
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    
    .sidebar-header .avatar {
        font-size: 3rem;
        margin-bottom: 4px;
    }
    
    .sidebar-header h3 {
        margin: 4px 0;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .sidebar-header p {
        opacity: 0.8;
        font-size: 0.8rem;
        margin: 0;
    }
    
    .stat-card {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .stat-number {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        color: var(--gray);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
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
        .enterprise-title {
            font-size: 1.8rem;
        }
        .chat-user, .chat-assistant {
            max-width: 90%;
            padding: 10px 14px;
            font-size: 0.9rem;
        }
        .stat-number {
            font-size: 1.5rem;
        }
    }
    
    ::-webkit-scrollbar {
        width: 4px;
        height: 4px;
    }
    ::-webkit-scrollbar-track {
        background: var(--dark);
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--primary), var(--secondary));
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

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
    
    def add_message(self, role: str, content: str, agent: str = None):
        msg = {
            "role": role,
            "content": content,
            "agent": agent,
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
class RyzenAI:
    def __init__(self, db: Database):
        self.db = db
        self.name = "Ryzen"
        self.agents = {
            "technical": {"name": "TechPro", "role": "Teknik Uzman", "icon": "💻", "temp": 0.3},
            "creative": {"name": "CreativeMind", "role": "Yaratıcı Yazar", "icon": "🎨", "temp": 0.9},
            "analyst": {"name": "DataAnalyst", "role": "Veri Analisti", "icon": "📊", "temp": 0.4},
            "business": {"name": "BizPro", "role": "İş Danışmanı", "icon": "💼", "temp": 0.6}
        }
    
    def _select_agent(self, query: str) -> str:
        q = query.lower()
        if any(w in q for w in ["kod", "python", "sistem", "hata", "çözüm", "teknoloji"]):
            return "technical"
        if any(w in q for w in ["şiir", "hikaye", "yaratıcı", "sanat", "edebiyat"]):
            return "creative"
        if any(w in q for w in ["veri", "istatistik", "grafik", "analiz", "rapor"]):
            return "analyst"
        if any(w in q for w in ["strateji", "pazarlama", "iş", "satış", "müşteri"]):
            return "business"
        return "technical"
    
    def web_search(self, query: str) -> str:
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            r = requests.get(url, timeout=5)
            data = r.json()
            if data.get('AbstractText'):
                return data['AbstractText'][:400]
            if data.get('RelatedTopics'):
                for t in data['RelatedTopics'][:2]:
                    if t.get('Text'):
                        return t['Text'][:300]
            return ""
        except:
            return ""
    
    def ask(self, user_input: str, agent_key: str = None) -> Dict:
        if not agent_key or agent_key not in self.agents:
            agent_key = self._select_agent(user_input)
        
        agent = self.agents[agent_key]
        
        web_result = ""
        if any(w in user_input for w in ["?", "nedir", "nasıl", "kimdir", "nerede"]):
            web_result = self.web_search(user_input)
        
        parts = []
        parts.append(f"🤖 **{agent['icon']} {agent['name']}** ({agent['role']})")
        parts.append("")
        
        if web_result:
            parts.append(f"🌐 **Bilgi:** {web_result}")
            parts.append("")
        
        parts.append("📝 **Cevap:**")
        parts.append(f"Merhaba! {agent['name']} olarak sana yardımcı olabilirim.")
        parts.append(f"Sorun: '{user_input}' hakkında detaylı bilgi vermek isterim.")
        parts.append("")
        parts.append("💡 **Öneri:** Daha spesifik olursan daha iyi cevap verebilirim.")
        
        response = "\n".join(parts)
        
        self.db.add_message("user", user_input)
        self.db.add_message("assistant", response, agent['name'])
        
        return {
            "content": response,
            "agent": agent['name'],
            "agent_icon": agent['icon'],
            "web_search": bool(web_result)
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
    st.session_state.ai = RyzenAI(st.session_state.db)
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "page" not in st.session_state:
    st.session_state.page = "Chat"

# ============================================
# GİRİŞ EKRANI
# ============================================
def render_login():
    st.markdown(
        """
        <div style="text-align:center;padding:30px 0 10px 0;">
            <div style="font-size:4rem;">🏢</div>
            <h1 class="enterprise-title">Ryzen AI Enterprise</h1>
            <p style="color:#94a3b8;">Kurumsal Yapay Zeka Platformu</p>
            <span class="enterprise-badge">v3.0</span>
            <p style="color:#64748b;font-size:0.8rem;margin-top:10px;">🔐 Demo: admin / admin123</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
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
                        st.session_state.messages = []
                        st.session_state.db.add_message(
                            "assistant",
                            f"👋 Hoş geldin **{user['username']}**! Sana nasıl yardımcı olabilirim?",
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
    st.markdown(
        """
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;">
            <h1 class="enterprise-title" style="margin:0;">💬 Sohbet</h1>
            <div>
                <span class="enterprise-badge live-badge">⚡ Canlı</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        agent_names = [f"{a['icon']} {a['name']}" for a in st.session_state.ai.agents.values()]
        selected_agent = st.selectbox("🤖 Agent Seç", agent_names, index=0)
        agent_key = selected_agent.split(" ")[1] if " " in selected_agent else "technical"
    with col2:
        st.write("")
        st.write("")
        clear = st.button("🗑️ Temizle", use_container_width=True)
        if clear:
            st.session_state.db.clear_messages()
            st.session_state.messages = []
            st.rerun()
    
    msgs = st.session_state.db.get_messages()
    
    if not msgs:
        st.markdown(
            """
            <div style="text-align:center;padding:40px 20px;">
                <div style="font-size:3rem;">👋</div>
                <h3 style="color:#94a3b8;">Merhaba! Sohbet etmeye başlayalım.</h3>
                <p style="color:#64748b;">Aşağıdan bir mesaj yaz veya hızlı komutları kullan.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        for msg in msgs:
            if msg["role"] == "user":
                st.markdown(
                    f"""
                    <div class="chat-user">
                        <strong>👤 Siz</strong>
                        <div>{msg["content"]}</div>
                        <div class="chat-time">{msg["timestamp"][:16]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                agent_name = msg.get("agent", "Ryzen")
                st.markdown(
                    f"""
                    <div class="chat-assistant">
                        <div class="agent-name">🤖 {agent_name}</div>
                        <div>{msg["content"]}</div>
                        <div class="chat-time">{msg["timestamp"][:16]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    st.divider()
    if prompt := st.chat_input("Mesajınızı yazın..."):
        with st.spinner("Düşünüyor..."):
            st.session_state.ai.ask(prompt, agent_key)
        st.rerun()
    
    st.caption("⚡ Hızlı Komutlar")
    cols = st.columns(4)
    quick = [
        ("🌤️ Hava", "Bugün hava nasıl?"),
        ("💡 Fikir", "Bana yaratıcı bir fikir ver"),
        ("📊 Rapor", "Bir satış raporu hazırla"),
        ("💻 Kod", "Python'da web scraper yaz")
    ]
    for col, (label, action) in zip(cols, quick):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.ai.ask(action, agent_key)
                st.rerun()

# ============================================
# AGENT SAYFASI
# ============================================
def render_agents():
    st.markdown("<h1 class='enterprise-title'>🤖 Agent'lar</h1>", unsafe_allow_html=True)
    
    cols = st.columns(2)
    idx = 0
    for key, agent in st.session_state.ai.agents.items():
        with cols[idx % 2]:
            st.markdown(
                f"""
                <div class="card card-gradient">
                    <div style="display:flex;align-items:center;gap:12px;">
                        <div style="font-size:2.5rem;">{agent['icon']}</div>
                        <div>
                            <h3 style="margin:0;">{agent['name']}</h3>
                            <p style="color:#94a3b8;font-size:0.85rem;margin:0;">{agent['role']}</p>
                        </div>
                        <div style="margin-left:auto;">
                            <span class="enterprise-badge" style="background:#059669;">Aktif</span>
                        </div>
                    </div>
                    <p style="color:#cbd5e1;margin-top:8px;font-size:0.9rem;">
                        Uzmanlık alanı: {agent['role']}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        idx += 1

# ============================================
# ANALİTİK SAYFASI
# ============================================
def render_analytics():
    st.markdown("<h1 class='enterprise-title'>📊 Analitik</h1>", unsafe_allow_html=True)
    
    stats = st.session_state.ai.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">{stats['total_messages']}</div>
                <div class="stat-label">📝 Toplam Mesaj</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f""
