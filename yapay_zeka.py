streamlit
groq
st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Geliştirici kimlik kontrolü (Yolda yakalama)
        if "ahmet iriş kimdir" in prompt.lower() or "ahmet iriş kim" in prompt.lower():
            answer = "Ahmet İRİŞ, bu harika web tabanlı yapay zeka asistanı projesinin arkasındaki asıl geliştirici, kurucu ve liderdir! 🚀 Projenin mimarı o, ben ise onun tasarlayıp kodladığı yapay zeka asistanıyım. 😎👨‍💻"
            message_placeholder.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            try:
                system_instruction = (
                    "Sen Ahmet İRİŞ tarafından geliştirilmiş; samimi, zeki ve kanka ruhlu bir asistansın. "
                    "Asla hayali geçmiş konular açma, asla kaba olma, sadece kullanıcıya odaklan. "
                    "Sadece Türkçe konuş ve emojileri tadında kullan."
                )
                
                model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction)
                
                gemini_history = []
                for msg in st.session_state.messages[:-1]:
                    role = "model" if msg["role"] == "assistant" else "user"
                    gemini_history.append({"role": role, "parts": [msg["content"]]})
                
                chat = model.start_chat(history=gemini_history)
                response = chat.send_message(prompt)
                
                message_placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                message_placeholder.markdown(f"❌ Bir hata oluştu: `{e}`")
                
