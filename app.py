import streamlit as st
import streamlit_extras as ste
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json

from core.assistant import ProfessionalAI
from utils.auth import AuthManager
from utils.logger import Logger
from utils.metrics import MetricsCollector
from ui.components import UIComponents
from ui.styles import load_css

# ============================================
# SAYFA YAPILANDIRMASI
# ============================================
st.set_page_config(
    page_title="Ryzen AI Assistant Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS yükle
st.markdown(load_css(), unsafe_allow_html=True)

# ============================================
# OTURUM BAŞLATMA
# ============================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'ai' not in st.session_state:
    st.session_state.ai = ProfessionalAI()
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = None

auth = AuthManager()
logger = Logger()
metrics = MetricsCollector()

# ============================================
# GİRİŞ EKRANI
# ============================================
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://via.placeholder.com/150x150.png?text=🧠", width=150)
        st.title("🧠 Ryzen AI Pro")
        st.caption("Kurumsal Seviye Yapay Zeka Asistanı")
        
        login_tab, register_tab = st.tabs(["🔑 Giriş", "📝 Kayıt"])
        
        with login_tab:
            with st.form("login_form"):
                username = st.text_input("Kullanıcı Adı")
                password = st.text_input("Şifre", type="password")
                col1, col2 = st.columns([2, 1])
                with col2:
                    submit = st.form_submit_button("Giriş", use_container_width=True)
                
                if submit:
                    user = auth.login(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("❌ Geçersiz kullanıcı adı veya şifre!")
        
        with register_tab:
            with st.form("register_form"):
                new_username = st.text_input("Kullanıcı Adı")
                new_email = st.text_input("E-posta")
                new_password = st.text_input("Şifre", type="password")
                confirm_password = st.text_input("Şifre Tekrar", type="password")
                col1, col2 = st.columns([2, 1])
                with col2:
                    submit = st.form_submit_button("Kayıt", use_container_width=True)
                
                if submit:
                    if new_password != confirm_password:
                        st.error("❌ Şifreler eşleşmiyor!")
                    elif auth.register(new_username, new_email, new_password):
                        st.success("✅ Kayıt başarılı! Şimdi giriş yapabilirsin.")
                    else:
                        st.error("❌ Bu kullanıcı adı zaten var!")

# ============================================
# ANA UYGULAMA
# ============================================
else:
    # ==========================================
    # SİDEBAR
    # ==========================================
    with st.sidebar:
        # Kullanıcı bilgisi
        st.image("https://via.placeholder.com/100x100.png?text=👤", width=80)
        st.markdown(f"### {st.session_state.user['username']}")
        st.caption(f"📧 {st.session_state.user['email']}")
        
        st.divider()
        
        # Ana Menü
        selected = option_menu(
            menu_title=None,
            options=[
                "💬 Sohbet",
                "📁 Belgeler",
                "📊 Analitik",
                "⚙️ Ayarlar",
                "📤 Dışa Aktar",
                "🔌 API",
                "❓ Yardım"
            ],
            icons=[
                "chat-dots",
                "folder",
                "bar-chart",
                "gear",
                "download",
                "plug",
                "question-circle"
            ],
            default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "icon": {"font-size": "1.2rem"},
                "nav-link": {
                    "font-size": "0.9rem",
                    "text-align": "left",
                    "margin": "2px 0px",
                },
                "nav-link-selected": {
                    "background-color": "#ff6b6b",
                },
            }
        )
        
        st.divider()
        
        # Konuşmalar
        st.subheader("📝 Son Konuşmalar")
        conversations = st.session_state.ai.memory.get_all_conversations()
        for conv in conversations[-5:]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"📌 {conv['title'][:20]}")
            with col2:
                if st.button("📂", key=f"load_{conv['id']}"):
                    st.session_state.messages = conv['messages']
                    st.rerun()
        
        st.divider()
        
        # Çıkış
        if st.button("🚪 Çıkış", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    # ==========================================
    # ANA İÇERİK
    # ==========================================
    
    if selected == "💬 Sohbet":
        # Sohbet Arayüzü
        st.markdown("<h1 class='gradient-text'>💬 AI Asistan</h1>", unsafe_allow_html=True)
        
        # Model seçimi
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            model = st.selectbox(
                "🤖 Model",
                ["gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o"],
                index=0
            )
        with col2:
            temperature = st.slider("🎨 Yaratıcılık", 0.0, 1.0, 0.7, 0.1)
        with col3:
            max_tokens = st.number_input("📝 Max Tokens", 100, 4000, 2000, 100)
        
        # Sohbet geçmişi
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("metadata"):
                    with st.expander("📊 Metadeta"):
                        st.json(msg["metadata"])
        
        # Kullanıcı girişi
        if prompt := st.chat_input("Mesajınızı yazın..."):
            # Kullanıcı mesajı
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Asistan cevabı
            with st.chat_message("assistant"):
                with st.spinner("🧠 Düşünüyorum..."):
                    response = st.session_state.ai.ask(prompt)
                    
                    if response.get('error'):
                        st.error(f"❌ Hata: {response['error']}")
                    else:
                        st.markdown(response['content'])
                        
                        # Metadata
                        with st.expander("📊 Detaylar"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Model", response['metadata']['model'])
                            with col2:
                                st.metric("Token", response['metadata']['tokens'])
                            if response['metadata'].get('thoughts'):
                                st.write("**Düşünce Zinciri:**")
                                for thought in response['metadata']['thoughts']:
                                    st.caption(f"• {thought}")
                
                # Kaydet
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response['content'],
                    "metadata": response['metadata']
                })
                
                # Metrikleri güncelle
                metrics.log_interaction(
                    user=st.session_state.user['username'],
                    model=response['metadata']['model'],
                    tokens=response['metadata']['tokens']
                )
        
        # Hızlı eylemler
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("💡 Bugün hava nasıl?", use_container_width=True):
                prompt = "Bugün hava durumu nasıl?"
                # Burada yukarıdaki mantığı çalıştır
        with col2:
            if st.button("📝 Özet çıkar", use_container_width=True):
                prompt = "Son konuşmamızı özetler misin?"
        with col3:
            if st.button("🔍 Ara", use_container_width=True):
                prompt = "ara: en son teknolojiler"
        with col4:
            if st.button("💻 Kod yaz", use_container_width=True):
                prompt = "Python'da bir web scraper yaz"
    
    elif selected == "📁 Belgeler":
        st.markdown("<h1 class='gradient-text'>📁 Belge Yönetimi</h1>", unsafe_allow_html=True)
        
        # Belge yükleme
        uploaded_file = st.file_uploader(
            "📤 Belge Yükle",
            type=['pdf', 'txt', 'docx', 'md'],
            accept_multiple_files=False
        )
        
        if uploaded_file:
            if st.button("📥 Belgeyi İşle"):
                with st.spinner("📄 Belge işleniyor..."):
                    content = uploaded_file.read().decode('utf-8')
                    st.session_state.ai.rag.add_document(
                        name=uploaded_file.name,
                        content=content
                    )
                    st.success(f"✅ {uploaded_file.name} başarıyla işlendi!")
        
        # Yüklenen belgeler
        st.subheader("📚 Yüklenen Belgeler")
        documents = st.session_state.ai.rag.get_documents()
        if documents:
            df = pd.DataFrame(documents)
            st.dataframe(
                df[['name', 'type', 'chunk_count', 'uploaded_at']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Henüz belge yüklenmemiş.")
    
    elif selected == "📊 Analitik":
        st.markdown("<h1 class='gradient-text'>📊 Analitik Paneli</h1>", unsafe_allow_html=True)
        
        # Metrikler
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💬 Toplam Konuşma", metrics.get_total_conversations())
        with col2:
            st.metric("🔄 Günlük Sorgu", metrics.get_daily_queries())
        with col3:
            st.metric("⏱️ Ortalama Cevap", f"{metrics.get_avg_response_time()}s")
        with col4:
            st.metric("⭐ Memnuniyet", f"{metrics.get_satisfaction_rate()}%")
        
        # Grafikler
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=metrics.get_daily_dates(),
                y=metrics.get_daily_queries_list(),
                mode='lines+markers',
                name='Sorgular'
            ))
            fig.update_layout(
                title="Günlük Sorgu Sayısı",
                xaxis_title="Tarih",
                yaxis_title="Sorgu Sayısı"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure(data=[go.Pie(
                labels=['GPT-4', 'GPT-3.5', 'Diğer'],
                values=[60, 30, 10]
            )])
            fig.update_layout(title="Model Kullanım Dağılımı")
            st.plotly_chart(fig, use_container_width=True)
    
    elif selected == "⚙️ Ayarlar":
        st.markdown("<h1 class='gradient-text'>⚙️ Ayarlar</h1>", unsafe_allow_html=True)
        
        # Sistem ayarları
        with st.expander("🔧 Sistem Ayarları", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("API Anahtarı", type="password")
                st.selectbox("Varsayılan Model", ["gpt-4-turbo", "gpt-3.5-turbo"])
            with col2:
                st.checkbox("Web Araması", value=True)
                st.checkbox("Hafıza", value=True)
                st.checkbox("RAG", value=True)
        
        # Kişiselleştirme
        with st.expander("🎨 Kişiselleştirme"):
            st.color_picker("Ana Renk", "#ff6b6b")
            st.selectbox("Tema", ["Açık", "Koyu", "Sistem"])
            st.text_input("Asistan İsmi", value="Ryzen")
        
        # Güvenlik
        with st.expander("🔐 Güvenlik"):
            st.checkbox("İçerik Filtresi", value=True)
            st.number_input("Hız Limiti (dakika)", 10, 100, 60)
            st.checkbox("2FA", value=False)
    
    elif selected == "📤 Dışa Aktar":
        st.markdown("<h1 class='gradient-text'>📤 Dışa Aktar</h1>", unsafe_allow_html=True)
        
        # Dışa aktarma seçenekleri
        format_type = st.selectbox("📁 Format", ["JSON", "CSV", "PDF", "Markdown"])
        include_metadata = st.checkbox("📊 Metadata dahil et", value=True)
        
        if st.button("📥 Dışa Aktar", use_container_width=True):
            with st.spinner("📤 Dışa aktarılıyor..."):
                data = st.session_state.ai.export_conversation(
                    st.session_state.conversation_id,
                    format_type.lower()
                )
                st.download_button(
                    label="⬇️ İndir",
                    data=data,
                    file_name=f"conversation_{datetime.now().strftime('%Y%m%d')}.{format_type.lower()}",
                    mime_type="application/octet-stream"
                )
    
    elif selected == "🔌 API":
        st.markdown("<h1 class='gradient-text'>🔌 API Dokümantasyonu</h1>", unsafe_allow_html=True)
        
        st.code("""
        # API Kullanımı
        curl -X POST http://localhost:8000/ask \\
          -H "Content-Type: application/json" \\
          -H "Authorization: Bearer YOUR_API_KEY" \\
          -d '{"question": "Merhaba, nasılsın?"}'
        
        # Response
        {
          "response": "Merhaba! Ben Ryzen, size nasıl yardımcı olabilirim?",
          "metadata": {
            "model": "gpt-4-turbo",
            "tokens": 45,
            "timestamp": "2024-01-15T10:30:00Z"
          }
        }
        """, language="bash")
        
        # API anahtarı oluştur
        if st.button("🔄 Yeni API Anahtarı Oluştur"):
            new_key = auth.generate_api_key(st.session_state.user['username'])
            st.success(f"✅ Yeni API Anahtarı: `{new_key}`")
            st.warning("⚠️ Bu anahtarı güvenli bir yerde saklayın! Tekrar gösterilmeyecek.")
    
    elif selected == "❓ Yardım":
        st.markdown("<h1 class='gradient-text'>❓ Yardım</h1>", unsafe_allow_html=True)
        
        # Yardım içeriği
        with st.expander("🚀 Başlangıç Rehberi", expanded=True):
            st.markdown("""
            ### Hoş Geldiniz!
            Bu profesyonel AI asistanı size yardımcı olmak için tasarlanmıştır.
            
            **Özellikler:**
            - 💬 Gelişmiş sohbet arayüzü
            - 📁 Belge yükleme ve RAG
            - 📊 Analitik paneli
            - 🔌 API erişimi
            - 📤 Dışa aktarma
            - ⚙️ Özelleştirilebilir ayarlar
            
            **Kullanım İpuçları:**
            - Spesifik sorular sorun
            - Belge yükleyerek daha doğru cevaplar alın
            - Hızlı komutları kullanın
            """)
        
        with st.expander("❓ Sık Sorulan Sorular"):
            st.markdown("""
            **Q: Asistan hangi modelleri destekliyor?**
            A: GPT-4, GPT-3.5 ve yakında Claude 3.
            
            **Q: Verilerim güvende mi?**
            A: Evet, tüm veriler şifrelenir ve sadece sizin hesabınıza bağlıdır.
            
            **Q: Kaç belge yükleyebilirim?**
            A: 100 adet belge (toplam 50MB).
            """)

# ============================================
# FOOTER
# ============================================
st.divider()
st.caption("🧠 Ryzen AI Assistant Pro v2.0 | © 2026 | Tüm hakları saklıdır.")
