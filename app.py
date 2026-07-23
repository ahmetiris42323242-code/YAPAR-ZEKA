"""
RYZEN AI ENTERPRISE - TEK DOSYA KURUMSAL ASİSTAN
Versiyon: 3.0.0
Tüm özellikler tek dosyada!
"""

import streamlit as st
import os
import json
import hashlib
import time
import re
import asyncio
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import string
from io import BytesIO, StringIO
import csv

# ============================================
# SAYFA KONFIGÜRASYONU
# ============================================
st.set_page_config(
    page_title="🏢 Ryzen AI Enterprise",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS - KURUMSAL TEMA
# ============================================
st.markdown("""
<style>
    /* ===== KURUMSAL RENKLER ===== */
    :root {
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --secondary: #7c3aed;
        --success: #059669;
        --danger: #dc2626;
        --warning: #d97706;
        --dark: #0f172a;
        --dark-secondary: #1e293b;
        --light: #f8fafc;
        --gray: #94a3b8;
    }
    
    /* ===== BAŞLIKLAR ===== */
    .enterprise-title {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        padding: 1rem 0;
        letter-spacing: -0.5px;
    }
    
    .enterprise-badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        padding: 4px 16px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 1.5rem 0 1rem 0;
        color: var(--light);
    }
    
    /* ===== KARTLAR ===== */
    .card {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.06);
        transition: all 0.3s ease;
        margin-bottom: 12px;
    }
    
    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(37, 99, 235, 0.15);
        border-color: rgba(37, 99, 235, 0.3);
    }
    
    .card-gradient {
        background: linear-gradient(135deg, rgba(37,99,235,0.1), rgba(124,58,237,0.1));
        border: 1px solid rgba(37,99,235,0.2);
    }
    
    /* ===== CHAT MESAJLARI ===== */
    .chat-user {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 14px 22px;
        margin: 8px 0 8px auto;
        max-width: 75%;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
        animation: slideInRight 0.3s ease;
    }
    
    .chat-assistant {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px 18px 18px 4px;
        padding: 14px 22px;
        margin: 8px auto 8px 0;
        max-width: 75%;
        animation: slideInLeft 0.3s ease;
    }
    
    .chat-assistant .agent-name {
        color: var(--secondary);
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    /* ===== SIDEBAR ===== */
    .sidebar-header {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        padding: 24px 20px;
        border-radius: 16px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    
    .sidebar-header .avatar {
        font-size: 3.5rem;
        margin-bottom: 8px;
    }
    
    .sidebar-header h3 {
        margin: 4px 0;
        font-weight: 600;
    }
    
    .sidebar-header p {
        opacity: 0.8;
        font-size: 0.85rem;
        margin: 0;
    }
    
    /* ===== STAT KARTLARI ===== */
    .stat-card {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
        transition: all 0.3s;
    }
    
    .stat-card:hover {
        background: rgba(255,255,255,0.06);
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
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }
    
    /* ===== BUTONLAR ===== */
    .btn-primary {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border: none;
        border-radius: 50px;
        padding: 12px 30px;
        font-weight: 600;
        transition: all 0.3s;
        cursor: pointer;
        width: 100%;
    }
    
    .btn-primary:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 30px rgba(37, 99, 235, 0.4);
    }
    
    .btn-outline {
        background: transparent;
        border: 2px solid var(--primary);
        color: var(--primary);
        border-radius: 50px;
        padding: 10px 28px;
        font-weight: 600;
        transition: all 0.3s;
        cursor: pointer;
        width: 100%;
    }
    
    .btn-outline:hover {
        background: var(--primary);
        color: white;
    }
    
    /* ===== ANİMASYONLAR ===== */
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease;
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: var(--dark);
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--primary), var(--secondary));
        border-radius: 10px;
    }
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .enterprise-title {
            font-size: 1.8rem;
        }
        .chat-user, .chat-assistant {
            max-width: 90%;
        }
        .stat-number {
            font-size: 1.5rem;
        }
    }
    
    /* ===== BADGE ANIMASYON ===== */
    .live-badge {
        animation: pulse 1.5s infinite;
        display: inline-block;
    }
    
    /* ===== TAB MENU ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 6px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        transition: all 0.3s;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white !important;
    }
    
    /* ===== METRIK ===== */
    .stMetric {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 12px;
        border: 1px solid rgba(255,255,255,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# VERİ MODELLERİ
# ============================================
@dataclass
class User:
    id: str
    username: str
    email: str
    password_hash: str
    role: str = "user"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_login: Optional[str] = None
    preferences: Dict = field(default_factory=dict)

@dataclass
class Message:
    id: str
    conversation_id: str
    role: str
    content: str
    agent: Optional[str] = None
    model: Optional[str] = None
    tokens: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Conversation:
    id: str
    user_id: str
    title: str
    messages: List[Message] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Document:
    id: str
    user_id: str
    name: str
    content: str
    type: str
    chunks: int = 0
    uploaded_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Agent:
    name: str
    role: str
    description: str
    icon: str
    system_prompt: str
    temperature: float = 0.7
    is_active: bool = True

# ============================================
# VERİTABANI (İN-MEMORY)
# ============================================
class Database:
    """In-memory veritabanı - JSON ile persistence"""
    
    def __init__(self, db_file="enterprise_db.json"):
        self.db_file = db_file
        self.data = {
            "users": {},
            "conversations": {},
            "messages": {},
            "documents": {},
            "feedback": {},
            "analytics": {}
        }
        self.load()
    
    def load(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except:
                pass
    
    def save(self):
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get(self, collection: str, key: str):
        return self.data.get(collection, {}).get(key)
    
    def set(self, collection: str, key: str, value: Any):
        if collection not in self.data:
            self.data[collection] = {}
        self.data[collection][key] = value
        self.save()
    
    def delete(self, collection: str, key: str):
        if collection in self.data and key in self.data[collection]:
            del self.data[collection][key]
            self.save()
    
    def list(self, collection: str) -> List[Dict]:
        return list(self.data.get(collection, {}).values())
    
    def find(self, collection: str, **filters) -> List[Dict]:
        items = self.data.get(collection, {}).values()
        result = []
        for item in items:
            match = True
            for key, value in filters.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                result.append(item)
        return result
    
    def count(self, collection: str) -> int:
        return len(self.data.get(collection, {}))

# ============================================
# YAPAY ZEKA ÇEKİRDEĞİ
# ============================================
class RyzenAI:
    """Ana AI Motoru - Multi-Agent, RAG, Memory"""
    
    def __init__(self, db: Database):
        self.db = db
        self.name = "Ryzen"
        self.agents = self._init_agents()
        self.memory_file = "memory.json"
        self.memory = self._load_memory()
    
    def _init_agents(self) -> Dict[str, Agent]:
        return {
            "technical": Agent(
                name="TechPro",
                role="Teknik Uzman",
                description="Kod, sistem, veri yapıları ve teknoloji çözümleri",
                icon="💻",
                system_prompt="Sen bir teknoloji uzmanısın. Kod yaz, hata ayıkla, sistem tasarla.",
                temperature=0.3
            ),
            "creative": Agent(
                name="CreativeMind",
                role="Yaratıcı Yazar",
                description="İçerik, şiir, hikaye ve yaratıcı fikirler",
                icon="🎨",
                system_prompt="Sen yaratıcı bir yazarsın. İlham verici, özgün ve etkileyici içerikler üret.",
                temperature=0.9
            ),
            "analyst": Agent(
                name="DataAnalyst",
                role="Veri Analisti",
                description="Veri analizi, raporlama, istatistik ve içgörüler",
                icon="📊",
                system_prompt="Sen bir veri analisti uzmanısın. Verileri yorumla, grafikler oluştur.",
                temperature=0.4
            ),
            "business": Agent(
                name="BizPro",
                role="İş Danışmanı",
                description="Strateji, pazarlama, yönetim ve iş geliştirme",
                icon="💼",
                system_prompt="Sen bir iş danışmanısın. Stratejik tavsiyeler ver, iş planları oluştur.",
                temperature=0.6
            )
        }
    
    def _load_memory(self) -> List[Dict]:
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_memory(self):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def _select_agent(self, query: str) -> Agent:
        """Soruya göre en uygun agent'ı seç"""
        q = query.lower()
        
        # Teknik
        if any(w in q for w in ["kod", "python", "sistem", "hata", "çözüm", "teknoloji", "server", "api"]):
            return self.agents["technical"]
        
        # Yaratıcı
        if any(w in q for w in ["şiir", "hikaye", "masal", "yaratıcı", "sanat", "edebiyat", "renk"]):
            return self.agents["creative"]
        
        # Analist
        if any(w in q for w in ["veri", "istatistik", "grafik", "analiz", "rapor", "sayı", "oran"]):
            return self.agents["analyst"]
        
        # İş
        if any(w in q for w in ["strateji", "pazarlama", "yönetim", "iş", "satış", "müşteri"]):
            return self.agents["business"]
        
        # Varsayılan
        return self.agents["technical"]
    
    def web_search(self, query: str) -> str:
        """Web araması"""
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data.get('AbstractText'):
                return data['AbstractText'][:500]
            
            if data.get('RelatedTopics'):
                for topic in data['RelatedTopics'][:3]:
                    if topic.get('Text'):
                        return topic['Text'][:300]
            
            return "Arama sonucu bulunamadı."
        except:
            return "Web araması şu anda kullanılamıyor."
    
    def think(self, problem: str, agent: Agent) -> List[str]:
        """Düşünce zinciri"""
        return [
            f"🎯 {agent.name} olarak problemi analiz ediyorum...",
            f"📋 Konu: {problem[:60]}...",
            "🔍 İlgili bağlamı kontrol ediyorum...",
            "⚡ En iyi yaklaşımı seçiyorum...",
            "✅ Cevabı oluşturuyorum ve doğruluyorum..."
        ]
    
    def ask(self, user_input: str, agent_name: Optional[str] = None, 
            model: str = "GPT-4", temperature: float = 0.7) -> Dict:
        """Soruya cevap üret"""
        
        # Agent seçimi
        if agent_name and agent_name in self.agents:
            agent = self.agents[agent_name]
        else:
            agent = self._select_agent(user_input)
        
        # Düşünce zinciri
        thoughts = self.think(user_input, agent)
        
        # Web araması
        web_result = ""
        if any(w in user_input for w in ["?", "nedir", "nasıl", "kimdir", "nerede"]):
            web_result = self.web_search(user_input)
        
        # Hafıza ara
        memory_context = self._search_memory(user_input)
        
        # Cevap oluştur
        response_parts = []
        
        # Agent bilgisi
        response_parts.append(f"🤖 **{agent.icon} {agent.name}** ({agent.role})\n")
        
        # Web sonucu
        if web_result and "bulunamadı" not in web_result and "kullanılamıyor" not in web_result:
            response_parts.append(f"🌐 **Web Arama Sonucu:**\n{web_result}\n")
        
        # Hafıza
        if memory_context:
            response_parts.append(f"📝 **Hafızamdan hatırlıyorum:**\n{memory_context[:200]}...\n")
        
        # Düşünce zinciri
        response_parts.append("💭 **Düşünce Süreci:**")
        for t in thoughts:
            response_parts.append(f"  • {t}")
        response_parts.append("")
        
        # Ana cevap
        response_parts.append(f"✨ **Cevap:**")
        response_parts.append(f"Merhaba! {agent.name} olarak sana yardımcı olabilirim. ")
        response_parts.append(f"Sorun: '{user_input}' hakkında detaylı bilgi vermek isterim.")
        response_parts.append(f"\n💡 **Öneri:** Daha spesifik olursan daha iyi cevap verebilirim.")
        
        response = "\n".join(response_parts)
        
        # Hafızaya kaydet
        self.memory.append({
            "user": user_input,
            "ai": response,
            "agent": agent.name,
            "model": model,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.memory) > 200:
            self.memory = self.memory[-200:]
        self._save_memory()
        
        return {
            "content": response,
            "agent": agent.name,
            "agent_icon": agent.icon,
            "model": model,
            "tokens": len(response.split()),
            "thoughts": thoughts,
            "web_search": bool(web_result and "bulunamadı" not in web_result),
            "timestamp": datetime.now().isoformat()
        }
    
    def _search_memory(self, query: str, limit: int = 3) -> str:
        """Hafızada ara"""
        results = []
        q_words = set(query.lower().split())
        for entry in reversed(self.memory):
            text = f"{entry['user']} {entry['ai']}".lower()
            score = sum(1 for w in q_words if w in text)
            if score > 0:
                results.append((score, entry))
        results.sort(key=lambda x: x[0], reverse=True)
        
        if results:
            context = []
            for _, entry in results[:limit]:
                context.append(f"👤 {entry['user'][:80]}")
                context.append(f"🤖 {entry['ai'][:80]}...")
            return "\n".join(context)
        return ""
    
    def get_agents(self) -> List[Dict]:
        """Tüm agent'ları getir"""
        return [
            {
                "name": a.name,
                "role": a.role,
                "description": a.description,
                "icon": a.icon,
                "is_active": a.is_active
            }
            for a in self.agents.values()
        ]
    
    def get_stats(self) -> Dict:
        """İstatistikleri getir"""
        return {
            "total_conversations": len(self.memory),
            "last_activity": self.memory[-1]['timestamp'] if self.memory else "Yok",
            "agents_used": list(set([m.get('agent', 'bilinmiyor') for m in self.memory])),
            "total_tokens": sum([len(m['ai'].split()) for m in self.memory])
        }

# ============================================
# AUTHENTICATION
# ============================================
class AuthManager:
    """Kimlik doğrulama ve yetkilendirme"""
    
    def __init__(self, db: Database):
        self.db = db
        self.session_t
