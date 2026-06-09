import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import requests
from datetime import datetime

# 1. Configuración inicial de la página (Adaptada a pantallas móviles)
st.set_page_config(page_title="Análisis de ROI adicional", page_icon="🇨🇱", layout="centered")

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
    return 40746.28  # Valor histórico de respaldo basado en tu captura

# Cargar la UF inicial en el estado de la sesión
if 'valor_uf' not in st.session_state:
    st.session_state['valor_uf'] = obtener_uf_actual()

# Inicialización de variables globales de validez predictiva para que no se pierdan
if 'r1_auto' not in st.session_state:
    st.session_state['r1_auto'] = 0.40  
if 'r2_auto' not in st.session_state:
    st.session_state['r2_auto'] = 0.80  

# --- TÍTULO PRINCIPAL ---
st.title("Análisis de ROI adicional de método actual versus nuevo")
st.markdown("---")

# ==========================================
# SECCIÓN: CALCULADORA DE VALIDEZ PREDICTIVA
# ==========================================
st.markdown("### 🎯 Calculadora validez predictiva de batería de selección")
st.write("Cargue sus archivos para calcular de forma automatizada las valideces (r1 y r2).")

col_up1, col_up2 = st.columns(2)

def procesar_excel_inteligente(uploaded_file):
    """Busca los encabezados mapeados sin importar si hay texto o instrucciones previas"""
    if uploaded_file is None:
        return None
    try:
        for i in range(15):  
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
            st.error("❌ Error: Columnas no encontradas.")
        elif res_r1 is not None:
            st.session_state['r1_auto'] = float(res_r1)
            st.success(f"Validez calculada r1: {res_r1:.2f}")

with col_up2:
    file_nov = st.file_uploader("Planilla Proceso Nuevo", type=["xlsx"], key="u_nov")
    if file_nov:
        res_r2 = procesar_excel_inteligente(file_nov)
        if res_r2 == "Error_Columnas":
            st.error("❌ Error: Columnas no encontradas.")
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

# Regla del 40% automática para SDy
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
    st.toast("¡Valor de la UF actualizado!")

valor_uf_input = st.number_input("Valor de la UF ($):", value=st.session_state['valor_uf'], step=0.01)

# ==========================================
# SECCIÓN: PROCESO ACTUAL VS NUEVO
# ==========================================
st.subheader("PROCESO ACTUAL (1)")
col_act1, col_act2, col_act3 = st.columns(3)
with col_act1:
    r1 = st.number_input("r1 (Validez del test actual):", value=st.session_state['r1_auto'], min_value=0.0, max_value=1.0, step=0.01)
with col_act2:
    SR = k_porcentaje / 100.0
    from scipy.stats import norm
    phi_lambda = norm.pdf(norm.ppf(1 - SR)) if SR < 1.0 else 0.0
    Z1_calc = phi_lambda / SR if SR > 0 else 0.0
    Z1 = st.number_input("Z1 (Media predictor normalizado):", value=float(Z1_calc), step=0.01)
with col_act3:
    C1 = st.number_input("C1 (Costo por candidato en UF - Actual):", value=3.0, step=0.1)

st.subheader("NUEVO PROCESO PROPUESTO (2)")
col_nov1, col_nov2, col_nov3 = st.columns(3)
with col_nov1:
    r2 = st.number_input("r2 (Validez del nuevo test):", value=st.session_state['r2_auto'], min_value=0.0, max_value=1.0, step=0.01)
with col_nov2:
    Z2 = st.number_input("Z2 (Media predictor normalizado - Nuevo):", value=float(Z1_calc), step=0.01)
with col_nov3:
    C2 = st.number_input("C2 (Costo por candidato en UF - Nuevo):", value=6.0, step=0.1)

# Inicializar llaves en memoria para evitar errores de renderizado
if 'u_actual_res' not in st.session_state: st.session_state['u_actual_res'] = 0.0
if 'u_nuevo_res' not in st.session_state: st.session_state['u_nuevo_res'] = 0.0
if 'c_unitario_act' not in st.session_state: st.session_state['c_unitario_act'] = 0.0
if 'c_unitario_nov' not in st.session_state: st.session_state['c_unitario_nov'] = 0.0
if 'calculado' not in st.session_state: st.session_state['calculado'] = False

st.markdown("---")

