import streamlit as st
import requests
from duckduckgo_search import DDGS

# --- AYARLAR ---
st.set_page_config(page_title="Ahmet İRİŞ Asistanı", page_icon="🤖")
API_KEY = st.secrets["GEMINI_API_KEY"]
URL = "https://router.flatkey.ai/v1/chat/completions"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        search_instruction = ""
        # Hız Optimizasyonu: Sadece "ara" veya "güncel" kelimesi geçince internete git
        if any(word in prompt.lower() for word in ["ara", "güncel", "yeni", "modlar"]):
            with st.spinner("2026 verileri taranıyor..."):
                try:
                    results = DDGS().text(f"{prompt} 2026", max_results=3)
                    search_summary = "\n".join([f"- {r['body']}" for r in results])
                    search_instruction = f"\n\n[GÜNCEL VERİLER]: {search_summary}"
                except: pass

        system_instructions = (
            "Sen Ahmet İRİŞ tarafından tasarlanmış bir asistanısın. "
            "Kim olduğunu sorarlarsa Ahmet İRİŞ'i belirt. "
            "'Çağın'ı tanıyor musun?' sorusuna: 'O sırada Çağın aga, ben ne alaka ya ha ha ha!' de."
        )

        messages = [{"role": "system", "content": system_instructions}] + st.session_state.messages[:-1]
        messages.append({"role": "user", "content": prompt + search_instruction})
            
        try:
            response = requests.post(URL, headers=headers, json={"model": "gpt-4o", "messages": messages})
            answer = response.json()['choices'][0]['message']['content']
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except:
            st.error("Bir hata oluştu.")
