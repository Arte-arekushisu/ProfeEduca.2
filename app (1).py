import streamlit as st
from fpdf import FPDF
import unicodedata
import io
import datetime
from groq import Groq
from supabase import create_client, Client

# --- CONFIGURACIÓN DE CONEXIONES ---
SUPABASE_URL = "https://pmqmqeukhufaqecbuodg.supabase.co" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBtcW1xZXVraHVmYXFlY2J1b2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE0NzY2MzksImV4cCI6MjA4NzA1MjYzOX0.Hr_3LlyI43zEoV4ZMn28gSKiBABK35VPTWip9rjC-zc"
GROQ_KEY = "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"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    supabase = None

# --- FUNCIONES DE IA ---
def llamar_ia_pedagogica(tipo, campo, alumno, nivel):
    try:
        client = Groq(api_key=GROQ_KEY)
        if tipo == "trayectoria":
            # Prompt enfocado en el estilo de "Escrito Diario Reflexivo"
            prompt = (f"Como educador experto, redacta un texto reflexivo breve (estilo diario pedagógico) "
                      f"sobre el campo formativo {campo} para el alumno {alumno} ({nivel}). "
                      f"Enfócate en el proceso de descubrimiento, retos vencidos y la emoción del aprendizaje. "
                      f"Máximo 4 líneas, sin asteriscos.")
        elif tipo == "resumen":
            prompt = f"Redacta un resumen narrativo de aprendizajes para {alumno}. Incluye metas y estrategias. Sin asteriscos."
        else:
            prompt = f"Redacta compromisos de aprendizaje motivadores para {alumno}. Sin asteriscos."
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6, max_tokens=800
        )
        return completion.choices[0].message.content.replace("*", "")
    except:
        return ""

def clean(txt):
    if not txt: return ""
    txt = "".join(c for c in unicodedata.normalize('NFD', str(txt)) if unicodedata.category(c) != 'Mn')
    txt = txt.replace('ñ', 'n').replace('Ñ', 'N').replace('¿', '').replace('¡', '')
    return txt.encode('latin-1', 'ignore').decode('latin-1')

class ReporteFinalPDF(FPDF):
    def header(self):
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 30, 'F')
        self.set_text_color(56, 189, 248)
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 20, clean('REPORTE DE EVALUACION Y APRENDIZAJES'), 0, 1, 'C')

# --- INTERFAZ STREAMLIT (TOTAL DARK) ---
st.set_page_config(page_title="PROFEEDUCA - Reporte Final", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #020617; color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    .stTextArea textarea, .stTextInput input, .stSelectbox div {
        background-color: #1e293b !important; color: #38bdf8 !important; border: 1px solid #38bdf8 !important;
    }
    label { color: #38bdf8 !important; font-weight: bold; }
    hr { border: 1px solid #38bdf8; }
    </style>
    """, unsafe_allow_html=True)

st.title("📝 Generador de Reporte Formativo Completo")

with st.sidebar:
    st.header("🏢 Encabezado")
    nombre_ec = st.text_input("Educador", "AXEL REYES")
    nombre_ec_acompa = st.text_input("Educador de Acompañamiento")
    comunidad = st.text_input("Comunidad", "PARAJES")
    fecha_doc = st.date_input("Fecha", datetime.date.today())
    st.divider()
    nombre_alumno = st.text_input("Alumno")
    nivel_edu = st.selectbox("Nivel", ["Preescolar", "Primaria", "Secundaria"])
    grado_edu = st.selectbox("Grado/Fase", ["1", "2", "3", "4", "5", "6"])

# --- CONTENIDO PRINCIPAL ---
st.subheader("🤖 Automatización con IA (Basada en Diarios Reflexivos)")
if st.button("✨ GENERAR TODO CON IA"):
    if not nombre_alumno: st.error("Falta nombre del alumno")
    else:
        with st.spinner("Redactando informe basado en reflexiones..."):
            campos = ["Lenguajes", "Saberes y P.C.", "Etica, N. y S.", "De lo Humano y lo Com."]
            for c in campos:
                st.session_state[f"t_{c}"] = llamar_ia_pedagogica("trayectoria", c, nombre_alumno, nivel_edu)
            st.session_state["compromiso_ia"] = llamar_ia_pedagogica("compromiso", "", nombre_alumno, nivel_edu)
            st.session_state["resumen_ia"] = llamar_ia_pedagogica("resumen", "", nombre_alumno, nivel_edu)

# 1. Campos Formativos y Claves Manuales
campos_nombres = ["Lenguajes", "Saberes y P.C.", "Etica, N. y S.", "De lo Humano y lo Com."]
eval_campos = {}
claves_prescolar = {}

for c in campos_nombres:
    st.markdown(f"#### 📍 {c}")
    col_txt, col_clv = st.columns([3, 1])
    
    # El texto reflexivo aparece para TODOS los niveles
    eval_campos[c] = col_txt.text_area(f"Reflexión: {c}", value=st.session_state.get(f"t_{c}", ""), height=100, key=f"area_{c}")
    
    # Las 4 CLAVES MANUALES solo para Preescolar
    if nivel_edu == "Preescolar":
        claves_prescolar[c] = col_clv.text_input(f"Clave {c} (T-xxx)", value="T", key=f"clv_pre_{c}")

st.divider()
nombre_proyecto = st.text_input("🚀 Nombre del Proyecto Comunitario", placeholder="Ej. El Jardín de mi Comunidad")

# 3. Resumen de Aprendizajes y Compromisos
st.subheader("📚 Resumen y Seguimiento")
resumen_txt = st.text_area("📝 Resumen de Aprendizajes", value=st.session_state.get("resumen_ia", ""), height=150)
compromiso_txt = st.text_area("🤝 Compromisos del Alumno", value=st.session_state.get("compromiso_ia", ""), height=100)

# 4. Calificaciones (Primaria/Secundaria)
eval_detalles = []
if nivel_edu != "Preescolar":
    st.subheader("📊 Calificaciones")
    if nivel_edu == "Primaria":
        materias = ["Lenguajes", "Saberes", "Etica", "Humano"]
    else:
        materias = ["Español", "Matemáticas", "Inglés", "Historia", "Geografía", "Artes", "Ed. Física"]
        if grado_edu == "1": materias.insert(2, "Biología")
        elif grado_edu == "2": materias.insert(2, "Física")
        else: materias.insert(2, "Química")
    
    for m in materias:
        c1, c2 = st.columns([3, 1])
        n = c1.number_input(f"{m}", 5, 10, 8, key=f"n_{m}")
        clv = c2.text_input(f"Clave", "T", key=f"cl_{m}")
        eval_detalles.append({"m": m, "n": n, "c": clv})

# --- GENERACIÓN PDF ---
if st.button("🚀 FINALIZAR Y DESCARGAR REPORTE"):
    try:
        pdf = ReporteFinalPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 10)
        
        # Encabezado
        pdf.cell(100, 7, clean(f"EDUCADOR: {nombre_ec}"), 0, 0)
        pdf.cell(90, 7, clean(f"ACOMPAÑANTE: {nombre_ec_acompa}"), 0, 1)
        pdf.cell(100, 7, clean(f"COMUNIDAD: {comunidad}"), 0, 0)
        pdf.cell(90, 7, clean(f"FECHA: {fecha_doc}"), 0, 1)
        pdf.cell(100, 7, clean(f"PROYECTO: {nombre_proyecto}"), 0, 1)
        pdf.ln(5)

        # Trayectorias por Campo
        pdf.set_fill_color(230, 245, 255)
        for campo in campos_nombres:
            # Título del campo con clave si es preescolar
            header_txt = f"{campo}"
            if nivel_edu == "Preescolar":
                header_txt += f" | CLAVE: {claves_prescolar.get(campo, 'T')}"
            
            pdf.set_font("Helvetica", "B", 10); pdf.cell(0, 7, clean(header_txt), 1, 1, 'L', True)
            pdf.set_font("Helvetica", "", 9); pdf.multi_cell(0, 5, clean(eval_campos[campo]), 1)
            pdf.ln(2)

        # Resumen y Compromisos
        pdf.ln(3); pdf.set_font("Helvetica", "B", 10); pdf.cell(0, 7, clean("RESUMEN DE APRENDIZAJES"), 1, 1, 'C', True)
        pdf.set_font("Helvetica", "", 9); pdf.multi_cell(0, 5, clean(resumen_txt), 1)

        pdf.ln(3); pdf.set_font("Helvetica", "B", 10); pdf.cell(0, 7, clean("COMPROMISOS DEL ALUMNO"), 1, 1, 'C', True)
        pdf.set_font("Helvetica", "", 9); pdf.multi_cell(0, 5, clean(compromiso_txt), 1)

        # Calificaciones
        if nivel_edu != "Preescolar":
            pdf.ln(5); pdf.set_font("Helvetica", "B", 10)
            pdf.cell(90, 7, "MATERIA", 1); pdf.cell(45, 7, "NOTA", 1); pdf.cell(45, 7, "CLAVE", 1, 1)
            pdf.set_font("Helvetica", "", 9)
            for item in eval_detalles:
                pdf.cell(90, 6, clean(item['m']), 1); pdf.cell(45, 6, str(item['n']), 1); pdf.cell(45, 6, clean(item['c']), 1, 1)

        # Firmas
        pdf.ln(25)
        pdf.cell(90, 10, "__________________________", 0, 0, 'C')
        pdf.cell(10, 10, "", 0, 0)
        pdf.cell(90, 10, "__________________________", 0, 1, 'C')
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(90, 5, clean(f"FIRMA: {nombre_ec}"), 0, 0, 'C')
        pdf.cell(10, 5, "", 0, 0)
        pdf.cell(90, 5, clean("FIRMA PADRE / MADRE / TUTOR"), 0, 1, 'C')

        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 DESCARGAR REPORTE PDF", pdf_bytes, f"Reporte_{nombre_alumno}.pdf", "application/pdf")
        st.success("¡Reporte listo y perrón!")

    except Exception as e:
        st.error(f"Error: {e}")
