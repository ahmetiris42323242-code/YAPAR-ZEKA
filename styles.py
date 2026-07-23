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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            transition: all 0.3s !important;
        }
        
        .stButton > button:hover {
            transform: scale(1.05) !important;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2) !important;
        }
        
        /* Input alanları */
        .stTextInput > div > div > input {
            border-radius: 25px !important;
            border: 2px solid #667eea !important;
            padding: 10px 20px !important;
        }
        
        /* Metrik kartları */
        .stMetric {
            background: rgba(255,255,255,0.05) !important;
            backdrop-filter: blur(10px) !important;
            border-radius: 15px !important;
            padding: 15px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
        }
        
        /* Animasyonlar */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Loading spinner */
        .stSpinner > div {
            border-color: #667eea !important;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #1a1a2e;
        }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #667eea, #764ba2);
            border-radius: 10px;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .gradient-text {
                font-size: 1.8rem !important;
            }
            .stChatMessage[data-testid="user"],
            .stChatMessage[data-testid="assistant"] {
                margin: 0 !important;
            }
        }
    </style>
    """
