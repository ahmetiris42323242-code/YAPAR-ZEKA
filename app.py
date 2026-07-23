import streamlit as st
import os
import json
import hashlib
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Ryzen AI", page_icon="🧠", layout="wide")

# ============================================
# CSS
# ============================================
st.markdown("""
<style>
    .title { text-align: center; font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #2563eb, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; padding: 10px 0; }
    .chat-user { background: linear-gradient(135deg, #2563eb, #7c3aed); color: white; border-radius: 18px 18px 4px 18px; padding: 12px 18px; margin: 8px 0 8px auto; max-width: 80%; word-wrap: break-word; }
    .chat-assistant { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08); border-radius: 18px 18px 18px 4px; padding: 12px 18px; margin: 8px auto 8px 0; max-width: 80%; word-wrap: break-word; }
    .chat-time { font-size: 0.6rem; color: #64748b; margin-top: 4px; text-align: right; }
    .sidebar-header { background: linear-gradient(135deg, #2563eb, #7c3aed); padding: 20px; border-radius: 16px; text-align: center; color: white; margin-bottom: 20px; }
    .stat-card { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 16px; text-align: center; border: 1px solid rgba(255,255,255,0.05); }
    .stat-number { font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #2563eb, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .footer { text-align: center; color: #475569; font-size: 0.75rem; padding: 20px 0; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 20px; }
    @media (max-width: 768px) { .title { font-size: 1.8rem; } .chat-user, .chat-assistant { max-width: 90%; } }
</style>
""", unsafe_allow_html=True)

