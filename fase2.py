import streamlit as st
import requests
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN Y CREDENCIALES ---
GEMINI_KEY = "AIzaSyBGZ7-k5lvJHp-CaX7ruwG90jEqbvC0zXM"
SUPABASE_URL = "https://pmqmqeukhufaqecbuodg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBtcW1xZXVraHVmYXFlY2J1b2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE0NzY2MzksImV4cCI6MjA4NzA1MjYzOX0.Hr_3LlyI43zEoV4ZMn28gSKiBABK35VPTWip9rjC-zc"

st.set_page_config(page_title="ProfeEduca | Fase 2", page_icon="🍎", layout="wide")

# Inicializar Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. ESTILOS CSS (Tu diseño original) ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top, #0f172a 0%, #020617 100%); color: #f8fafc; }
    @keyframes worm-move {
        0%, 100% { transform: translate(45px, -30px) scale(1); opacity: 0; }
        25% { transform: translate(30px, -45px) scale(1.1); opacity: 1; }
        50% { transform: translate(0px, -50px) scale(1.2); opacity: 1; }
        75% { transform: translate(-30px, -45px) scale(1.1); opacity: 1; }
        90% { transform: translate(-45px, -30px) scale(1); opacity: 0; }
    }
    .apple-container { position: relative; display: inline-block; font-size: 8rem; margin-top: 20px; }
    .worm-icon { position: absolute; font-size: 3rem; animation: worm-move 5s ease-in-out infinite; }
    .brand-header { font-size: 2.5rem; font-weight: 900; color: #38bdf8; text-align: center; }
    .stButton>button { width: 100%; border-radius: 10px; text-align: left; padding: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. MOTOR DE IA (Gemini 1.5 Flash) ---
def llamar_ia_gemini(instruccion):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": instruccion}]}]}
    try:
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        return f"Error de IA: {res.status_code}"
    except:
        return "Error de conexión con la IA."

# --- 4. INTERFAZ DE USUARIO ---
if 'p' not in st.session_state: st.session_state.p = "inicio"

col_menu, col_visual = st.columns([1, 1.5])

with col_menu:
    st.markdown("### 🚀 Menú de Funciones")
    if st.button("🏠 Inicio"): st.session_state.p = "inicio"
    if st.button("📝 Planeación ABCD"): st.session_state.p = "plan"
    if st.button("📓 Escrito Reflexivo"): st.session_state.p = "reflex"
    if st.button("📅 Diario del Maestro"): st.session_
