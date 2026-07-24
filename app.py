import streamlit as st
import os
import json
import hashlib
from datetime import datetime
import pandas as pd
import random

st.set_page_config(page_title="Ryzen AI", page_icon="🧠", layout="wide")

st.markdown("""
<style>
.title { text-align:center; font-size:2.5rem; font-weight:800; background:linear-gradient(135deg,#2563eb,#7c3aed); -webkit-background-clip:text; -webkit-text-fill-color:transparent; padding:10px 0; }
.chat-user { background:linear-gradient(135deg,#2563eb,#7c3aed); color:white; border-radius:18px 18px 4px 18px; padding:12px 18px; margin:8px 0 8px auto; max-width:80%; }
.chat-assistant { background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.08); border-radius:18px 18px 18px 4px; padding:12px 18px; margin:8px auto 8px 0; max-width:80%; }
.chat-time { font-size:0.6rem; color:#64748b; margin-top:4px; text-align:right; }
.sidebar-header { background:linear-gradient(135deg,#2563eb,#7c3aed); padding:20px; border-radius:16px; text-align:center; color:white; margin-bottom:20px; }
.stat-card { background:rgba(255,255,255,0.03); border-radius:12px; padding:16px; text-align:center; border:1px solid rgba(255,255,255,0.05); }
.stat-number { font-size:2rem; font-weight:700; background:linear-gradient(135deg,#2563eb,#7c3aed); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.footer { text-align:center; color:#475569; font-size:0.75rem; padding:20px 0; border-top:1px solid rgba(255,255,255,0.05); margin-top:20px; }
@media (max-width:768px) { .title { font-size:1.8rem; } .chat-user, .chat-assistant { max-width:90%; } }
</style>
""", unsafe_allow_html=True)

class Database:
    def __init__(self, file="db.json"):
        self.file = file
        self.data = {"users": {}, "messages": [], "stats": {}}
        self.load()
    def load(self):
        if os.path.exists(self.file):
            try:
                with open(self.file, "r") as f:
                    self.data = json.load(f)
            except:
                self.data = {"users": {}, "messages": [], "stats": {}}
        self.save()
    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    def get_messages(self):
        return self.data.get("messages", [])
    def add_message(self, role, content, agent=None):
        msg = {"role": role, "content": content, "agent": agent, "timestamp": datetime.now().isoformat()}
        self.data["messages"].append(msg)
        if len(self.data["messages"]) > 500:
            self.data["messages"] = self.data["messages"][-500:]
        self.save()
        return msg
    def clear_messages(self):
        self.data["messages"] = []
        self.save()
    def get_users(self):
        return self.data.get("users", {})
    def add_user(self, username, data):
        self.data["users"][username] = data
        self.save()
    def update_stats(self, key, value):
        self.data["stats"][key] = value
        self.save()
    def get_stats(self):
        return self.data.get("stats", {})

