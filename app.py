"""
Dashboard Call Center Pro - Versión Final para Producción
Con métricas: 2-5min, >5min, >10min
Roles: Admin y Supervisor
Campañas: Energía y Telefonía
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

# ============================================================================
# CONFIGURACIÓN INICIAL
# ============================================================================

st.set_page_config(
    page_title="Call Center Analytics Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de campañas
CAMPANAS = {
    "Energía": {
        "icon": "⚡",
        "color": "#f97316",
        "gradient": "linear-gradient(135deg, #f97316, #ea580c)",
        "csv_path": "REPORTE_ENERGIA.csv",
        "description": "Campaña de Energía - Ventas de servicios eléctricos"
    },
    "Telefonía": {
        "icon": "📱",
        "color": "#3b82f6",
        "gradient": "linear-gradient(135deg, #3b82f6, #2563eb)",
        "csv_path": "REPORTE_TELEFONIA.csv",
        "description": "Campaña de Telefonía - Planes móviles y fibra óptica"
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

# CSS Profesional
CUSTOM_CSS = """
<style>
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.block-container {
    padding-top: 1rem;
    animation: fadeIn 0.5s ease-out;
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

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    transition: left 0.5s;
}

.metric-card:hover::before {
    left: 100%;
}

.metric-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 30px -10px rgba(0,0,0,0.4);
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

