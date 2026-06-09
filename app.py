import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Configuración de la página web
st.set_page_config(page_title="Auditoría Comparativa RRHH - BCG", page_icon="📊", layout="wide")

st.title("📊 Sistema Avanzado de Auditoría de Selección & Modelo BCG")
st.markdown("---")

# Crear las dos pestañas principales del sistema web
tab1, tab2 = st.tabs(["🎯 1. Auditoría de Validez (Subir 2 Excels)", "💰 2. Simulación y Retorno Financiero BCG"])

# ==========================================
# PESTAÑA 1: AUDITORÍA DE VALIDEZ COMPARATIVA
# ==========================================
with tab1:
    st.header("Análisis Estadístico: Proceso Actual vs. Proceso Nuevo")
    st.write("Cargue los datos históricos de ambos procesos para calcular y comparar sus niveles de validez reales.")
    
    # Creamos un diseño de dos columnas en la web para cargar los dos archivos de forma paralela
    col_file1, col_file2 = st.columns(2)
    
    # Inicializamos variables de validez en la sesión para que no se borren
    if 'r1_calculado' not in st.session_state:
        st.session_state['r1_calculado'] = 0.20  # Valor base por defecto
    if 'r2_calculado' not in st.session_state:
        st.session_state['r2_calculado'] = 0.50  # Valor base por defecto

    # --- COLUMNA IZQUIERDA: PROCESO ACTUAL ---
    with col_file1:
        st.subheader("📉 Planilla A: Proceso Histórico / Actual")
        st.caption("Cargue el archivo con los resultados del método que venía usando antes (ej: solo entrevistas).")
        uploaded_actual = st.file_uploader("Subir Excel Proceso Actual (.xlsx)", type=["xlsx"], key="actual_file")
        
        if uploaded_actual is not None:
            try:
                # Intento de lectura tolerante a instrucciones superiores
                try:
                    df_act = pd.read_excel(uploaded_actual, header=8)
                    df_act.columns = df_act.columns.str.strip()
                    columnas_necesarias = ['Test_Inteligencia', 'Test_Personalidad', 'Prueba_Tecnica', 'Desempeno_Real']
                    if not all(col in df_act.columns for col in columnas_necesarias): raise KeyError()
                except Exception:
                    df_act = pd.read_excel(uploaded_actual, header=0)
                    df_act.columns = df_act.columns.str.strip()
                
                # Limpieza y Regresión
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
                else:
                    st.error("Se necesitan al menos 3 filas de datos válidas.")
            except Exception as e:
                st.error("Error al procesar el archivo del Proceso Actual. Revise los encabezados.")

    # --- COLUMNA DERECHA: PROCESO NUEVO ---
    with col_file2:
        st.subheader("🚀 Planilla B: Proceso Científico / Nuevo")
        st.caption("Cargue el archivo con los resultados de la nueva batería de test que desea auditar o proponer.")
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
                
                # Limpieza y Regresión
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
                else:
                    st.error("Se necesitan al menos 3 filas de datos válidas.")
            except Exception as e:
                st.error("Error al procesar el archivo del Proceso Nuevo. Revise los encabezados.")

    st.markdown("---")
    st.info("💡 **Nota metodológica:** Una vez cargadas una o ambas planillas, los valores se inyectarán de forma automática en el simulador financiero de la pestaña superior. Si no sube archivos, el sistema trabajará con valores estándar de mercado (0.20 vs 0.50).")

