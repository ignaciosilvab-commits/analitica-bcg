import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import requests

# Configuración de la página web
st.set_page_config(page_title="Auditoría RRHH & Modelo BCG Chile", page_icon="📊", layout="wide")

# --- FUNCIÓN PARA OBTENER LA UF EN TIEMPO REAL ---
@st.cache_data(ttl=3600)  # Guarda el valor por 1 hora para que cargue rápido
def obtener_uf_actual():
    try:
        # Consultamos la API pública de mindicador.cl
        url = "https://mindicador.cl/api/uf"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            datos = response.json()
            valor_uf = datos['serie'][0]['valor']
            fecha_uf = datos['serie'][0]['fecha'][:10]
            # Formatear fecha a DD-MM-AAAA
            fecha_f = "-".join(fecha_uf.split("-")[::-1])
            return float(valor_uf), fecha_f
    except Exception:
        pass
    return 38000.0, "Valor estimado (Error de conexión)" # Valor de respaldo si la API falla

# Cargar la UF al iniciar la app
valor_uf, fecha_uf = obtener_uf_actual()

st.title("📊 Sistema Avanzado de Analítica de Selección (Modelo BCG - Chile)")
st.markdown(f"**Indicador Económico del Día:** 1 UF = **${valor_uf:,.2f} CLP** *(Actualizado al: {fecha_uf})*")
st.markdown("---")

# Crear las dos pestañas principales del sistema web
tab1, tab2 = st.tabs(["🎯 1. Auditoría de Validez (Subir 2 Excels)", "🇨🇱 2. Simulación Financiera BCG (en CLP y UF)"])

# ==========================================
# PESTAÑA 1: AUDITORÍA DE VALIDEZ COMPARATIVA
# ==========================================
with tab1:
    st.header("Análisis Estadístico: Proceso Actual vs. Proceso Nuevo")
    st.write("Cargue los datos históricos de ambos procesos para calcular sus niveles de validez reales.")
    
    col_file1, col_file2 = st.columns(2)
    
    if 'r1_calculado' not in st.session_state:
        st.session_state['r1_calculado'] = 0.20  
    if 'r2_calculado' not in st.session_state:
        st.session_state['r2_calculado'] = 0.49  

    with col_file1:
        st.subheader("📉 Planilla A: Proceso Histórico / Actual")
        uploaded_actual = st.file_uploader("Subir Excel Proceso Actual (.xlsx)", type=["xlsx"], key="actual_file")
        if uploaded_actual is not None:
            try:
                try:
                    df_act = pd.read_excel(uploaded_actual, header=8)
                    df_act.columns = df_act.columns.str.strip()
                    columnas_necesarias = ['Test_Inteligencia', 'Test_Personalidad', 'Prueba_Tecnica', 'Desempeno_Real']
                    if not all(col in df_act.columns for col in columnas_necesarias): raise KeyError()
                except Exception:
                    df_act = pd.read_excel(uploaded_actual, header=0)
                    df_act.columns = df_act.columns.str.strip()
                
                df_act = df_act.dropna(subset=['Test_Inteligencia', 'Test_Personalidad', 'Prueba_Tecnica', 'Desempeno_Real'])
                if len(df_act) >= 3:
                    X_act = df_act[['Test_Inteligencia', 'Test_Personalidad', 'Prueba_Tecnica']]
                    y_act = df_act['Desempeno_Real']
                    modelo_act = LinearRegression()
                    modelo_act.fit(X_act, y_act)
                    r1 = np.sqrt(modelo_act.score(X_act, y_act))
                    st.session_state['r1_calculado'] = float(r1)
                    st.metric(label="VALIDEZ REAL PROCESO ACTUAL (r1)", value=f"{r1:.2f}")
                    st.success(f"✔️ {len(df_act)} casos procesados con éxito.")
                else: st.error("Se necesitan al menos 3 filas de datos válidas.")
            except Exception: st.error("Error al procesar el archivo. Revise los encabezados.")

    with col_file2:
        st.subheader("🚀 Planilla B: Proceso Científico / Nuevo")
        uploaded_nuevo = st.file_uploader("Subir Excel Proceso Nuevo (.xlsx)", type=["xlsx"], key="nuevo_file")
        if uploaded_nuevo is not None:
            try:
                try:
                    df_nov = pd.read_excel(uploaded_nuevo, header=8)
                    df_nov.columns = df_nov.columns.str.strip()
                    columnas_necesarias = ['Test_Inteligencia', 'Test_Personalidad', 'Prueba_Tecnica', 'Desempeno_Real']
                    if not all(col in df_nov.columns for col in columnas_necesarias): raise KeyError()
                except Exception:
                    df_nov = pd.read_excel(uploaded_nuevo, header=0)
                    df_nov.columns = df_nov.columns.str.strip()
                
                df_nov = df_nov.dropna(subset=['Test_Inteligencia', 'Test_Personalidad', 'Prueba_Tecnica', 'Desempeno_Real'])
                if len(df_nov) >= 3:
                    X_nov = df_nov[['Test_Inteligencia', 'Test_Personalidad', 'Prueba_Tecnica']]
                    y_nov = df_nov['Desempeno_Real']
                    modelo_nov = LinearRegression()
                    modelo_nov.fit(X_nov, y_nov)
                    r2 = np.sqrt(modelo_nov.score(X_nov, y_nov))
                    st.session_state['r2_calculado'] = float(r2)
                    st.metric(label="VALIDEZ REAL PROCESO NUEVO (r2)", value=f"{r2:.2f}")
                    st.success(f"✔️ {len(df_nov)} casos procesados con éxito.")
                else: st.error("Se necesitan al menos 3 filas de datos válidas.")
            except Exception: st.error("Error al procesar el archivo. Revise los encabezados.")

