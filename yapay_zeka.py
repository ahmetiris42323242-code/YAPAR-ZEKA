import streamlit as st
import requests

# --- 1. ARAYÜZ VE BAŞLIK ---
st.set_page_config(page_title="Kotasız Web Yapay Zeka", page_icon="🤖")
st.title("🤖 Kotasız Web Yapay Zeka Asistanı")
st.caption("Ahmet İRİŞ tarafından yapılmıştır (Sınırsız Sürüm)")
st.markdown("---")

# --- 2. SOHBET GEÇMİŞİ (HAFIZA) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski sohbeti ekrana yansıt
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. KULLANICI GİRDİSİ VE YANIT ---
if prompt := st.chat_input("İstediğin kadar yaz kanka, kota sınırı yok..."):
    
    # Kullanıcı mesajını ekle ve ekrana yaz
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Yapay zeka yanıt penceresi
    with st.chat_message("assistant"):
        try:
            # Karakter talimatı
            system_instruction = (
                "Sen Ahmet İRİŞ'in en yakın kankasısın. Sadece Türkçe konuş. "
                "Cevapların çok kısa, samimi ve net olsun. Mutlaka emoji kullan. "
                "Asla soru sorma. Fiziksel bir bedenin varmış gibi uydurma."
            )
            
            # DuckDuckGo AI Chat için bağlantı kuruyoruz (Kotasız hat)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "x-vqd-4": "1"  # DuckDuckGo ücretsiz havuz tetikleyicisi
            }
            
            # İlk istek: Oturum tokenı (VQD) alıyoruz
            token_url = "https://duckduckgo.com/duckchat/v1/status"
            headers["x-vqd-accept"] = "1"
            res_token = requests.get(token_url, headers=headers)
            vqd = res_token.headers.get("x-vqd-4")

            # Mesaj geçmişini hazırlıyoruz (Talimatla birleştirerek)
            messages_to_send = [{"role": "user", "content": f"[Sistem Talimatı: {system_instruction}] {msg['content']}" if i == 0 else msg['content']} for i, msg in enumerate(st.session_state.messages)]

            chat_url = "https://duckduckgo.com/duckchat/v1/chat"
            headers["x-vqd-4"] = vqd
            headers["Content-Type"] = "application/json"
            del headers["x-vqd-accept"]

            # Model olarak tamamen ücretsiz ve kotasız olan Mixtral modelini seçtik (Meta değil!)
            data = {
                "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "messages": messages_to_send
            }

            # İsteği gönder
            response = requests.post(chat_url, headers=headers, json=data)
            
            # Gelen veriyi temizleme (DuckDuckGo stream formatında gönderir)
            lines = response.text.split("\n")
            full_reply = ""
            for line in lines:
                if line.startswith("data:"):
                    try:
                        content_json = line[5:].strip()
                        if content_json == "[DONE]":
                            break
                        chunk = requests.json.loads(content_json)
                        if "message" in chunk:
                            full_reply += chunk["message"]
                    except:
                        continue

            if full_reply:
                st.markdown(full_reply)
                # Hafızaya ekle
                st.session_state.messages.append({"role": "assistant", "content": full_reply})
            else:
                st.error("Kotasız hatta anlık bir yoğunluk oldu, lütfen tekrar mesaj gönder kanka.")
                
        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")