class AIEngine:
    def __init__(self, db):
        self.db = db
        self.agents = {
            "technical": {"name": "TechPro", "icon": "💻", "role": "Teknik Uzman"},
            "creative": {"name": "CreativeMind", "icon": "🎨", "role": "Yaratıcı Yazar"},
            "analyst": {"name": "DataAnalyst", "icon": "📊", "role": "Veri Analisti"},
            "business": {"name": "BizPro", "icon": "💼", "role": "İş Danışmanı"}
        }
        self.how_are_you = [
            "Harikayım! 😊 Siz nasılsınız?",
            "Mükemmel! 🚀 Sizi görmek ne güzel!",
            "Çok iyiyim! Size yardım etmek için hazırım. 💪"
        ]
        self.greetings = [
            "Merhaba! 😊 Size nasıl yardımcı olabilirim?",
            "Hoş geldiniz! 🚀 Ne sormak istersiniz?",
            "Selam! 💪 Hemen yardımcı olmaya hazırım."
        ]
    def _select_agent(self, q):
        q = q.lower()
        if any(w in q for w in ["python", "kod", "sistem", "api", "teknoloji"]):
            return "technical"
        if any(w in q for w in ["hikaye", "siir", "yaratici", "sanat"]):
            return "creative"
        if any(w in q for w in ["veri", "analiz", "istatistik", "rapor"]):
            return "analyst"
        if any(w in q for w in ["strateji", "pazarlama", "is", "startup"]):
            return "business"
        return "technical"
    def _get_response(self, q, agent_key):
        q = q.lower()
        if "nasilsin" in q or "nasılsın" in q:
            return random.choice(self.how_are_you)
        if "merhaba" in q or "selam" in q:
            return random.choice(self.greetings)
        if "tesekkur" in q or "teşekkür" in q:
            return "Rica ederim! 😊 Başka bir şey sormak ister misiniz?"
        if "adın" in q or "ismin" in q:
            return "Benim adım Ryzen! 🤖 Profesyonel bir AI asistanıyım."
        if agent_key == "technical":
            if "python" in q:
                return "```python\nimport requests\nfrom bs4 import BeautifulSoup\nurl='https://example.com'\nr=requests.get(url)\nsoup=BeautifulSoup(r.text,'html.parser')\nfor h in soup.find_all('h1'):\n    print(h.text)\n```\nDetaylı anlatım ister misin?"
            return f"Teknik konuda yardımcı olabilirim. '{q}' hakkında daha spesifik olur musun?"
        if agent_key == "creative":
            return f"Yaratıcı bir hikaye mi yoksa şiir mi istersin? '{q}' konusunda ilham verebilirim."
        if agent_key == "analyst":
            return f"Veri analizi konusunda yardımcı olabilirim. '{q}' hakkında hangi adımda yardım istersin?"
        if agent_key == "business":
            if "startup" in q:
                return "🚀 Start-up kurulum rehberi:\n1. Fikir\n2. Plan\n3. Yasal\n4. Finansman\n5. Pazarlama\nDetay istersen söyle!"
            return f"İş danışmanı olarak '{q}' konusunda stratejik tavsiyeler verebilirim."
        return f"Merhaba! Ben Ryzen AI. '{q}' hakkında yardımcı olabilirim. Daha spesifik olur musun?"
    def ask(self, user_input, agent_key=None):
        if not agent_key or agent_key not in self.agents:
            agent_key = self._select_agent(user_input)
        agent = self.agents[agent_key]
        response = self._get_response(user_input, agent_key)
        final = f"**{agent['icon']} {agent['name']}** ({agent['role']})\n\n{response}"
        self.db.add_message("user", user_input)
        self.db.add_message("assistant", final, agent["name"])
        stats = self.db.get_stats()
        stats["total_questions"] = stats.get("total_questions", 0) + 1
        self.db.update_stats("total_questions", stats["total_questions"])
        return {"content": final, "agent": agent["name"]}
    def get_stats(self):
        msgs = self.db.get_messages()
        user_msgs = [m for m in msgs if m.get("role") == "user"]
        return {
            "total_messages": len(msgs),
            "total_conversations": len(user_msgs),
            "agents_used": list(set([m.get("agent") for m in msgs if m.get("agent")])),
            "total_questions": self.db.get_stats().get("total_questions", 0)
        }

class Auth:
    def __init__(self, db):
        self.db = db
    def login(self, username, password):
        users = self.db.get_users()
        if username not in users:
            return None
        user = users[username]
        if user.get("password") != hashlib.sha256(password.encode()).hexdigest():
            return None
        return {"username": username, "role": user.get("role", "user"), "email": user.get("email", "")}
    def register(self, username, email, password):
        users = self.db.get_users()
        if username in users:
            return None
        self.db.add_user(username, {
            "email": email,
            "password": hashlib.sha256(password.encode()).hexdigest(),
            "role": "admin" if len(users) == 0 else "user",
            "created_at": datetime.now().isoformat()
        })
        return {"username": username, "email": email, "role": "user"}

if "db" not in st.session_state:
    st.session_state.db = Database()
if "auth" not in st.session_state:
    st.session_state.auth = Auth(st.session_state.db)
if "ai" not in st.session_state:
    st.session_state.ai = AIEngine(st.session_state.db)
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "Sohbet"