.green-card {
    background: linear-gradient(135deg, #064e3b, #059669);
}
.red-card {
    background: linear-gradient(135deg, #7f1d1d, #dc2626);
}
.orange-card {
    background: linear-gradient(135deg, #7c2d12, #ea580c);
}
.blue-card {
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
}
.purple-card {
    background: linear-gradient(135deg, #4c1d95, #8b5cf6);
}
.yellow-card {
    background: linear-gradient(135deg, #854d0e, #eab308);
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
    box-shadow: 0 2px 8px rgba(220,38,38,0.3);
}

.role-badge-supervisor {
    background: linear-gradient(135deg, #3b82f6, #1e40af);
    padding: 6px 16px;
    border-radius: 30px;
    font-size: 0.8rem;
    font-weight: 700;
    display: inline-block;
    box-shadow: 0 2px 8px rgba(59,130,246,0.3);
}

.fresh-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
    animation: pulse 2s infinite;
}

.fresh-green { background-color: #22c55e; box-shadow: 0 0 10px #22c55e; }
.fresh-yellow { background-color: #eab308; box-shadow: 0 0 10px #eab308; }
.fresh-red { background-color: #ef4444; box-shadow: 0 0 10px #ef4444; }

.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    font-weight: 600;
    border-radius: 12px;
    padding: 10px 20px;
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 0.85rem;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px -5px rgba(102, 126, 234, 0.4);
}

.campaign-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border-radius: 16px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2px solid transparent;
    text-align: center;
}

.campaign-card:hover {
    transform: translateY(-3px);
    border-color: #667eea;
}

.campaign-card-active {
    border-color: #22c55e;
    background: linear-gradient(135deg, #1e3a3a, #0f172a);
}

.campaign-icon {
    font-size: 2.5rem;
    margin-bottom: 10px;
}

.campaign-title {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 5px;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #1e293b;
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

.dashboard-footer {
    margin-top: 30px;
    padding: 20px;
    text-align: center;
    border-top: 1px solid #334155;
    font-size: 0.8rem;
    color: #64748b;
}
</style>
"""

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
    
    # Métricas de contestador
    df["contestador_menor_igual_10s"] = df["es_contestador"] & (df["length_in_sec"] <= 10)
    df["contestador_mayor_10s"] = df["es_contestador"] & (df["length_in_sec"] > 10)
    
    # Métricas de NO INTERESADO por rangos
    df["no_interesado"] = df["es_no_interesado"]
    
    # Rango 2-5 minutos (120-300 segundos)
    df["no_interesado_2_5min"] = df["es_no_interesado"] & (df["length_in_sec"] >= 120) & (df["length_in_sec"] < 300)
    
    # Mayor a 5 minutos (300+ segundos)
    df["no_interesado_mas_5min"] = df["es_no_interesado"] & (df["length_in_sec"] >= 300)
    
    # Mayor a 10 minutos (600+ segundos)
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
            return "⚠️ Problema: contestador >10 segundos"
        if row.get("es_no_interesado", False):
            seg = row.get("length_in_sec", 0)
            if seg >= 600: return "🔴 CRÍTICO: No interesado con MÁS DE 10 MINUTOS - Revisión URGENTE"
            if seg >= 300: return "🔴 Grave: no interesado >5 minutos"
            if seg >= 120: return "🟡 Alerta: no interesado >2 minutos"
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


def export_to_excel(df: pd.DataFrame, campaign: str) -> bytes:
    output = io.BytesIO()
    resumen_agente = get_agente_summary(df)
    problemas = df[df["nivel_problema"].isin(["Problema grave", "Problema grave +10min", "Alerta media"])]
    
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        resumen_agente.to_excel(writer, sheet_name="Resumen Agente", index=False)
        problemas.to_excel(writer, sheet_name="Problemas Detectados", index=False)
        df.to_excel(writer, sheet_name="Detalle Filtrado", index=False)
    
    return output.getvalue()


# ============================================================================
# LOGIN
# ============================================================================

def login_screen():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    st.title("🎯 Call Center Analytics Pro")
    st.markdown("### Sistema de Gestión Profesional")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        st.markdown("#### 🔐 Acceso al Sistema")
        
        role = st.radio(
            "Selecciona tu rol:",
            ["supervisor", "admin"],
            format_func=lambda x: "👑 Administrador" if x == "admin" else "👁️ Supervisor",
            horizontal=True
        )
        
        password = st.text_input("Contraseña:", type="password")
        
        if st.button("Ingresar al Dashboard", use_container_width=True):
            expected_password = ROLES_CONFIG[role]["password"]
            if password == expected_password:
                st.session_state["authenticated"] = True
                st.session_state["role"] = role
                st.session_state["user"] = ROLES_CONFIG[role]["name"]
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
        
        st.markdown("---")
        st.caption("🔒 Sistema seguro - Acceso restringido")


# ============================================================================
# DASHBOARD PRINCIPAL
# ============================================================================

def main_dashboard():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    role = st.session_state["role"]
    is_admin = (role == "admin")
    
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title("🎯 Call Center Analytics Pro")
        st.caption(f"Bienvenido, {st.session_state['user']}")
    
    with col2:
        if is_admin:
            st.markdown('<div class="role-badge-admin">👑 ADMINISTRADOR</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="role-badge-supervisor">👁️ SUPERVISOR</div>', unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 Cerrar Sesión"):
            for key in ["authenticated", "role", "user", "selected_campaign"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    st.divider()
    
    # Selección de campaña
    st.markdown("### 📊 Seleccionar Campaña")
    
    col1, col2 = st.columns(2)
    
    for idx, (campaign, config) in enumerate(CAMPANAS.items()):
        col = col1 if idx == 0 else col2
        is_active = st.session_state.get("selected_campaign") == campaign
        
        with col:
            if st.button(
                f"{config['icon']} {campaign}",
                use_container_width=True,
                key=f"campaign_{campaign}"
            ):
                st.session_state["selected_campaign"] = campaign
                st.rerun()
    
    if "selected_campaign" not in st.session_state:
        st.session_state["selected_campaign"] = "Energía"
    
    campaign = st.session_state["selected_campaign"]
    campaign_config = CAMPANAS[campaign]
    
    st.info(f"{campaign_config['icon']} **{campaign}** - {campaign_config['description']}")
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
                st.cache_data.clear()
        
        with col2:
            uploaded_telefonia = st.file_uploader("REPORTE_TELEFONIA.csv", type=["csv"], key="upload_telefonia")
            if uploaded_telefonia:
                with open("REPORTE_TELEFONIA.csv", "wb") as f:
                    f.write(uploaded_telefonia.getbuffer())
                st.success("✅ Telefonía actualizado")
                st.cache_data.clear()
        
        st.divider()
    
    # Cargar datos
    csv_path = Path(campaign_config["csv_path"])
    
    if not csv_path.exists():
        if is_admin:
            st.warning(f"⚠️ No se encuentra {campaign_config['csv_path']}")
        else:
            st.warning(f"⚠️ Datos de {campaign} no disponibles")
        return
    
    with st.spinner(f"Cargando {campaign}..."):
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
                <div>📅 {st.session_state['last_update'].strftime('%Y-%m-%d %H:%M:%S')}</div>
                <div>{freshness_detail}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Filtros
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
        agentes_filter = st.multiselect("👤 Agentes", agentes, default=agentes)
        if agentes_filter:
            df = df[df["user"].isin(agentes_filter)]
        
        statuses = sorted(df["status_name"].dropna().unique().tolist())
        status_filter = st.multiselect("📌 Status", statuses, default=[])
        if status_filter:
            df = df[df["status_name"].isin(status_filter)]
        
        niveles = ["Todos", "Correcto", "Normal", "Alerta media", "Problema grave", "Problema grave +10min"]
        nivel_filter = st.selectbox("🚨 Nivel de problema", niveles)
        if nivel_filter != "Todos":
            df = df[df["nivel_problema"] == nivel_filter]
    
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
    
    # Fila 2 - Contestador
    st.subheader("📞 Análisis de Contestador Automático")
    col1, col2 = st.columns(2)
    
    with col1:
        metric_card("✅ Contestador ≤ 10s", metrics['contestador_menor'], "green-card",
                   subtext="Buenas prácticas - Cortar rápido")
    with col2:
        metric_card("❌ Contestador > 10s", metrics['contestador_mayor'], "red-card",
                   subtext="Área de mejora - Cortar antes")
    
    st.divider()
    
    # Fila 3 - No Interesado (NUEVO)
    st.subheader("🚫 Análisis de No Interesados por Duración")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        metric_card("⚠️ No interesado 2-5 min", metrics['no_interesado_2_5min'], "yellow-card",
                   subtext="Rango de 2 a 5 minutos - Revisar argumentación")
    
    with col2:
        metric_card("🔴 No interesado > 5 min", metrics['no_interesado_mas_5min'], "orange-card",
                   subtext="Más de 5 minutos - Problema grave")
    
    with col3:
        metric_card("💀 No interesado > 10 min", metrics['no_interesado_mas_10min'], "red-card",
                   subtext="MÁS DE 10 MINUTOS - Revisión URGENTE")
    
    st.divider()
    
    # Tabla por agente
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
    tab1, tab2, tab3 = st.tabs(["📊 Ranking Agentes", "🚨 Problemas Detectados", "📋 Detalle Completo"])
    
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
            st.dataframe(
                problemas[["user", "status_name", "length_in_sec", "minutos_hablados", "nivel_problema", "comentario_mejora"]],
                use_container_width=True,
                hide_index=True
            )
    
    with tab3:
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Exportar
    st.divider()
    excel_data = export_to_excel(df, campaign)
    st.download_button(
        label="📥 Descargar Análisis Completo (Excel)",
        data=excel_data,
        file_name=f"reporte_{campaign.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    
    # Footer
    st.markdown(f"""
    <div class="dashboard-footer">
        📊 <strong>{campaign}</strong> | 
        Última actualización: {st.session_state.get('last_update', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')} | 
        {metrics['total_llamadas']} llamadas | 
        {metrics['total_agentes']} agentes | 
        Rol: {st.session_state['user']}
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