import streamlit as st
from PIL import Image
import base64
import io
import random
import requests
from supabase import create_client, Client

# --- CONFIGURACIÓN Y CREDENCIALES ---
GEMINI_KEY = "AIzaSyBGZ7-k5lvJHp-CaX7ruwG90jEqbvC0zXM"
SUPABASE_URL = "https://pmqmqeukhufaqecbuodg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBtcW1xZXVraHVmYXFlY2J1b2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE0NzY2MzksImV4cCI6MjA4NzA1MjYzOX0.Hr_3LlyI43zEoV4ZMn28gSKiBABK35VPTWip9rjC-zc"

st.set_page_config(page_title="ProfeEduca F1: Registro", page_icon="👤", layout="wide")

# Inicializar Supabase de forma independiente
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- ESTILO DARK-CORPORATE ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top, #0f172a 0%, #020617 100%); color: #f8fafc; }
    .profile-pic { border-radius: 50%; width: 150px; height: 150px; border: 4px solid #38bdf8; box-shadow: 0 0 20px #38bdf866; }
    .stButton>button { border-radius: 10px; background: linear-gradient(90deg, #0ea5e9 0%, #2563eb 100%); color: white; font-weight: bold; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- IA: GEMINI 1.5 FLASH (Validación de Perfil) ---
def ia_validar_perfil(nombre, vision):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    prompt = f"Eres un mentor de CONAFE. El maestro {nombre} dice que su visión es: '{vision}'. Dale una breve frase de bienvenida personalizada que lo motive a usar el modelo ABCD."
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, json=payload)
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Bienvenido al ecosistema ProfeEduca, transformando la educación comunitaria."

# --- FLUJO DE LA FASE 1 ---
if 'step' not in st.session_state: st.session_state.step = "login"

st.title("🛡️ Fase 1: Identidad Digital")

if st.session_state.step == "login":
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        email = st.text_input("Correo Institucional")
        if st.button("Iniciar Registro"):
            if "@" in email:
                st.session_state.email = email
                st.session_state.step = "perfil"
                st.rerun()

elif st.session_state.step == "perfil":
    st.subheader("Configura tu Perfil Profesional")
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        foto = st.file_uploader("Sube tu foto", type=['jpg', 'png'])
        if foto: st.image(foto, width=150)
        
    with col_b:
        nombre = st.text_input("Nombre Completo")
        vision = st.text_area("¿Cuál es tu compromiso con la comunidad?")
        
        if st.button("Generar Bienvenida con IA"):
            with st.spinner("La IA está analizando tu perfil..."):
                mensaje = ia_validar_perfil(nombre, vision)
                st.session_state.mensaje_ia = mensaje
                st.info(mensaje)

    if st.button("Finalizar y Sincronizar con Supabase"):
        try:
            # Guardar en Supabase (Asegúrate de tener la tabla 'usuarios')
            data = {"email": st.session_state.email, "nombre": nombre, "mensaje_ia": st.session_state.get('mensaje_ia', "")}
            supabase.table("usuarios").insert(data).execute()
            st.success("¡Datos guardados! Fase 1 completada.")
            st.balloons()
        except Exception as e:
            st.error(f"Error de conexión: {e}")