# ==========================================
# PESTAÑA 2: SIMULADOR FINANCIERO BCG CHILE
# ==========================================
with tab2:
    st.header("Simulador de Utilidad Económica en Pesos Chilenos (BCG)")
    st.write("Determine el impacto financiero neto convirtiendo los costos de UF a CLP de forma automatizada.")
    
    r1_final = st.session_state['r1_calculado']
    r2_final = st.session_state['r2_calculado']
    
    st.info(f"📋 **Valideces Vinculadas:** Proceso Actual (**r1 = {r1_final:.2f}**) | Proceso Nuevo (**r2 = {r2_final:.2f}**)")

    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        st.subheader("📊 Estructura del Cargo y Filtros")
        N = st.number_input("Número de contratados al año (N)", value=10, min_value=1)
        T = st.number_input("Permanencia promedio en el puesto en años (T)", value=2.0, min_value=0.1)
        
        st.markdown("---")
        st.markdown("**💰 Costos de Selección (en UF):**")
        C_actual_uf = st.number_input("Costo de evaluación por postulante - Proceso Actual (UF)", value=1.5, step=0.1)
        C_nuevo_uf = st.number_input("Costo de evaluación por postulante - Proceso Nuevo (UF)", value=3.0, step=0.1)
        
        # Conversión automática a pesos para mostrar información al usuario
        c_act_clp = C_actual_uf * valor_uf
        c_nov_clp = C_nuevo_uf * valor_uf
        st.caption(f"➔ Equivalente en CLP: Proceso Actual: **${c_act_clp:,.0f}** | Proceso Nuevo: **${c_nov_clp:,.0f}** por postulante.")
        
    with col_input2:
        st.subheader("📈 Productividad Laboral Chilena")
        sueldo_mensual_clp = st.number_input("Sueldo BRUTO mensual promedio ($ CLP)", value=1500000, step=50000)
        
        # El modelo BCG requiere salario bruto ANUAL
        salario_anual_clp = sueldo_mensual_clp * 12
        
        porcentaje_sd = st.slider("Desviación estándar del desempeño (SDy % del sueldo)", min_value=10, max_value=60, value=40)
        SD_y_clp = salario_anual_clp * (porcentaje_sd / 100)
        
        st.caption(f"Sueldo Bruto Anualizado: ${salario_anual_clp:,.0f} CLP")
        st.caption(f"Variabilidad de rendimiento anual (SDy): **${SD_y_clp:,.0f} CLP**")

    st.markdown("#### 🎯 Selectividad del Embudo")
    tasa_seleccion = st.slider("Tasa de Selección (% de postulantes aceptados del total evaluado)", min_value=1, max_value=100, value=20)
    
    SR = tasa_seleccion / 100.0
    from scipy.stats import norm
    phi_lambda = norm.pdf(norm.ppf(1 - SR)) if SR < 1.0 else 0.0
    Z_score_factor = phi_lambda / SR if SR > 0 else 0.0

    # --- EJECUCIÓN DEL MODELO EN PESOS ---
    if st.button("💰 Calcular Impacto Económico en CLP", type="primary"):
        # Costos totales convertidos a pesos en la fórmula
        utilidad_actual_clp = (N * T * r1_final * SD_y_clp * Z_score_factor) - (N * (1/SR) * (C_actual_uf * valor_uf))
        utilidad_nueva_clp  = (N * T * r2_final * SD_y_clp * Z_score_factor) - (N * (1/SR) * (C_nuevo_uf * valor_uf))
        incremento_neto_clp = utilidad_nueva_clp - utilidad_actual_clp
        incremento_neto_uf = incremento_neto_clp / valor_uf
        
        st.markdown("---")
        st.subheader("🇨🇱 Informe Ejecutivo de Retorno de Inversión (CLP / UF)")
        
        c_res1, c_res2, c_res3 = st.columns(3)
        c_res1.metric(label="Rendimiento (Proceso Actual)", value=f"${utilidad_actual_clp:,.0f} CLP")
        c_res2.metric(label="Rendimiento (Proceso Nuevo)", value=f"${utilidad_nueva_clp:,.0f} CLP")
        
        if incremento_neto_clp > 0:
            c_res3.metric(label="INCREMENTO NETO PATRIMONIAL", value=f"${incremento_neto_clp:,.0f} CLP", delta=f"${incremento_neto_clp:,.0f} CLP")
            st.balloons()
            st.success(f"🚀 **Conclusión Estratégica:** Reemplazar el método tradicional por la nueva batería de test generará un beneficio económico incremental de **${incremento_neto_clp:,.0f} CLP** (equivalente a **{incremento_neto_uf:.1f} UF**) durante el ciclo laboral de los trabajadores contratados. El retorno justifica plenamente la inversión.")
        else:
            c_res3.metric(label="DIFERENCIA NETA", value=f"${incremento_neto_clp:,.0f} CLP", delta=f"${incremento_neto_clp:,.0f} CLP", delta_color="inverse")
            st.error("⚠️ **Conclusión Estratégica:** Los costos en UF de la nueva batería o la diferencia de validez no justifican financieramente modificar el proceso histórico.")
            
