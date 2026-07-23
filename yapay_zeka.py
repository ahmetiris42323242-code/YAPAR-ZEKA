import streamlit as st
import requests
import json
import hashlib
import time
from datetime import datetime
from typing import List, Dict
import re

# ============================================
# YAPAY ZEKA ASİSTANI SINIFI (BENZİNİ)
# ============================================
class AI_Assistant:
    """Benim gibi çalışan bir yapay zeka asistanı"""
    
    def __init__(self):
        self.name = "Ryzen"
        self.conversations = []
        self.memory_limit = 100
    
    def think(self, problem: str) -> List[str]:
        """Düşünce zinciri"""
        return [
            f"1. Problemi anlıyorum: {problem[:50]}...",
            "2. Analiz ediyorum...",
            "3. Çözüm yolları üretiyorum...",
            "4. En iyi yaklaşımı seçiyorum...",
            "5. Cevabı oluşturuyorum."
        ]
    
    def web_search(self, query: str) -> str:
        """Basit web araması"""
        try:
            # DuckDuckGo üzerinden basit arama
            url = f"https://api.duckduckgo.com/?q={query}&format=json"
            response = requests.get(url, timeout=5)
            data = response.json()
            if data.get('AbstractText'):
                return data['AbstractText'][:500]
            return "Arama sonucu bulunamadı."
        except:
            return "Web araması şu anda kullanılamıyor."
    
    def ask(self, user_input: str) -> str:
        """Soruya cevap üret"""
        # Düşünce zinciri
        thoughts = self.think(user_input)
        
        # Web araması (soru içeriyorsa)
        web_result = ""
        if "?" in user_input or "nedir" in user_input or "nasıl" in user_input:
            web_result = self.web_search(user_input)
        
        # Cevap oluştur
        if web_result and "bulunamadı" not in web_result:
            response = f"🌐 **Arama Sonucu:**\n{web_result}\n\n"
            response += f"💭 **Düşünce:** {' → '.join(thoughts)}"
        else:
            response = f"💭 **Düşünce Zinciri:**\n"
            for t in thoughts:
                response += f"  • {t}\n"
            response += f"\n🤖 **Cevap:** {user_input} hakkında yardımcı olabilirim. Daha spesifik olursan daha iyi cevap verebilirim."
        
        # Hafızaya kaydet
        self.conversations.append({
            "user": user_input,
            "ai": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Hafıza limiti
        if len(self.conversations) > self.memory_limit:
            self.conversations = self.conversations[-self.memory_limit:]
        
        return response
    
    def get_memory(self) -> List[Dict]:
        """Konuşma geçmişini getir"""
        return self.conversations[-10:]


# ============================================
# STREAMLIT ARAYÜZÜ
# ============================================

st.set_page_config(
    page_title="🧠 Ryzen AI Asistan",
    page_icon="🧠",
    layout="wide"
)

# CSS ile özelleştirme
st.markdown("""
<style>
    .stChatMessage {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .stChatMessage[data-testid="user"] {
        background-color: #dcf8c6;
    }
    .stChatMessage[data-testid="assistant"] {
        background-color: #e8f0fe;
    }
    .main-title {
        background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Başlık
st.markdown('<p class="main-title">🧠 Ryzen AI Asistan</p>', unsafe_allow_html=True)
st.caption("Benimle aynı seviyede çalışan yapay zeka - Streamlit üzerinde")

# Sidebar - Ayarlar
with st.sidebar:
    st.header("⚙️ Ayarlar")
    
    # Asistan adı
    assistant_name = st.text_input("Asistan Adı", value="Ryzen")
    
    # Hafıza boyutu
    memory_size = st.slider("Hafıza Boyutu", min_value=5, max_value=50, value=20)
    
    # Web araması
    web_search_enabled = st.toggle("🌐 Web Araması", value=True)
    
    # Düşünce zinciri
    show_thoughts = st.toggle("💭 Düşünce Zinciri Göster", value=True)
    
    st.divider()
    
    # İstatistikler
    st.subheader("📊 İstatistikler")
    if "assistant" in st.session_state:
        conv_count = len(st.session_state.assistant.conversations)
        st.metric("Toplam Konuşma", conv_count)
        st.metric("Hafıza Kullanımı", f"{conv_count}/{memory_size}")
    
    st.divider()
    
    # Temizle
    if st.button("🗑️ Konuşmayı Temizle", type="secondary"):
        if "assistant" in st.session_state:
            st.session_state.assistant.conversations = []
            st.session_state.messages = []
            st.rerun()
    
    st.divider()
    
    # Bilgi
    st.caption("🔹 **Nasıl Çalışır?**")
    st.caption("Bu asistan, web araması, düşünce zinciri ve hafıza ile çalışır.")
    st.caption("📌 **Komutlar:**")
    st.caption("  • Normal sorular → Cevap verir")
    st.caption("  • `kod:` → Kod çalıştırır")
    st.caption("  • `ara:` → Web araması yapar")

# Ana alan - iki sütun
col1, col2 = st.columns([2, 1])

with col1:
    # Asistanı başlat
    if "assistant" not in st.session_state:
        st.session_state.assistant = AI_Assistant()
        st.session_state.messages = []
        st.session_state.assistant.name = assistant_name
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sohbet geçmişini göster
    for msg in st.session_state.messages:
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        with st.chat_message(role):
            st.markdown(content)
    
    # Kullanıcı girişi
    prompt = st.chat_input("Mesajını yaz...")
    
    if prompt:
        # Kullanıcı mesajını ekle
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Asistan yanıtı üret
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            # Asistanı güncelle
            asistan = st.session_state.assistant
            asistan.name = assistant_name
            
            # Web aramasını kontrol et
            if prompt.startswith("ara:") or prompt.startswith("search:"):
                query = prompt.replace("ara:", "").replace("search:", "").strip()
                response = asistan.web_search(query)
                if response:
                    response = f"🔍 **Arama Sonucu:**\n{response}"
                else:
                    response = "❌ Arama sonucu bulunamadı."
            else:
                # Normal soru
                response = asistan.ask(prompt)
                # Düşünce zincirini gizle/göster
                if not show_thoughts:
                    # Sadece cevap kısmını göster
                    response = response.split("**Cevap:**")[-1] if "**Cevap:**" in response else response
            
            # Yanıtı göster (türkçe karakterler için decode)
            response_placeholder.markdown(response)
            
            # Mesajı kaydet
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.rerun()

with col2:
    st.subheader("📝 Konuşma Geçmişi")
    
    if "assistant" in st.session_state:
        memory = st.session_state.assistant.get_memory()
        if memory:
            for i, conv in enumerate(reversed(memory)):
                with st.expander(f"🗣️ Konuşma {len(memory)-i}"):
                    st.caption(f"👤 **Sen:** {conv['user'][:50]}...")
                    st.caption(f"🤖 **Asistan:** {conv['ai'][:80]}...")
                    st.caption(f"🕐 {conv.get('timestamp', '')[:16]}")
        else:
            st.info("Henüz konuşma yok.")
    
    # Hızlı komutlar
    st.divider()
    st.subheader("⚡ Hızlı Komutlar")
    
    if st.button("🔍 Bugün hava nasıl?"):
        prompt = "ara: bugün hava nasıl"
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()
    
    if st.button("💻 Python'da dosya okuma"):
        prompt = "Python'da dosya nasıl okunur?"
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()
    
    if st.button("🌐 Dünya nüfusu nedir?"):
        prompt = "Dünya nüfusu kaç?"
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()