# ============================================
# VERİTABANI
# ============================================
class Database:
    def __init__(self):
        self.file = "ryzen_db.json"
        self.data = {"users": {}, "messages": []}
        self.load()
    
    def load(self):
        if os.path.exists(self.file):
            try:
                with open(self.file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except:
                self.data = {"users": {}, "messages": []}
        self.save()
    
    def save(self):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_messages(self):
        return self.data.get("messages", [])
    
    def add_message(self, role, content, agent=None):
        msg = {"role": role, "content": content, "agent": agent, "timestamp": datetime.now().isoformat()}
        self.data["messages"].append(msg)
        if len(self.data["messages"]) > 200:
            self.data["messages"] = self.data["messages"][-200:]
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

# ============================================
# AI MOTORU
# ============================================
class AIEngine:
    def __init__(self, db):
        self.db = db
        self.agents = {
            "technical": {"name": "TechPro", "icon": "💻", "role": "Teknik Uzman"},
            "creative": {"name": "CreativeMind", "icon": "🎨", "role": "Yaratıcı Yazar"},
            "analyst": {"name": "DataAnalyst", "icon": "📊", "role": "Veri Analisti"},
            "business": {"name": "BizPro", "icon": "💼", "role": "İş Danışmanı"}
        }
    
    def _select_agent(self, query):
        q = query.lower()
        if any(w in q for w in ["kod", "python", "sistem", "teknoloji", "yazilim"]):
            return "technical"
        if any(w in q for w in ["siir", "hikaye", "yaratici", "sanat"]):
            return "creative"
        if any(w in q for w in ["veri", "istatistik", "analiz", "rapor"]):
            return "analyst"
        if any(w in q for w in ["strateji", "pazarlama", "is", "satis"]):
            return "business"
        return "technical"
    
    def _generate_response(self, query, agent_key):
        agent = self.agents[agent_key]
        q = query.lower()
        
        # Teknik cevaplar
        if agent_key == "technical":
            if "python" in q:
                return "Python ile web scraper yapmak icin:\n\n```python\nimport requests\nfrom bs4 import BeautifulSoup\n\nurl = 'https://example.com'\nresponse = requests.get(url)\nsoup = BeautifulSoup(response.text, 'html.parser')\ntitles = soup.find_all('h1')\nfor title in titles:\n    print(title.text)\n```\n\nDaha detayli bilgi istersen soyle!"
            elif "api" in q:
                return "REST API icin Flask ornegi:\n\n```python\nfrom flask import Flask, jsonify\napp = Flask(__name__)\n\n@app.route('/api/data')\ndef get_data():\n    return jsonify({'status': 'success'})\n```"
            else:
                return f"Teknik konuda sana yardimci olabilirim. '{query}' hakkinda daha spesifik olur musun? (Python, API, Sistem, vs.)"
        
        # Yaratıcı cevaplar
        elif agent_key == "creative":
            if "hikaye" in q:
                return "Bir zamanlar, kucuk bir kasabada yasayan bir kiz vardi. Her gun yeni seyler kesfetmek icin sabirsizlaniyordu. Bir gun, ormanda gizemli bir kitap buldu. Bu kitap, ona dunyayi degistirebilecegini ogretti. Ve o gun, hayatinin en buyuk macerasina basladi...\n\nDevami icin 'devam et' yaz!"
            else:
                return f"Yaratici fikirler uretebilirim. '{query}' konusunda bir hikaye, siir veya ilham verici bir soz ister misin?"
        
        # Analist cevaplar
        elif agent_key == "analyst":
            return f"Veri analizi konusunda yardimci olabilirim. '{query}' hakkinda:\n\n- Veri temizleme\n- Istatistiksel analiz\n- Gorsellestirme (Plotly, Matplotlib)\n- Raporlama\n\nHangi konuda detay istersin?"
        
        # İş cevapları
        elif agent_key == "business":
            if "start-up" in q or "kurulur" in q:
                return "Start-up kurmak icin adimlar:\n\n1. Fikir gelistirme ve pazar arastirmasi\n2. Is plani hazirlama\n3. Sirket turu secimi (A.S., Ltd.)\n4. Finansman kaynaklari (melek yatirimci, VC)\n5. Pazarlama ve musteri edinme\n\nHangi adimda yardim istersin?"
            else:
                return f"Is danismani olarak '{query}' konusunda stratejik tavsiyeler verebilirim. Daha spesifik olur musun?"
        
        # Genel cevap
        return f"Merhaba! Ben Ryzen AI. '{query}' hakkinda sana yardimci olabilirim.\n\nUzmanlik alanlarim:\n💻 Teknoloji (Python, API, Sistem)\n🎨 Yaratıcı İçerik (Hikaye, Şiir)\n📊 Veri Analizi (Istatistik, Rapor)\n💼 İş Danışmanlığı (Strateji, Pazarlama)"
    
    def ask(self, user_input, agent_key=None):
        if not agent_key or agent_key not in self.agents:
            agent_key = self._select_agent(user_input)
        agent = self.agents[agent_key]
        
        response = self._generate_response(user_input, agent_key)
        final = f"**{agent['icon']} {agent['name']}** ({agent['role']})\n\n{response}"
        
        self.db.add_message("user", user_input)
        self.db.add_message("assistant", final, agent["name"])
        
        return {"content": final, "agent": agent["name"]}
    
    def get_stats(self):
        msgs = self.db.get_messages()
        user_msgs = [m for m in msgs if m.get("role") == "user"]
        return {
            "total_messages": len(msgs),
            "total_conversations": len(user_msgs),
            "agents": list(set([m.get("agent") for m in msgs if m.get("agent")]))
        }

# ============================================
# AUTH
# ============================================
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

# ============================================
# OTURUM
# ============================================
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

# ============================================
# GİRİŞ
# ============================================
def render_login():
    st.markdown('<div style="text-align:center;padding:30px 0;"><div style="font-size:4rem;">🧠</div><h1 class="title">Ryzen AI Pro</h1><p style="color:#94a3b8;">Profesyonel Yapay Zeka Asistanı</p><p style="color:#64748b;font-size:0.8rem;">🔐 Demo: admin / admin123</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Giriş", "📝 Kayıt"])
        
        with tab1:
            with st.form("login"):
                u = st.text_input("Kullanıcı Adı")
                p = st.text_input("Şifre", type="password")
                if st.form_submit_button("Giriş Yap", use_container_width=True):
                    user = st.session_state.auth.login(u, p)
                    if user:
                        st.session_state.user = user
                        st.session_state.db.add_message("assistant", f"👋 Hoş geldin {user['username']}! Sana nasıl yardımcı olabilirim?", "Ryzen")
                        st.rerun()
                    else:
                        st.error("❌ Geçersiz kullanıcı!")
        
        with tab2:
            with st.form("register"):
                u = st.text_input("Kullanıcı Adı")
                e = st.text_input("E-posta")
                p1 = st.text_input("Şifre", type="password")
                p2 = st.text_input("Şifre Tekrar", type="password")
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
# SOHBET
# ============================================
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
        st.info("👋 Merhaba! Sohbete başlayalım. Aşağıdan sorunu yaz.")
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
    quick = [
        ("💻 Python", "Python'da web scraper nasıl yazılır?"),
        ("📊 Analiz", "Veri analizi için en iyi yöntemler nelerdir?"),
        ("🎨 Hikaye", "Bana ilham verici bir hikaye anlat"),
        ("💼 Start-up", "Bir start-up nasıl kurulur?")
    ]
    for col, (label, action) in zip(cols, quick):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.ai.ask(action, agent_key)
                st.rerun()

# ============================================
# ANALİTİK
# ============================================
def render_analytics():
    st.markdown('<h1 class="title" style="font-size:2rem;">📊 Analitik</h1>', unsafe_allow_html=True)
    
    stats = st.session_state.ai.get_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["total_messages"]}</div><div style="color:#94a3b8;">📝 Toplam Mesaj</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{stats["total_conversations"]}</div><div style="color:#94a3b8;">💬 Konuşma</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(stats.get("agents", []))}</div><div style="color:#94a3b8;">🤖 Uzman</div></div>', unsafe_allow_html=True)

# ============================================
# AYARLAR
# ============================================
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
        st.success("✅ Ayarlar kaydedildi!")

# ============================================
# ADMIN
# ============================================
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

# ============================================
# ANA
# ============================================
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