def render_login():
    st.markdown('<div style="text-align:center;padding:40px 0;"><div style="font-size:4rem;">🧠</div><h1 class="title">Ryzen AI Pro</h1><p style="color:#94a3b8;">Profesyonel Yapay Zeka Asistanı</p><p style="color:#64748b;font-size:0.8rem;">🔐 Demo: admin / admin123</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Giriş", "📝 Kayıt"])
        with tab1:
            with st.form("login"):
                u = st.text_input("Kullanıcı Adı")
                p = st.text_input("Şifre", type="password")
                if st.form_submit_button("Giriş", use_container_width=True):
                    user = st.session_state.auth.login(u, p)
                    if user:
                        st.session_state.user = user
                        st.session_state.db.add_message("assistant", "👋 Hoş geldin! Ben Ryzen AI.", "Ryzen")
                        st.rerun()
                    else:
                        st.error("❌ Geçersiz kullanıcı!")
        with tab2:
            with st.form("register"):
                u = st.text_input("Kullanıcı Adı")
                e = st.text_input("E-posta")
                p1 = st.text_input("Şifre", type="password")
                p2 = st.text_input("Şifre Tekrar", type="password")
                if st.form_submit_button("Kayıt", use_container_width=True):
                    if p1 != p2:
                        st.error("❌ Şifreler eşleşmiyor!")
                    elif len(p1) < 6:
                        st.error("❌ Şifre en az 6 karakter!")
                    else:
                        user = st.session_state.auth.register(u, e, p1)
                        if user:
                            st.success("✅ Kayıt başarılı!")
                        else:
                            st.error("❌ Kullanıcı adı zaten var!")

def render_chat():
    st.markdown('<h1 class="title" style="font-size:2rem;">💬 Sohbet</h1>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        agent_names = [f"{a['icon']} {a['name']}" for a in st.session_state.ai.agents.values()]
        selected = st.selectbox("🤖 Uzman Seç", agent_names, index=0)
        agent_key = selected.split(" ")[1] if " " in selected else "technical"
    with col2:
        if st.button("🗑️ Temizle", use_container_width=True):
            st.session_state.db.clear_messages()
            st.rerun()
    msgs = st.session_state.db.get_messages()
    if not msgs:
        st.info("👋 Merhaba! Sohbete başlayalım.")
    else:
        for msg in msgs:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user"><strong>👤 Siz</strong><div>{msg["content"]}</div><div class="chat-time">{msg["timestamp"][:16]}</div></div>', unsafe_allow_html=True)
            else:
                agent = msg.get("agent", "Ryzen")
                st.markdown(f'<div class="chat-assistant"><strong>🧠 {agent}</strong><div>{msg["content"]}</div><div class="chat-time">{msg["timestamp"][:16]}</div></div>', unsafe_allow_html=True)
    st.divider()
    if prompt := st.chat_input("Mesajınızı yazın..."):
        with st.spinner("Düşünüyor..."):
            st.session_state.ai.ask(prompt, agent_key)
        st.rerun()
    st.caption("⚡ Hızlı Komutlar")
    cols = st.columns(4)
    quick = [("💻 Python", "Python'da web scraper nasıl yazılır?"), ("📊 Analiz", "Veri analizi için en iyi yöntemler nelerdir?"), ("🎨 Hikaye", "Bana ilham verici bir hikaye anlat"), ("🚀 Start-up", "Bir start-up nasıl kurulur?")]
    for col, (label, action) in zip(cols, quick):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.ai.ask(action, agent_key)
                st.rerun()

def render_analytics():
    st.markdown('<h1 class="title" style="font-size:2rem;">📊 Analitik</h1>', unsafe_allow_html=True)
    stats = st.session_state.ai.get_stats()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["total_messages"]}</div><div style="color:#94a3b8;">📝 Mesaj</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["total_conversations"]}</div><div style="color:#94a3b8;">💬 Konuşma</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["total_questions"]}</div><div style="color:#94a3b8;">❓ Soru</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(stats.get("agents_used", []))}</div><div style="color:#94a3b8;">🤖 Uzman</div></div>', unsafe_allow_html=True)

def render_settings():
    st.markdown('<h1 class="title" style="font-size:2rem;">⚙️ Ayarlar</h1>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sistem")
        st.selectbox("Model", ["GPT-4", "GPT-3.5", "Claude-3"], index=0)
        st.slider("Yaratıcılık", 0.0, 1.0, 0.7)
    with col2:
        st.subheader("Görünüm")
        st.selectbox("Tema", ["Koyu", "Açık"], index=0)
        st.color_picker("Ana Renk", "#2563eb")
    if st.button("💾 Kaydet", use_container_width=True):
        st.success("✅ Kaydedildi!")

def render_admin():
    st.markdown('<h1 class="title" style="font-size:2rem;">🔧 Admin</h1>', unsafe_allow_html=True)
    users = st.session_state.db.get_users()
    if users:
        data = []
        for u, info in users.items():
            data.append({"Kullanıcı": u, "E-posta": info.get("email", ""), "Rol": info.get("role", "user")})
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else:
        st.info("Henüz kullanıcı yok.")

def main():
    if not st.session_state.user:
        render_login()
        return
    with st.sidebar:
        user = st.session_state.user
        st.markdown(f'<div class="sidebar-header"><div style="font-size:3rem;">👤</div><h3>{user.get("username", "Kullanıcı")}</h3><p>{user.get("email", "")}</p><span style="display:inline-block;background:rgba(255,255,255,0.2);padding:2px 12px;border-radius:12px;font-size:0.7rem;">{user.get("role", "user").upper()}</span></div>', unsafe_allow_html=True)
        menu = ["💬 Sohbet", "📊 Analitik", "⚙️ Ayarlar"]
        if user.get("role") == "admin":
            menu.append("🔧 Admin")
        selected = st.radio("📌 MENÜ", menu, index=0)
        st.session_state.page = selected
        st.divider()
        stats = st.session_state.ai.get_stats()
        st.caption(f"💬 {stats['total_conversations']} konuşma")
        st.caption(f"📝 {stats['total_messages']} mesaj")
        st.divider()
        if st.button("🚪 Çıkış", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    page = st.session_state.page
    if page == "💬 Sohbet":
        render_chat()
    elif page == "📊 Analitik":
        render_analytics()
    elif page == "⚙️ Ayarlar":
        render_settings()
    elif page == "🔧 Admin":
        render_admin()
    else:
        render_chat()
    st.markdown('<div class="footer">🧠 Ryzen AI Pro | © 2026</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