# ==========================================
# SECCIÓN: BOTONES DE ACCIÓN (MÓDULO DE CONTROL)
# ==========================================
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("Calcular Utilidad", type="primary"):
        total_evaluados = N * (1 / SR)
        costo_unitario_act = C1 * valor_uf_input
        costo_unitario_nov = C2 * valor_uf_input
        
        utilidad_actual = (N * T * r1 * SD_y * Z1) - (total_evaluados * costo_unitario_act)
        utilidad_nueva  = (N * T * r2 * SD_y * Z2) - (total_evaluados * costo_unitario_nov)
        
        st.session_state['u_actual_res'] = utilidad_actual
        st.session_state['u_nuevo_res'] = utilidad_nueva
        st.session_state['c_unitario_act'] = costo_unitario_act
        st.session_state['c_unitario_nov'] = costo_unitario_nov
        st.session_state['calculado'] = True
        
        if utilidad_nueva > utilidad_actual:
            st.balloons()

with col_btn2:
    if st.button("Limpiar Datos"):
        st.session_state['r1_auto'] = 0.40
        st.session_state['r2_auto'] = 0.80
        st.session_state['u_actual_res'] = 0.0
        st.session_state['u_nuevo_res'] = 0.0
        st.session_state['c_unitario_act'] = 0.0
        st.session_state['c_unitario_nov'] = 0.0
        st.session_state['calculado'] = False
        st.rerun()

# ==========================================
# SECCIÓN: INFORME Y GRÁFICO INTERACTIVO
# ==========================================
if st.session_state['calculado']:
    import plotly.graph_objects as go
    
    u_act = st.session_state['u_actual_res']
    u_nov = st.session_state['u_nuevo_res']
    c_act = st.session_state['c_unitario_act']
    c_nov = st.session_state['c_unitario_nov']
    
    utilidad_incremental = u_nov - u_act
    por_empleado_ano = utilidad_incremental / (N * T) if (N * T) > 0 else 0.0

    # Conversión para el gráfico en escala de Millones de Pesos ($ M)
    val_act_m = u_act / 1000000
    val_nov_m = u_nov / 1000000
    val_inc_m = utilidad_incremental / 1000000

    categorias = ['Proceso Actual', 'Nuevo Proceso', 'DIFERENCIA NETAS']
    valores_m = [val_act_m, val_nov_m, val_inc_m]
    textos_barra = [f"${u_act:,.1f}M", f"${u_nov:,.1f}M", f"${utilidad_incremental:,.1f}M"]
    colores_barra = ['#94a3b8', '#1f77b4', '#2ca02c'] 

    fig = go.Figure(go.Bar(
        x=valores_m,
        y=categorias,
        orientation='h',
        text=textos_barra,
        textposition='outside', 
        marker_color=colores_barra,
        hovertemplate="<b>%{y}</b><br>Valor: %{text}<extra></extra>"
    ))

    fig.update_layout(
        title=f"<b>Comparativa y Diferencia - {nombre_cargo}</b>",
        title_x=0.5, 
        xaxis_title="Miles de Pesos ($ M)",
        # Habilitar barras de desplazamiento y estiramiento libre en los ejes
        xaxis=dict(showgrid=True, gridcolor='LightGray', gridwidth=0.5, fixedrange=False),
        yaxis=dict(autorange="reversed", fixedrange=False), 
        plot_bgcolor='white',
        margin=dict(l=120, r=60, t=50, b=50),
        height=380,
        dragmode='pan' # Activa el desplazamiento táctil/paneo por defecto
    )

    # Renderizar el gráfico con soporte completo para scroll de mouse y zoom táctil
    st.plotly_chart(
        fig, 
        use_container_width=True,
        config={
            'scrollZoom': True,
            'displayModeBar': True,
            'modeBarButtonsToRemove': [],
            'editable': False
        }
    )
    
    st.markdown("---")

    # Bloque analítico final idéntico al reporte corporativo
    st.markdown(f"""
    <div style='text-align: center; font-size: 19px; line-height: 1.6;'>
        Utilidad Proceso Actual: ${u_act:,.2f}<br>
        <span style='color: #666666;'>(Costo unitario calculado: ${c_act:,.2f})</span><br>
        Utilidad Nuevo Proceso: ${u_nov:,.2f}<br>
        <span style='color: #666666;'>(Costo unitario calculado: ${c_nov:,.2f})</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if utilidad_incremental > 0:
        st.markdown(f"""
        <div style='text-align: center; font-size: 22px; font-weight: bold;'>
            <span style='color: #2ca02c;'>¡Rentable para {nombre_cargo}!</span><br>
            <span style='color: #2ca02c;'>Utilidad Incremental: ${utilidad_incremental:,.2f}</span><br>
            <span style='color: #2ca02c;'>(+${por_empleado_ano:,.2f} por empleado/año)</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='text-align: center; font-size: 22px; font-weight: bold; color: #d62728;'>
            No Rentable para {nombre_cargo}<br>
            Diferencia Negativa: ${utilidad_incremental:,.2f}
        </div>
        """, unsafe_allow_html=True)