# ==========================================
# PESTAÑA 2: SIMULADOR FINANCIERO BCG
# ==========================================
with tab2:
    st.header("Simulador de Retorno de Inversión (Utility Analysis - BCG)")
    st.write("Compare el impacto financiero en la productividad neta de la empresa utilizando los datos reales extraídos de sus Excels.")
    
    # Recuperamos los coeficientes reales calculados en la Pestaña 1
    r1_final = st.session_state['r1_calculado']
    r2_final = st.session_state['r2_calculado']
    
    st.info(f"📋 **Coeficientes Vinculados en Tiempo Real:** Validez Actual (**r1 = {r1_final:.2f}**) | Validez Nueva (**r2 = {r2_final:.2f}**)")

    # Formulario de parámetros económicos
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        st.subheader("📊 Parámetros del Puesto y Estructura")
        N = st.number_input("Número de seleccionados al año (N)", value=10, min_value=1)
        T = st.number_input("Permanencia promedio del trabajador en años (T)", value=2.0, min_value=0.1)
        C_actual = st.number_input("Costo de evaluación por postulante - Proceso Actual ($)", value=50.0)
        C_nuevo = st.number_input("Costo de evaluación por postulante - Proceso Nuevo ($)", value=120.0)
        
    with col_input2:
        st.subheader("📈 Métricas de Productividad Laboral")
        salario_anual = st.number_input("Sueldo bruto anual promedio de la posición ($)", value=24000.0)
        porcentaje_sd = st.slider("Desviación estándar del desempeño (SDy % del sueldo)", min_value=10, max_value=60, value=40)
        SD_y = salario_anual * (porcentaje_sd / 100)
        st.caption(f"Variabilidad estimada del rendimiento (SDy): ${SD_y:,.2f} anuales por individuo.")

    st.markdown("#### 🎯 Parámetros del Embudo de Reclutamiento")
    tasa_seleccion = st.slider("Tasa de Selección (Porcentaje de postulantes aceptados del total evaluado)", min_value=1, max_value=100, value=20)
    
    # Cálculos estadísticos del filtro (Z/SR)
    SR = tasa_seleccion / 100.0
    from scipy.stats import norm
    phi_lambda = norm.pdf(norm.ppf(1 - SR)) if SR < 1.0 else 0.0
    Z_score_factor = phi_lambda / SR if SR > 0 else 0.0
    st.caption(f"Factor estadístico de selectividad (Z/SR): {Z_score_factor:.3f}")

    # --- EJECUCIÓN DEL MODELO FINANCIERO DE RESTA DIRECTA ---
    if st.button("💰 Calcular Retorno Financiero de la Estrategia (ROI)", type="primary"):
        # Ecuación de Brogden-Cronbach-Gleser para cada escenario independiente
        utilidad_actual = (N * T * r1_final * SD_y * Z_score_factor) - (N * (1/SR) * C_actual)
        utilidad_nueva  = (N * T * r2_final * SD_y * Z_score_factor) - (N * (1/SR) * C_nuevo)
        incremento_neto = utilidad_nueva - utilidad_actual
        
        st.markdown("---")
        st.subheader("💵 Informe Ejecutivo de Utilidad Económica")
        
        c_res1, c_res2, c_res3 = st.columns(3)
        c_res1.metric(label="Rendimiento Financiero (Proceso Actual)", value=f"${utilidad_actual:,.2f}")
        c_res2.metric(label="Rendimiento Financiero (Proceso Nuevo)", value=f"${utilidad_nueva:,.2f}")
        
        if incremento_neto > 0:
            c_res3.metric(label="INCREMENTO NETO PATRIMONIAL (AHORRO)", value=f"${incremento_neto:,.2f}", delta=f"${incremento_neto:,.2f}")
            st.balloons()
            st.success(f"🚀 **Conclusión Gerencial:** Al comparar directamente la eficacia de ambas planillas, sustituir el Proceso Actual por el Proceso Nuevo generará una utilidad económica incremental de **${incremento_neto:,.2f}** durante la permanencia de los contratados, cubriendo con creces el aumento en los costos de inversión operativa.")
        else:
            c_res3.metric(label="DIFERENCIA NETA", value=f"${incremento_neto:,.2f}", delta=f"${incremento_neto:,.2f}", delta_color="inverse")
            st.error("⚠️ **Conclusión Gerencial:** Los datos reales de rendimiento demuestran que el aumento en los costos del Proceso Nuevo no se justifica frente al rendimiento histórico del Proceso Actual.")
            
