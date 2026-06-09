import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import requests
from datetime import datetime

# Configuración de la página web adaptada a dispositivos móviles
st.set_page_config(page_title="Análisis Económico Avanzado (BCG)", page_icon="🇨🇱", layout="centered")

# --- FUNCIÓN PARA OBTENER LA UF EN TIEMPO REAL ---
@st.cache_data(ttl=3600)
def obtener_uf_actual():
    try:
        url = "https://mindicador.cl/api/uf"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            datos = response.json()
            valor_uf = datos['serie'][0]['valor']
            return float(valor_uf)
    except Exception:
        pass
    return 40746.28  # Usamos el valor exacto que aparece en tu captura de pantalla como respaldo

# Cargar la UF inicial
if 'valor_uf' not in st.session_state:
    st.session_state['valor_uf'] = obtener_uf_actual()

# Inicialización de variables globales de validez
if 'r1_auto' not in st.session_state:
    st.session_state['r1_auto'] = 0.40  # Valor por defecto de tu captura
if 'r2_auto' not in st.session_state:
    st.session_state['r2_auto'] = 0.80  # Valor por defecto de tu captura

# --- DISEÑO VISUAL DE LA INTERFAZ ---
st.title("ANÁLISIS ECONÓMICO AVANZADO (BCG)")

# ==========================================
# SECCIÓN: MÓDULO DE AUDITORÍA (EXCEL INTEGRADO)
# ==========================================
st.markdown("### 🎯 AUDITORÍA DE PLANILLAS EXCEL")
st.write("Cargue sus archivos para calcular de forma automatizada las valideces ($r_1$ y $r_2$). Si el Excel tiene texto introductorio, el sistema buscará los encabezados correctos de forma inteligente.")

col_up1, col_up2 = st.columns(2)

def procesar_excel_inteligente(uploaded_file):
    """Busca dinámicamente los encabezados correctos para evitar el error de la captura 1"""
    if uploaded_file is None:
        return None
    try:
        # Intentar leer desde el inicio primero
        for i in range(15):  # Probamos desde la fila 1 hasta la 15 como margen
            df = pd.read_excel(uploaded_file, header=i)
            df.columns = df.columns.str.strip()
            columnas_buscadas = ['Test_Inteligencia', 'Test_Personalidad', 'Prueba_Tecnica', 'Desempeno_Real']
            if all(col in df.columns for col in columnas_buscadas):
                df = df.dropna(subset=columnas_buscadas)
                X = df[['Test_Inteligencia', 'Test_Personalidad', 'Prueba_Tecnica']]
                y = df['Desempeno_Real']
                modelo = LinearRegression()
                modelo.fit(X, y)
                return np.sqrt(modelo.score(X, y))
    except Exception:
        pass
    return "Error_Columnas"

with col_up1:
    file_act = st.file_uploader("Planilla Proceso Actual", type=["xlsx"], key="u_act")
    if file_act:
        res_r1 = procesar_excel_inteligente(file_act)
        if res_r1 == "Error_Columnas":
            st.error("❌ Error: No se encontraron las columnas requeridas.")
        elif res_r1 is not None:
            st.session_state['r1_auto'] = float(res_r1)
            st.success(f"Validez calculada r1: {res_r1:.2f}")

with col_up2:
    file_nov = st.file_uploader("Planilla Proceso Nuevo", type=["xlsx"], key="u_nov")
    if file_nov:
        res_r2 = procesar_excel_inteligente(file_nov)
        if res_r2 == "Error_Columnas":
            st.error("❌ Error: No se encontraron las columnas requeridas.")
        elif res_r2 is not None:
            st.session_state['r2_auto'] = float(res_r2)
            st.success(f"Validez calculada r2: {res_r2:.2f}")

st.markdown("---")

# ==========================================
# SECCIÓN: DATOS DEL CARGO (REGLA 40%)
# ==========================================
st.subheader("DATOS DEL CARGO (REGLA 40%)")
nombre_cargo = st.text_input("Nombre del Cargo:", value="Analista TI")
sueldo_mensual = st.number_input("Sueldo Mensual ($):", value=1500000, step=50000)

# Regla del 40% automatizada para el cálculo de SDy
sueldo_anual = sueldo_mensual * 12
SD_y = sueldo_anual * 0.40
st.markdown(f"<span style='color:green;'>SDy (Variabilidad Anual): ${SD_y:,.2f} CLP</span>", unsafe_allow_html=True)

# ==========================================
# SECCIÓN: VARIABLES GENERALES
# ==========================================
st.subheader("VARIABLES GENERALES")
col_var1, col_var2, col_var3 = st.columns(3)
with col_var1:
    N = st.number_input("N (Número contratados):", value=15, min_value=1)
with col_var2:
    T = st.number_input("T (Años de permanencia):", value=3, min_value=1)
with col_var3:
    k_porcentaje = st.number_input("k (Razón de Selección %):", value=10, min_value=1, max_value=100)

# ==========================================
# SECCIÓN: CONEXIÓN FINANCIERA ONLINE
# ==========================================
st.subheader("CONEXIÓN FINANCIERA ONLINE")
fecha_hoy = datetime.today().strftime('%Y-%m-%d')
st.text_input("Fecha UF (AAAA-MM-DD):", value=fecha_hoy, disabled=True)

if st.button("Consultar Valor UF", type="secondary"):
    st.session_state['valor_uf'] = obtener_uf_actual()
    st.toast("¡Valor de UF actualizado desde el servidor público!")

valor_uf_input = st.number_input("Valor de la UF ($):", value=st.session_state['valor_uf'], step=0.01)

# ==========================================
# SECCIÓN: PROCESO ACTUAL (1) vs NUEVO (2)
# ==========================================
st.subheader("PROCESO ACTUAL (1)")
col_act1, col_act2, col_act3 = st.columns(3)
with col_act1:
    r1 = st.number_input("r1 (Validez del test actual):", value=st.session_state['r1_auto'], min_value=0.0, max_value=1.0, step=0.01)
with col_act2:
    # Cálculo estadístico preciso de la ordenada normal basándose en la Razón de Selección (SR)
    SR = k_porcentaje / 100.0
    from scipy.stats import norm
    phi_lambda = norm.pdf(norm.ppf(1 - SR)) if SR < 1.0 else 0.0
    Z1_calc = phi_lambda / SR if SR > 0 else 0.0
    Z1 = st.number_input("Z1 (Media predictor normalizado):", value=float(Z1_calc), step=0.01, help="Calculado automáticamente según la razón de selección k")
with col_act3:
    C1 = st.number_input("C1 (Costo por candidato en UF - Actual):", value=3.0, step=0.1)

st.subheader("NUEVO PROCESO PROPUESTO (2)")
col_nov1, col_nov2, col_nov3 = st.columns(3)
with col_nov1:
    r2 = st.number_input("r2 (Validez del nuevo test):", value=st.session_state['r2_auto'], min_value=0.0, max_value=1.0, step=0.01)
with col_nov2:
    Z2 = st.number_input("Z2 (Media predictor normalizado - Nuevo):", value=float(Z1_calc), step=0.01, help="Suele ser idéntico a Z1 al mantener la misma razón de selección k")
with col_nov3:
    C2 = st.number_input("C2 (Costo por candidato en UF - Nuevo):", value=6.0, step=0.1)

# Inicializar estados de utilidad en la sesión para despliegue posterior
if 'u_actual_res' not in st.session_state: st.session_state['u_actual_res'] = 0.0
if 'u_nuevo_res' not in st.session_state: st.session_state['u_nuevo_res'] = 0.0

st.markdown("---")

# ==========================================
# SECCIÓN: ACCIONES Y RESULTADOS FINALES
# ==========================================
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("Calcular Utilidad", type="primary"):
        # Ecuación Financiera Completa del Modelo BCG (Brogden-Cronbach-Gleser)
        # Multiplicamos el costo en UF por el valor de la UF y por la cantidad total de evaluados (N * (1/SR))
        total_evaluados = N * (1 / SR)
        
        utilidad_actual = (N * T * r1 * SD_y * Z1) - (total_evaluados * (C1 * valor_uf_input))
        utilidad_nueva  = (N * T * r2 * SD_y * Z2) - (total_evaluados * (C2 * valor_uf_input))
        
        st.session_state['u_actual_res'] = utilidad_actual
        st.session_state['u_nuevo_res'] = utilidad_nueva
        
        if utilidad_nueva > utilidad_actual:
            st.balloons()

with col_btn2:
    if st.button("Limpiar Datos"):
        st.session_state['r1_auto'] = 0.40
        st.session_state['r2_auto'] = 0.80
        st.session_state['u_actual_res'] = 0.0
        st.session_state['u_nuevo_res'] = 0.0
        st.rerun()

# Despliegue de los resultados numéricos idéntico a la parte baja de la imagen 2
st.markdown(f"### **Utilidad Proceso Actual:** `${st.session_state['u_actual_res']:,.0f} CLP`")
st.markdown(f"### **Utilidad Nuevo Proceso:** `${st.session_state['u_nuevo_res']:,.0f} CLP`")

# Mostrar el beneficio neto incremental
diferencia = st.session_state['u_nuevo_res'] - st.session_state['u_actual_res']
if diferencia > 0:
    st.success(f"🚀 **Incremento Neto Patrimonial (Ahorro):** `${diferencia:,.0f} CLP` (Equivalente a `{diferencia/valor_uf_input:,.1f} UF`)")
    
