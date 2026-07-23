def load_css():
    return """
    <style>
        /* Ana gradient başlık */
        .gradient-text {
            background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        
        /* Chat mesajları */
        .stChatMessage {
            border-radius: 12px !important;
            padding: 12px !important;
            margin: 6px 0 !important;
            animation: fadeIn 0.3s ease-in;
        }
        
        .stChatMessage[data-testid="user"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            margin-left: 20% !important;
        }
        
        .stChatMessage[data-testid="assistant"] {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
            color: white !important;
            margin-right: 20% !important;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
        }
        
        /* Butonlar */
        .stButton > button {
            border-radius: 25px !important;
            background:
