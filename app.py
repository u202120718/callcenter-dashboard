"""
Dashboard Call Center Pro - Versión Definitiva
Con: Botones visibles, frases rotativas cada 5s (CORREGIDO), interfaz mejorada, CHAT con notificaciones y sonido
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import unicodedata
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import re
from functools import lru_cache
import io
import random
import time
import json
import os
import base64

# ============================================================================
# CONFIGURACIÓN INICIAL
# ============================================================================

st.set_page_config(
    page_title="Analis de la Gestion",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Archivo para guardar mensajes
MENSAJES_FILE = "mensajes.json"

# Configuración de campañas
CAMPANAS = {
    "Energía": {
        "icon": "⚡",
        "color": "#f97316",
        "gradient": "linear-gradient(135deg, #f97316, #ea580c)",
        "csv_path": "REPORTE_ENERGIA.csv",
        "description": "Campaña de Energía - Ventas de servicios eléctricos",
        "bg_color": "rgba(249,115,22,0.1)"
    },
    "Telefonía": {
        "icon": "📱",
        "color": "#3b82f6",
        "gradient": "linear-gradient(135deg, #3b82f6, #2563eb)",
        "csv_path": "REPORTE_TELEFONIA.csv",
        "description": "Campaña de Telefonía - Planes móviles y fibra óptica",
        "bg_color": "rgba(59,130,246,0.1)"
    }
}

# Configuración de roles con contraseñas seguras
ROLES_CONFIG = {
    "admin": {
        "name": "Administrador",
        "password": "CallCenter2026!Admin#Secure",
        "can_upload": True,
        "can_configure": True,
        "can_delete": True,
        "can_see_all": True
    },
    "supervisor": {
        "name": "Supervisor",
        "password": "Supervisor@Call2026#Pro",
        "can_upload": False,
        "can_configure": False,
        "can_delete": False,
        "can_see_all": True
    }
}

# Opciones de actualización
REFRESH_OPTIONS = {
    "Cada 30 minutos": 1800,
    "Cada 1 hora": 3600,
    "Cada 2 horas": 7200,
    "Cada 4 horas": 14400,
    "Manual (solo Admin)": 0
}

# Frases motivacionales (rotan cada 5 segundos)
FRASES = [
    "🌟 El éxito es la suma de pequeños esfuerzos repetidos día tras día.",
    "📞 Cada llamada es una oportunidad para crear un cliente feliz.",
    "🎯 La calidad no es un acto, es un hábito.",
    "💪 Los grandes equipos están hechos de personas que nunca se rinden.",
    "⭐ La excelencia no es un destino, es un viaje continuo.",
    "🔊 Escucha más de lo que hablas y ganarás más de lo que imaginas.",
    "🚀 El cielo no es el límite cuando hay huellas en la luna.",
    "🏆 El profesionalismo se demuestra en cada llamada.",
    "💎 La perseverancia vence lo que la alegría no puede.",
    "🎧 Un cliente satisfecho es la mejor publicidad."
]

# Sonido de notificación (base64)
NOTIFICATION_SOUND = """
<audio id="notificationSound" preload="auto">
    <source src="data:audio/wav;base64,U3RlYW0gU291bmQ=" type="audio/wav">
</audio>
<script>
function playNotification() {
    const audio = document.getElementById('notificationSound');
    if(audio) {
        audio.play().catch(e => console.log('Audio play failed:', e));
    }
}
</script>
"""

# JavaScript para rotar frases cada 5 segundos (CORREGIDO)
ROTATE_FRASES_JS = """
<script>
function rotatePhrase() {
    const frases = [
        "🌟 El éxito es la suma de pequeños esfuerzos repetidos día tras día.",
        "📞 Cada llamada es una oportunidad para crear un cliente feliz.",
        "🎯 La calidad no es un acto, es un hábito.",
        "💪 Los grandes equipos están hechos de personas que nunca se rinden.",
        "⭐ La excelencia no es un destino, es un viaje continuo.",
        "🔊 Escucha más de lo que hablas y ganarás más de lo que imaginas.",
        "🚀 El cielo no es el límite cuando hay huellas en la luna.",
        "🏆 El profesionalismo se demuestra en cada llamada.",
        "💎 La perseverancia vence lo que la alegría no puede.",
        "🎧 Un cliente satisfecho es la mejor publicidad."
    ];
    let index = 0;
    const phraseElement = document.getElementById('rotating-phrase');
    if (phraseElement) {
        setInterval(() => {
            index = (index + 1) % frases.length;
            phraseElement.style.transition = 'opacity 0.5s ease';
            phraseElement.style.opacity = '0';
            setTimeout(() => {
                phraseElement.textContent = frases[index];
                phraseElement.style.opacity = '1';
            }, 500);
        }, 5000);
    }
}
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', rotatePhrase);
} else {
    rotatePhrase();
}
</script>
"""

# CSS Mejorado
CUSTOM_CSS = """
<style>
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.8; transform: scale(1.02); }
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes starAnimation {
    0% { opacity: 0; transform: translateY(0px) rotate(0deg); }
    50% { opacity: 1; transform: translateY(-20px) rotate(180deg); }
    100% { opacity: 0; transform: translateY(-40px) rotate(360deg); }
}

@keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

@keyframes notificationBadge {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.3); background-color: #ef4444; }
}

.star {
    position: fixed;
    color: #FFD700;
    font-size: 1.2rem;
    pointer-events: none;
    animation: starAnimation 3s ease-in-out infinite;
    z-index: 9999;
}

.login-container {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 30px;
    padding: 40px;
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
    border: 1px solid rgba(255,255,255,0.2);
    position: relative;
    overflow: hidden;
}

.login-container::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 1%, transparent 1%);
    background-size: 50px 50px;
    animation: shimmer 20s linear infinite;
}

.login-title {
    text-align: center;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #FFD700, #FFA500, #FF6347, #FFD700);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientShift 3s ease infinite;
    margin-bottom: 20px;
}

.login-subtitle {
    text-align: center;
    color: #cbd5e1;
    margin-bottom: 30px;
    font-style: italic;
}

.rotating-phrase {
    text-align: center;
    background: rgba(255,255,255,0.1);
    padding: 12px 20px;
    border-radius: 40px;
    font-size: 0.95rem;
    color: #FFD700;
    transition: opacity 0.5s ease;
    margin: 20px 0;
}

.metric-card {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    border-radius: 20px;
    padding: 20px;
    color: white;
    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid rgba(255,255,255,0.1);
    position: relative;
    overflow: hidden;
}

.metric-card::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    transition: left 0.5s;
}

.metric-card:hover::after {
    left: 100%;
}

.metric-card:hover {
    transform: translateY(-5px) scale(1.02);
}

.metric-title {
    font-size: 0.85rem;
    color: #94a3b8;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    font-weight: 600;
}

.metric-value {
    font-size: 2rem;
    font-weight: 800;
    margin-top: 8px;
    background: linear-gradient(135deg, #fff, #94a3b8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.metric-sub {
    font-size: 0.7rem;
    color: #64748b;
    margin-top: 5px;
}

.green-card { background: linear-gradient(135deg, #064e3b, #059669); }
.red-card { background: linear-gradient(135deg, #7f1d1d, #dc2626); }
.orange-card { background: linear-gradient(135deg, #7c2d12, #ea580c); }
.blue-card { background: linear-gradient(135deg, #1e3a8a, #3b82f6); }
.yellow-card { background: linear-gradient(135deg, #854d0e, #eab308); }
.purple-card { background: linear-gradient(135deg, #4c1d95, #8b5cf6); }

.result-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border-radius: 16px;
    padding: 20px;
    margin: 15px 0;
    border-left: 4px solid #22c55e;
    animation: fadeIn 0.5s ease-out;
}

.result-card-critical {
    border-left-color: #ef4444;
}

.result-card-warning {
    border-left-color: #eab308;
}

.update-panel {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    padding: 20px 25px;
    border-radius: 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.1);
}

.role-badge-admin {
    background: linear-gradient(135deg, #dc2626, #991b1b);
    padding: 6px 16px;
    border-radius: 30px;
    font-size: 0.8rem;
    font-weight: 700;
    display: inline-block;
    animation: pulse 2s infinite;
}

.role-badge-supervisor {
    background: linear-gradient(135deg, #3b82f6, #1e40af);
    padding: 6px 16px;
    border-radius: 30px;
    font-size: 0.8rem;
    font-weight: 700;
    display: inline-block;
    animation: pulse 2s infinite;
}

/* Estilos mejorados para el chat */
.chat-container {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.1);
}

.message-bubble {
    background: #0f172a;
    border-radius: 15px;
    padding: 12px 16px;
    margin-bottom: 12px;
    border-left: 3px solid;
}

.message-admin {
    border-left-color: #dc2626;
    background: linear-gradient(135deg, #1e293b, #2d1a1a);
}

.message-supervisor {
    border-left-color: #3b82f6;
}

.message-time {
    font-size: 0.65rem;
    color: #64748b;
    margin-bottom: 5px;
}

.message-sender {
    font-weight: 700;
    font-size: 0.8rem;
    margin-bottom: 5px;
}

.message-text {
    font-size: 0.9rem;
    color: #e2e8f0;
}

/* Notificación mejorada estilo WhatsApp */
.notification-whatsapp {
    background: linear-gradient(135deg, #dc2626, #ef4444);
    color: white;
    border-radius: 30px;
    padding: 8px 18px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    animation: notificationBadge 0.5s ease;
    box-shadow: 0 4px 12px rgba(220,38,38,0.4);
    margin-left: 10px;
}

.notification-whatsapp::before {
    content: "💬";
    font-size: 1rem;
}

.chat-input-area {
    background: #0f172a;
    border-radius: 12px;
    padding: 15px;
    margin-top: 15px;
}

.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    font-weight: 600;
    border-radius: 12px;
    padding: 10px 20px;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px -5px rgba(102, 126, 234, 0.4);
}

.dashboard-footer {
    margin-top: 30px;
    padding: 20px;
    text-align: center;
    border-top: 1px solid #334155;
    font-size: 0.8rem;
    color: #64748b;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: linear-gradient(135deg, #1e293b, #0f172a);
    padding: 8px;
    border-radius: 16px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    padding: 8px 20px;
    font-weight: 600;
    transition: all 0.3s;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: #334155;
}
</style>
"""

# ============================================================================
# FUNCIONES DE MENSAJERÍA
# ============================================================================

def cargar_mensajes():
    """Carga los mensajes guardados del archivo JSON"""
    if os.path.exists(MENSAJES_FILE):
        try:
            with open(MENSAJES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_mensaje(mensaje):
    """Guarda un nuevo mensaje"""
    mensajes = cargar_mensajes()
    mensajes.append(mensaje)
    with open(MENSAJES_FILE, 'w', encoding='utf-8') as f:
        json.dump(mensajes, f, ensure_ascii=False, indent=2)

def enviar_mensaje(remitente, texto, rol):
    """Envía un mensaje nuevo con hora Perú (UTC-5)"""
    # Crear zona horaria de Perú (UTC-5)
    from datetime import timezone, timedelta
    
    # Definir zona horaria Perú (UTC-5)
    zona_peru = timezone(timedelta(hours=-5))
    
    # Obtener hora actual con zona Perú
    hora_peru = datetime.now(zona_peru)
    
    mensaje = {
        'id': len(cargar_mensajes()) + 1,
        'remitente': remitente,
        'texto': texto,
        'rol': rol,
        'timestamp': (datetime.now() - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S'),
        'leido': False
    }
    guardar_mensaje(mensaje)

def marcar_como_leidos(rol_usuario):
    """Marca todos los mensajes para el usuario actual como leídos"""
    mensajes = cargar_mensajes()
    for msg in mensajes:
        if msg['rol'] != rol_usuario:
            msg['leido'] = True
    with open(MENSAJES_FILE, 'w', encoding='utf-8') as f:
        json.dump(mensajes, f, ensure_ascii=False, indent=2)

def contar_no_leidos(rol_usuario):
    """Cuenta mensajes no leídos para el usuario actual"""
    mensajes = cargar_mensajes()
    no_leidos = 0
    for msg in mensajes:
        if msg['rol'] != rol_usuario and not msg.get('leido', False):
            no_leidos += 1
    return no_leidos

def obtener_texto_notificacion(rol_usuario):
    """Obtiene el texto de notificación estilo WhatsApp"""
    no_leidos = contar_no_leidos(rol_usuario)
    if no_leidos == 0:
        return None
    elif no_leidos == 1:
        return "Tienes 1 mensaje nuevo"
    else:
        return f"Tienes {no_leidos} mensajes nuevos"

def mostrar_chat(rol_usuario, nombre_usuario):
    """Muestra el chat completo"""
    
    st.markdown("""
    <div class="chat-container">
        <h3>💬 Centro de Mensajes</h3>
        <p style="color: #94a3b8; font-size: 0.8rem;">Comunícate directamente con el administrador</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar mensajes existentes
    mensajes = cargar_mensajes()
    
    if mensajes:
        for msg in reversed(mensajes[-15:]):
            clase = "message-admin" if msg['rol'] == 'admin' else "message-supervisor"
            icono = "👑" if msg['rol'] == 'admin' else "👁️"
            st.markdown(f"""
            <div class="message-bubble {clase}">
                <div class="message-time">🕐 {msg['timestamp']}</div>
                <div class="message-sender">{icono} <strong>{msg['remitente']}</strong> ({'Administrador' if msg['rol'] == 'admin' else 'Supervisor'})</div>
                <div class="message-text">{msg['texto']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("💬 No hay mensajes aún. ¡Envía el primero!")
    
    st.markdown("---")
    
    # Botones de acción rápida para supervisor
    if rol_usuario == 'supervisor':
        st.markdown("#### ⚡ Acciones rápidas")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📢 Solicitar actualización", use_container_width=True):
                enviar_mensaje(nombre_usuario, "📢 Solicito actualización del reporte, por favor.", rol_usuario)
                st.success("✅ Solicitud enviada")
                time.sleep(0.5)
                st.rerun()
        with col2:
            if st.button("⚠️ Reportar problema", use_container_width=True):
                enviar_mensaje(nombre_usuario, "⚠️ Reporto un problema con el dashboard, por favor revisar.", rol_usuario)
                st.success("✅ Reporte enviado")
                time.sleep(0.5)
                st.rerun()
        st.markdown("---")
    
    # Área para escribir mensaje
    st.markdown("#### ✏️ Escribir mensaje")
    
    if rol_usuario == 'admin':
        placeholder = "Escribe tu respuesta como administrador..."
    else:
        placeholder = "Escribe tu mensaje para el administrador..."
    
    mensaje_texto = st.text_area("Mensaje:", placeholder=placeholder, height=80)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📨 Enviar mensaje", use_container_width=True):
            if mensaje_texto.strip():
                enviar_mensaje(nombre_usuario, mensaje_texto, rol_usuario)
                st.success("✅ Mensaje enviado")
                time.sleep(0.5)
                st.rerun()
            else:
                st.warning("⚠️ Escribe un mensaje primero")
    
    # Botones de respuesta rápida para admin
    if rol_usuario == 'admin':
        st.markdown("---")
        st.markdown("#### ⚡ Respuestas rápidas")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("✅ Reporte actualizado", use_container_width=True):
                enviar_mensaje(nombre_usuario, "✅ El reporte ya está actualizado con los últimos datos.", 'admin')
                st.success("✅ Respuesta enviada")
                time.sleep(0.5)
                st.rerun()
        with col2:
            if st.button("🔄 Actualizando...", use_container_width=True):
                enviar_mensaje(nombre_usuario, "🔄 Estamos actualizando el reporte, estará listo en breve.", 'admin')
                st.success("✅ Respuesta enviada")
                time.sleep(0.5)
                st.rerun()
        with col3:
            if st.button("📊 Nuevos datos", use_container_width=True):
                enviar_mensaje(nombre_usuario, "📊 Se han cargado nuevos datos al sistema.", 'admin')
                st.success("✅ Respuesta enviada")
                time.sleep(0.5)
                st.rerun()
        with col4:
            if st.button("🔧 Revisando", use_container_width=True):
                enviar_mensaje(nombre_usuario, "🔧 Estamos revisando el problema reportado.", 'admin')
                st.success("✅ Respuesta enviada")
                time.sleep(0.5)
                st.rerun()
    
    # Botón para marcar como leídos
    if st.button("✅ Marcar todos como leídos", use_container_width=True):
        marcar_como_leidos(rol_usuario)
        st.success("Mensajes marcados como leídos")
        time.sleep(0.5)
        st.rerun()

# ============================================================================
# FUNCIONES DE ANIMACIÓN
# ============================================================================

def generar_estrellas():
    estrellas = ""
    for i in range(40):
        left = random.randint(0, 100)
        top = random.randint(0, 100)
        delay = random.randint(0, 5)
        duration = random.randint(2, 4)
        size = random.choice([0.8, 1.0, 1.2, 1.5])
        estrellas += f'<div class="star" style="left: {left}%; top: {top}%; animation-delay: {delay}s; animation-duration: {duration}s; font-size: {size}rem;">⭐</div>'
    return estrellas

# ============================================================================
# UTILIDADES
# ============================================================================

@lru_cache(maxsize=1000)
def normalizar_texto(texto: str) -> str:
    try:
        texto = str(texto).upper().strip()
        texto = unicodedata.normalize("NFKD", texto)
        texto = "".join(c for c in texto if not unicodedata.combining(c))
        texto = re.sub(r'[^\w\s]', ' ', texto)
        return texto
    except Exception:
        return ""


def format_seconds(seconds: int) -> str:
    seconds = max(0, int(seconds or 0))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def metric_card(title: str, value: str, css_class: str = "", subtext: str = ""):
    st.markdown(
        f"""
        <div class="metric-card {css_class}">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            {f'<div class="metric-sub">{subtext}</div>' if subtext else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_divide(a: float, b: float, default: float = 0) -> float:
    return a / b if b != 0 else default


def get_freshness_status(last_update: datetime) -> tuple:
    if last_update is None:
        return "Sin datos", "red", "No hay datos cargados"
    
    minutes_ago = (datetime.now() - last_update).total_seconds() / 60
    
    if minutes_ago < 30:
        return "🟢 DATOS RECIENTES", "green", f"Actualizado hace {int(minutes_ago)} minutos"
    elif minutes_ago < 60:
        return "🟡 DATOS MODERADOS", "yellow", f"Actualizado hace {int(minutes_ago)} minutos"
    else:
        return "🔴 DATOS ANTIGUOS", "red", f"¡Actualizar! Hace {int(minutes_ago)} minutos"


# ============================================================================
# CARGA Y LIMPIEZA DE DATOS
# ============================================================================

@st.cache_data(show_spinner="Cargando datos...")
def load_csv(file_path: Path):
    if not file_path.exists():
        return None
    
    encodings = ['utf-8', 'latin1', 'iso-8859-1']
    separators = [';', ',']
    
    for encoding in encodings:
        for sep in separators:
            try:
                df = pd.read_csv(file_path, sep=sep, encoding=encoding, low_memory=False)
                return df
            except Exception:
                continue
    return None


def clean_data(df: pd.DataFrame, campaign_name: str) -> pd.DataFrame:
    df = df.copy()
    df["campaña"] = campaign_name
    
    required_cols = ["user", "full_name", "status", "status_name", "length_in_sec", "call_date", "phone_number_dialed"]
    
    for col in required_cols:
        if col not in df.columns:
            df[col] = None
    
    df["user"] = df["user"].fillna("SIN_USUARIO").astype(str).str.strip()
    df["full_name"] = df["full_name"].fillna(df["user"]).astype(str).str.strip()
    df["status"] = df["status"].fillna("SIN_STATUS").astype(str).str.strip()
    df["status_name"] = df["status_name"].fillna("SIN_STATUS_NAME").astype(str).str.strip()
    
    df["length_in_sec"] = pd.to_numeric(df["length_in_sec"], errors="coerce").fillna(0).astype(int)
    df["minutos_hablados"] = (df["length_in_sec"] / 60).round(2)
    
    df["call_date"] = pd.to_datetime(df["call_date"], errors="coerce", dayfirst=True)
    df["fecha"] = df["call_date"].dt.date
    
    df["status_normalizado"] = df["status"].apply(normalizar_texto)
    df["status_name_normalizado"] = df["status_name"].apply(normalizar_texto)
    
    texto_status = df["status_normalizado"] + " " + df["status_name_normalizado"]
    
    df["es_auto_dial"] = df["user"].str.upper().isin(["VDAD", "VDCL"])
    
    df["es_contestador"] = texto_status.str.contains(
        "CONTESTADOR|CONTESTADORA|CONTESTADOR AUTOMATICO|ANSWERING MACHINE|MACHINE|BUZON|VOICEMAIL",
        regex=True, na=False
    )
    
    df["es_no_interesado"] = texto_status.str.contains(
        "NO INTERESADO|NO LE INTERESA|NO INTERESA|NO QUIERE|NO ACEPTA",
        regex=True, na=False
    )
    
    df["contacto_humano_estimado"] = ~texto_status.str.contains(
        "NO ANSWER|BUSY|ANSWERING MACHINE|CONTESTADOR|DISCONNECTED|DROP",
        regex=True, na=False
    )
    
    return df


def add_analysis_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    df["contestador_menor_igual_10s"] = df["es_contestador"] & (df["length_in_sec"] <= 10)
    df["contestador_mayor_10s"] = df["es_contestador"] & (df["length_in_sec"] > 10)
    df["no_interesado_2_5min"] = df["es_no_interesado"] & (df["length_in_sec"] >= 120) & (df["length_in_sec"] < 300)
    df["no_interesado_mas_5min"] = df["es_no_interesado"] & (df["length_in_sec"] >= 300)
    df["no_interesado_mas_10min"] = df["es_no_interesado"] & (df["length_in_sec"] >= 600)
    
    def clasificar_problema(row):
        if row.get("es_contestador", False):
            return "Correcto" if row.get("length_in_sec", 0) <= 10 else "Problema grave"
        if row.get("es_no_interesado", False):
            seg = row.get("length_in_sec", 0)
            if seg >= 600: return "Problema grave +10min"
            if seg >= 300: return "Problema grave"
            if seg >= 120: return "Alerta media"
        return "Normal"
    
    def generar_comentario(row):
        if row.get("es_contestador", False):
            seg = row.get("length_in_sec", 0)
            if seg <= 10:
                return "✅ Correcto: cortó rápido al detectar contestador"
            return "⚠️ Problema: contestador >10 segundos - Debe cortar antes"
        if row.get("es_no_interesado", False):
            seg = row.get("length_in_sec", 0)
            if seg >= 600: return "🔴 CRÍTICO: No interesado con MÁS DE 10 MINUTOS - Revisión URGENTE"
            if seg >= 300: return "🔴 Grave: no interesado >5 minutos - Requiere coaching"
            if seg >= 120: return "🟡 Alerta: no interesado >2 minutos - Mejorar argumentación"
        return "ℹ️ Normal"
    
    df["nivel_problema"] = df.apply(clasificar_problema, axis=1)
    df["comentario_mejora"] = df.apply(generar_comentario, axis=1)
    
    return df


def calculate_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    total_llamadas = len(df)
    total_agentes = df["user"].nunique()
    tiempo_total = df["length_in_sec"].sum()
    promedio_llamada = df["length_in_sec"].mean()
    contactabilidad = safe_divide(df["contacto_humano_estimado"].sum(), total_llamadas, 0) * 100
    
    return {
        "total_llamadas": total_llamadas,
        "total_agentes": total_agentes,
        "tiempo_total_seg": tiempo_total,
        "tiempo_total_formatted": format_seconds(tiempo_total),
        "promedio_llamada_seg": round(promedio_llamada, 1),
        "contactabilidad": round(contactabilidad, 1),
        "contestador_menor": int(df["contestador_menor_igual_10s"].sum()),
        "contestador_mayor": int(df["contestador_mayor_10s"].sum()),
        "no_interesado_2_5min": int(df["no_interesado_2_5min"].sum()),
        "no_interesado_mas_5min": int(df["no_interesado_mas_5min"].sum()),
        "no_interesado_mas_10min": int(df["no_interesado_mas_10min"].sum()),
    }


def get_agente_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["user", "full_name", "campaña"])
        .agg(
            llamadas=("user", "size"),
            tiempo_total_seg=("length_in_sec", "sum"),
            tiempo_promedio_seg=("length_in_sec", "mean"),
            contestador_menor=("contestador_menor_igual_10s", "sum"),
            contestador_mayor=("contestador_mayor_10s", "sum"),
            no_interesado_2_5min=("no_interesado_2_5min", "sum"),
            no_interesado_mas_5min=("no_interesado_mas_5min", "sum"),
            no_interesado_mas_10min=("no_interesado_mas_10min", "sum"),
            contactabilidad_raw=("contacto_humano_estimado", "mean")
        )
        .reset_index()
    )
    
    summary["tiempo_total"] = summary["tiempo_total_seg"].apply(format_seconds)
    summary["tiempo_promedio_seg"] = summary["tiempo_promedio_seg"].round(1)
    summary["contactabilidad"] = (summary["contactabilidad_raw"] * 100).round(1)
    summary = summary.drop(columns=["contactabilidad_raw"])
    
    return summary.sort_values("tiempo_total_seg", ascending=False)


def mostrar_resultados_filtro(df_filtrado, titulo, color, tipo_filtro):
    """Muestra los resultados del filtro"""
    if len(df_filtrado) > 0:
        st.markdown(f"""
        <div class="result-card result-card-{color}">
            <h4>{titulo}</h4>
            <p><strong>📊 Total encontrados:</strong> {len(df_filtrado)} llamadas</p>
            <p><strong>⏱️ Tiempo total:</strong> {format_seconds(df_filtrado['length_in_sec'].sum())}</p>
            <p><strong>👥 Agentes involucrados:</strong> {df_filtrado['user'].nunique()}</p>
            <p><strong>📈 Promedio por llamada:</strong> {(df_filtrado['length_in_sec'].mean() / 60):.1f} minutos</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander(f"📋 Ver detalles de las {len(df_filtrado)} llamadas", expanded=True):
            columnas_mostrar = ["user", "full_name", "phone_number_dialed", "status_name", "length_in_sec", "minutos_hablados", "comentario_mejora"]
            columnas_disponibles = [col for col in columnas_mostrar if col in df_filtrado.columns]
            
            st.dataframe(
                df_filtrado[columnas_disponibles],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "user": "Agente",
                    "full_name": "Nombre",
                    "phone_number_dialed": "📞 Teléfono",
                    "status_name": "Status",
                    "length_in_sec": "Duración (seg)",
                    "minutos_hablados": "Minutos",
                    "comentario_mejora": "Comentario"
                }
            )
        
        st.subheader("📋 Resumen por Agente")
        resumen_filtro = df_filtrado.groupby("user").agg(
            cantidad=("user", "size"),
            tiempo_total=("length_in_sec", "sum")
        ).reset_index().sort_values("cantidad", ascending=False)
        resumen_filtro["tiempo_formateado"] = resumen_filtro["tiempo_total"].apply(format_seconds)
        st.dataframe(resumen_filtro, use_container_width=True, hide_index=True)
        
        if tipo_filtro == "2_5":
            st.info("💡 **Recomendación:** Revisar argumentación comercial para reducir el tiempo en llamadas de no interesados (2-5 minutos).")
        elif tipo_filtro == "mas_5":
            st.warning("⚠️ **Recomendación:** Coaching urgente para mejorar cierre de llamadas sin oportunidad real (>5 minutos).")
        elif tipo_filtro == "mas_10":
            st.error("🚨 **REVISIÓN URGENTE:** Estos casos (>10 minutos) requieren atención inmediata de supervisión.")
    else:
        st.info(f"ℹ️ No se encontraron llamadas en esta categoría")


# ============================================================================
# LOGIN MEJORADO
# ============================================================================

def login_screen():
    # Inyectar JavaScript para frases rotativas
    st.markdown(ROTATE_FRASES_JS, unsafe_allow_html=True)
    st.markdown(NOTIFICATION_SOUND, unsafe_allow_html=True)
    
    estrellas_html = generar_estrellas()
    st.markdown(estrellas_html, unsafe_allow_html=True)
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div class="login-container">
            <div class="login-title">
                🎯 Analytics pro
            </div>
            <div class="login-subtitle">
                "Evalúa el rendimiento de tu equipo comercial"
            </div>
            <div class="rotating-phrase" id="rotating-phrase">
                {FRASES[0]}
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("#### 🔐 Acceso al Sistema")
        
        role = st.radio(
            "Selecciona tu rol:",
            ["supervisor", "admin"],
            format_func=lambda x: "👑 Administrador" if x == "admin" else "👁️ Supervisor",
            horizontal=True
        )
        
        password = st.text_input("Contraseña:", type="password")
        
        if st.button("✨ Ingresar al Sistema ✨", use_container_width=True):
            expected_password = ROLES_CONFIG[role]["password"]
            if password == expected_password:
                st.session_state["authenticated"] = True
                st.session_state["role"] = role
                st.session_state["user"] = ROLES_CONFIG[role]["name"]
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
        
        st.markdown("---")
        st.caption("🔒 Sistema seguro - Usar con responsabilidad, va estar monitoriado")
        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================================
# DASHBOARD PRINCIPAL
# ============================================================================

def main_dashboard():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(NOTIFICATION_SOUND, unsafe_allow_html=True)
    
    role = st.session_state["role"]
    is_admin = (role == "admin")
    nombre_usuario = st.session_state["user"]
    
    # Header mejorado con notificación estilo WhatsApp
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        st.title("🎯 Analytics Pro")
        st.caption(f"📊 Evaluando el rendimiento de tu equipo comercial | Bienvenido, {st.session_state['user']}")
    
    with col2:
        if is_admin:
            st.markdown('<div class="role-badge-admin">👑 ADMINISTRADOR</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="role-badge-supervisor">👁️ SUPERVISOR</div>', unsafe_allow_html=True)
    
    with col3:
        # Notificación estilo WhatsApp
        texto_notif = obtener_texto_notificacion(role)
        if texto_notif:
            st.markdown(f'<span class="notification-whatsapp">{texto_notif}</span>', unsafe_allow_html=True)
            # Reproducir sonido usando JavaScript
            st.markdown('<script>playNotification();</script>', unsafe_allow_html=True)
        
        if st.button("💬 Chat", use_container_width=True):
            st.session_state["show_chat"] = not st.session_state.get("show_chat", False)
            if contar_no_leidos(role) > 0:
                marcar_como_leidos(role)
            st.rerun()
    
    with col4:
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            for key in ["authenticated", "role", "user", "selected_campaign", "selected_filter", "show_chat"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    st.divider()
    
    # Mostrar chat si está activo
    if st.session_state.get("show_chat", False):
        mostrar_chat(role, nombre_usuario)
        st.divider()
    
    # ========================================================================
    # SELECCIÓN DE CAMPAÑA
    # ========================================================================
    
    st.markdown("### 📊 Seleccionar Campaña")
    st.markdown("Elige la campaña que deseas analizar: Señores(as) Coordinadores seleccionar la campaña que pertenece, el sistema va estar monitoriado.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(249,115,22,0.1), rgba(249,115,22,0.05)); border-radius: 20px; padding: 5px;">
        """, unsafe_allow_html=True)
        if st.button("⚡ ENERGÍA", use_container_width=True, key="btn_energia"):
            st.session_state["selected_campaign"] = "Energía"
            if "selected_filter" in st.session_state:
                del st.session_state["selected_filter"]
            st.rerun()
        st.markdown("""
        <div style="text-align: center; padding: 8px;">
            <small style="color: #f97316;">📊 Análisis de llamadas - Campaña Energia</small>
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(59,130,246,0.05)); border-radius: 20px; padding: 5px;">
        """, unsafe_allow_html=True)
        if st.button("📱 TELEFONÍA", use_container_width=True, key="btn_telefonia"):
            st.session_state["selected_campaign"] = "Telefonía"
            if "selected_filter" in st.session_state:
                del st.session_state["selected_filter"]
            st.rerun()
        st.markdown("""
        <div style="text-align: center; padding: 8px;">
            <small style="color: #3b82f6;">📊 Análisis de llamadas - Campaña Móvil o Telefonica</small>
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    if "selected_campaign" not in st.session_state:
        st.session_state["selected_campaign"] = "Energía"
    
    campaign = st.session_state["selected_campaign"]
    campaign_config = CAMPANAS[campaign]
    
    st.success(f"{campaign_config['icon']} **Campaña activa: {campaign}** - {campaign_config['description']}")
    st.divider()
    
    # Panel de Admin
    if is_admin:
        st.markdown("### 🎛️ Panel de Control")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            frecuencia = st.selectbox(
                "⏰ Frecuencia de actualización",
                options=list(REFRESH_OPTIONS.keys()),
                index=1,
                key="frecuencia_select"
            )
            st.session_state["auto_refresh_interval"] = REFRESH_OPTIONS[frecuencia]
        
        with col2:
            if st.button("🔄 ACTUALIZAR AHORA", use_container_width=True):
                st.cache_data.clear()
                st.session_state["last_update"] = datetime.now()
                enviar_mensaje(nombre_usuario, "✅ Se ha actualizado el reporte con nuevos datos.", 'admin')
                st.rerun()
        
        with col3:
            if st.session_state.get("auto_refresh_interval", 0) > 0:
                st.success(f"🤖 Auto-refresh: {frecuencia}")
            else:
                st.info("🔒 Modo manual")
        
        st.markdown("#### 📁 Carga de Datos")
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_energia = st.file_uploader("REPORTE_ENERGIA.csv", type=["csv"], key="upload_energia")
            if uploaded_energia:
                with open("REPORTE_ENERGIA.csv", "wb") as f:
                    f.write(uploaded_energia.getbuffer())
                st.success("✅ Energía actualizado")
                enviar_mensaje(nombre_usuario, "📊 Se ha actualizado el reporte de ENERGÍA.", 'admin')
                st.cache_data.clear()
        
        with col2:
            uploaded_telefonia = st.file_uploader("REPORTE_TELEFONIA.csv", type=["csv"], key="upload_telefonia")
            if uploaded_telefonia:
                with open("REPORTE_TELEFONIA.csv", "wb") as f:
                    f.write(uploaded_telefonia.getbuffer())
                st.success("✅ Telefonía actualizado")
                enviar_mensaje(nombre_usuario, "📊 Se ha actualizado el reporte de TELEFONÍA.", 'admin')
                st.cache_data.clear()
        
        st.divider()
    
    # Cargar datos
    csv_path = Path(campaign_config["csv_path"])
    
    if not csv_path.exists():
        if is_admin:
            st.warning(f"⚠️ No se encuentra {campaign_config['csv_path']}")
            st.info("💡 Como administrador, puedes subir el archivo CSV usando el panel de carga de datos arriba.")
        else:
            st.warning(f"⚠️ Datos de {campaign} no disponibles. Contacta al administrador.")
            if st.button("💬 Solicitar actualización al administrador"):
                enviar_mensaje(nombre_usuario, f"📢 Solicito actualización del reporte de {campaign}, por favor.", role)
                st.success("✅ Solicitud enviada")
                st.session_state["show_chat"] = True
                st.rerun()
        return
    
    with st.spinner(f"Cargando datos de {campaign}..."):
        df_raw = load_csv(csv_path)
        if df_raw is None:
            st.error("Error al cargar datos")
            return
        
        df = clean_data(df_raw, campaign)
        df = add_analysis_columns(df)
        
        if "last_update" not in st.session_state:
            st.session_state["last_update"] = datetime.now()
    
    # Estado de actualización
    if st.session_state.get("last_update"):
        freshness_status, freshness_color, freshness_detail = get_freshness_status(st.session_state["last_update"])
        st.markdown(f"""
        <div class="update-panel">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <span class="fresh-indicator fresh-{freshness_color}"></span>
                    <strong>{freshness_status}</strong>
                </div>
                <div>📅 Última actualización: {st.session_state['last_update'].strftime('%Y-%m-%d %H:%M:%S')}</div>
                <div>{freshness_detail}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Filtros en sidebar
    with st.sidebar:
        st.header("🔍 Filtros Avanzados")
        
        excluir_auto = st.checkbox("Excluir VDAD / VDCL", value=True)
        if excluir_auto:
            df = df[~df["es_auto_dial"]]
        
        if df["fecha"].notna().any():
            min_date = df["fecha"].min()
            max_date = df["fecha"].max()
            rango = st.date_input("📅 Rango de fechas", value=(min_date, max_date),
                                  min_value=min_date, max_value=max_date)
            if isinstance(rango, tuple) and len(rango) == 2:
                df = df[(df["fecha"] >= rango[0]) & (df["fecha"] <= rango[1])]
        
        agentes = sorted(df["user"].dropna().unique().tolist())
        agentes_filter = st.multiselect("👤 Agentes", agentes, default=agentes[:10] if len(agentes) > 10 else agentes)
        if agentes_filter:
            df = df[df["user"].isin(agentes_filter)]
        
        statuses = sorted(df["status_name"].dropna().unique().tolist())
        status_filter = st.multiselect("📌 Status", statuses, default=[])
        if status_filter:
            df = df[df["status_name"].isin(status_filter)]
    
    if df.empty:
        st.warning("No hay datos con los filtros seleccionados")
        return
    
    # Métricas
    metrics = calculate_metrics(df)
    resumen_agente = get_agente_summary(df)
    
    # Fila 1 - Métricas generales
    st.subheader("📈 Métricas Generales")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        metric_card("📞 Total llamadas", f"{metrics['total_llamadas']:,}".replace(",", "."))
    with col2:
        metric_card("👥 Agentes", metrics['total_agentes'])
    with col3:
        metric_card("⏱️ Tiempo hablado", metrics['tiempo_total_formatted'])
    with col4:
        metric_card("⚡ Promedio llamada", f"{metrics['promedio_llamada_seg']} seg")
    with col5:
        metric_card("🎯 Contactabilidad", f"{metrics['contactabilidad']}%")
    
    st.divider()
    
    # Fila 2 - Contestador Automático
    st.subheader("📞 Análisis de Contestador Automático")
    col1, col2 = st.columns(2)
    
    with col1:
        metric_card("✅ Contestador ≤ 10s", metrics['contestador_menor'], "green-card",
                   subtext="Buenas prácticas - Cortar rápido")
    with col2:
        metric_card("❌ Contestador > 10s", metrics['contestador_mayor'], "red-card",
                   subtext="Área de mejora - Cortar antes")
    
    st.divider()
    
    # Fila 3 - No Interesado
    st.subheader("🚫 Análisis de No Interesados por Duración")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        metric_card("⚠️ No interesado 2-5 min", metrics['no_interesado_2_5min'], "yellow-card",
                   subtext="Rango de 2 a 5 minutos")
    
    with col2:
        metric_card("🔴 No interesado > 5 min", metrics['no_interesado_mas_5min'], "orange-card",
                   subtext="Más de 5 minutos - Problema grave")
    
    with col3:
        metric_card("💀 No interesado > 10 min", metrics['no_interesado_mas_10min'], "red-card",
                   subtext="MÁS DE 10 MINUTOS - Revisión URGENTE")
    
    st.divider()
    
    # Filtro rápido
    st.markdown("### 🎯 Filtro Rápido por Tipo de No Interesado")
    st.markdown("Selecciona una categoría para ver resultados detallados:")
    
    df_2_5 = df[df["no_interesado_2_5min"]]
    df_mas_5 = df[df["no_interesado_mas_5min"]]
    df_mas_10 = df[df["no_interesado_mas_10min"]]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⚠️ 2 - 5 minutos", use_container_width=True, key="filter_2_5"):
            st.session_state["selected_filter"] = "2_5"
            st.rerun()
        st.caption(f"Total: {len(df_2_5)} llamadas")
    
    with col2:
        if st.button("🔴 Más de 5 minutos", use_container_width=True, key="filter_5"):
            st.session_state["selected_filter"] = "mas_5"
            st.rerun()
        st.caption(f"Total: {len(df_mas_5)} llamadas")
    
    with col3:
        if st.button("💀 Más de 10 minutos", use_container_width=True, key="filter_10"):
            st.session_state["selected_filter"] = "mas_10"
            st.rerun()
        st.caption(f"Total: {len(df_mas_10)} llamadas")
    
    st.divider()
    
    # Mostrar resultados del filtro
    if "selected_filter" in st.session_state:
        filtro = st.session_state["selected_filter"]
        
        if filtro == "2_5":
            mostrar_resultados_filtro(df_2_5, "⚠️ Llamadas de No Interesados (2-5 minutos)", "warning", "2_5")
        elif filtro == "mas_5":
            mostrar_resultados_filtro(df_mas_5, "🔴 Llamadas de No Interesados (Más de 5 minutos)", "critical", "mas_5")
        elif filtro == "mas_10":
            mostrar_resultados_filtro(df_mas_10, "💀 CRÍTICO - Llamadas de No Interesados (Más de 10 minutos)", "critical", "mas_10")
        
        st.divider()
    
    # Tabla de agentes
    st.subheader("👥 Análisis por Agente")
    
    display_cols = [
        "user", "full_name", "llamadas", "tiempo_total", "tiempo_promedio_seg",
        "contestador_menor", "contestador_mayor",
        "no_interesado_2_5min", "no_interesado_mas_5min", "no_interesado_mas_10min",
        "contactabilidad"
    ]
    
    st.dataframe(
        resumen_agente[display_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "user": "Agente",
            "full_name": "Nombre",
            "llamadas": st.column_config.NumberColumn("Llamadas", format="%d"),
            "tiempo_total": "Tiempo Total",
            "tiempo_promedio_seg": st.column_config.NumberColumn("Promedio (seg)", format="%.1f"),
            "contestador_menor": "Contestador ≤10s",
            "contestador_mayor": "Contestador >10s",
            "no_interesado_2_5min": "No Interesado 2-5min",
            "no_interesado_mas_5min": "No Interesado >5min",
            "no_interesado_mas_10min": "No Interesado >10min",
            "contactabilidad": st.column_config.NumberColumn("Contactabilidad %", format="%.1f%%")
        }
    )
    
    st.divider()
    
    # Tabs
    tab1, tab2 = st.tabs(["📊 Ranking Agentes", "🚨 Problemas Detectados"])
    
    with tab1:
        fig = px.bar(
            resumen_agente.head(15),
            x="user",
            y="tiempo_total_seg",
            text="tiempo_total",
            title=f"Top 15 Agentes - {campaign}",
            color="tiempo_total_seg",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        problemas = df[df["nivel_problema"].isin(["Problema grave", "Problema grave +10min", "Alerta media"])]
        if problemas.empty:
            st.success("✅ No se detectaron problemas")
        else:
            st.warning(f"⚠️ {len(problemas)} llamadas con problemas")
            columnas_problemas = ["user", "full_name", "phone_number_dialed", "status_name", "length_in_sec", "minutos_hablados", "nivel_problema", "comentario_mejora"]
            columnas_disponibles = [col for col in columnas_problemas if col in problemas.columns]
            st.dataframe(
                problemas[columnas_disponibles],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "user": "Agente",
                    "full_name": "Nombre",
                    "phone_number_dialed": "📞 Teléfono",
                    "status_name": "Status",
                    "length_in_sec": "Duración (seg)",
                    "minutos_hablados": "Minutos",
                    "nivel_problema": "Nivel",
                    "comentario_mejora": "Comentario"
                }
            )
    
    # Footer
    st.markdown(f"""
    <div class="dashboard-footer">
        📊 <strong>{campaign}</strong> | 
        Última actualización: {st.session_state.get('last_update', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')} | 
        {metrics['total_llamadas']} llamadas analizadas | 
        {metrics['total_agentes']} agentes activos | 
        👤 Rol: {st.session_state['user']}
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# MAIN
# ============================================================================

def main():
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        login_screen()
    else:
        main_dashboard()


if __name__ == "__main__":
    main()