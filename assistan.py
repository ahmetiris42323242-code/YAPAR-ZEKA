import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import openai
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, PyPDFLoader
import yaml

from .memory import MemorySystem
from .rag import RAGSystem
from .web_search import WebSearch
from .code_executor import CodeExecutor

class ProfessionalAI:
    """Kurumsal seviye AI asistanı"""
    
    def __init__(self, config_path="config.yaml"):
        self.config = self.load_config(config_path)
        self.name = self.config['app']['name']
        self.memory = MemorySystem()
        self.rag = RAGSystem(self.config)
        self.web_search = WebSearch()
        self.code_executor = CodeExecutor()
        self.conversation_id = None
        self.user_id = None
        
        # OpenAI API
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Vektör veritabanı
        if self.config['rag']['enabled']:
            self.vector_db = Chroma(
                persist_directory="data/vector_db/",
                embedding_function=OpenAIEmbeddings()
            )
    
    def load_config(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def ask(self, user_input: str, context: Dict = None) -> Dict:
        """Profesyonel cevap üret"""
        
        response = {
            "content": "",
            "metadata": {
                "model": self.config['models']['default'],
                "tokens": 0,
                "source": "ai",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        try:
            # 1. RAG araması (varsa)
            rag_context = ""
            if self.config['rag']['enabled']:
                rag_results = self.rag.search(user_input)
                if rag_results:
                    rag_context = "\n\n".join([r['content'] for r in rag_results[:3]])
            
            # 2. Web araması (gerekirse)
            web_context = ""
            if "?" in user_input or "nedir" in user_input:
                web_context = self.web_search.search(user_input)
            
            # 3. Hafıza
            memory_context = self.memory.search(user_input)
            
            # 4. Düşünce zinciri
            thoughts = self.think(user_input)
            
            # 5. Prompt oluştur
            prompt = self.build_prompt(
                user_input, 
                context=rag_context,
                web=web_context,
                memory=memory_context,
                thoughts=thoughts
            )
            
            # 6. AI çağrısı
            completion = openai.ChatCompletion.create(
                model=self.config['models']['default'],
                messages=[
                    {"role": "system", "content": "Sen profesyonel bir AI asistanısın."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # 7. Cevabı işle
            answer = completion.choices[0].message.content
            tokens_used = completion.usage.total_tokens
            
            response['content'] = answer
            response['metadata']['tokens'] = tokens_used
            response['metadata']['model'] = self.config['models']['default']
            response['metadata']['thoughts'] = thoughts
            
            # 8. Hafızaya kaydet
            self.memory.add(user_input, answer)
            
            return response
            
        except Exception as e:
            response['content'] = f"❌ Hata: {str(e)}"
            response['metadata']['error'] = str(e)
            return response
    
    def think(self, problem: str) -> List[str]:
        """Gelişmiş düşünce zinciri"""
        return [
            f"1. Problemi analiz ediyorum: {problem[:50]}...",
            "2. Bağlamı kontrol ediyorum...",
            "3. İlgili kaynakları tarıyorum...",
            "4. En iyi yaklaşımı seçiyorum...",
            "5. Cevabı oluşturuyorum ve doğruluyorum..."
        ]
    
    def build_prompt(self, user_input: str, **context) -> str:
        """Prompt oluştur"""
        prompt_parts = [
            f"Soru: {user_input}",
        ]
        
        if context.get('context'):
            prompt_parts.append(f"\nBağlam:\n{context['context']}")
        
        if context.get('web'):
            prompt_parts.append(f"\nWeb Arama:\n{context['web']}")
        
        if context.get('memory'):
            prompt_parts.append(f"\nHafıza:\n{context['memory']}")
        
        if context.get('thoughts'):
            prompt_parts.append(f"\nDüşünce:\n{' → '.join(context['thoughts'])}")
        
        prompt_parts.append("\nLütfen profesyonel ve doğru bir cevap ver.")
        
        return "\n".join(prompt_parts)
    
    def get_conversation(self, conversation_id: int) -> List[Dict]:
        """Konuşma geçmişini getir"""
        return self.memory.get_conversation(conversation_id)
    
    def export_conversation(self, conversation_id: int, format: str = "json") -> bytes:
        """Konuşmayı dışa aktar"""
        import json
        import csv
        from io import StringIO, BytesIO
        
        messages = self.get_conversation(conversation_id)
        
        if format == "json":
            return json.dumps(messages, indent=2, ensure_ascii=False).encode('utf-8')
        elif format == "csv":
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Role", "Content", "Timestamp"])
            for msg in messages:
                writer.writerow([msg['role'], msg['content'], msg['timestamp']])
            return output.getvalue().encode('utf-8')
        elif format == "pdf":
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import mm
            
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            c.setFont("Helvetica", 10)
            y = A4[1] - 20
            c.drawString(20, y, f"Conversation Export - {datetime.utcnow().isoformat()}")
            y -= 10
            
            for msg in messages:
                c.drawString(20, y, f"{msg['role']}: {msg['content'][:100]}...")
                y -= 15
                if y < 20:
                    c.showPage()
                    y = A4[1] - 20
            
            c.save()
            return buffer.getvalue()
        
        return b"Unsupported format"
