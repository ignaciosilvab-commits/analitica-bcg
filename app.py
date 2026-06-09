import streamlit as pd_st
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Configuración de la página web
st.set_page_config(page_title="Ecosistema Analítico RRHH - BCG", page_icon="📊", layout="wide")

# Estilos visuales corporativos (opcional/básico)
st.title("📊 Ecosistema de Analítica de Selección & Modelo BCG")
st.markdown("---")

# Crear las dos pestañas principales del sistema web
tab1, tab2 = st.tabs(["🎯 1. Calculador de Validez (Excel)", "💰 2. Simulador Financiero BCG"])

# ==========================================
# PESTAÑA 1: CALCULADOR DE VALIDEZ (RESILE)
# ==========================================
with tab1:
    st.header("Análisis de Validez Criterio (Regresión Múltiple)")
    st.write("Cargue la matriz histórica de sus trabajadores contratados para auditar la validez conjunta de su batería.")
    
    # Componente web nativo para arrastrar y soltar el archivo Excel
    uploaded_file = st.file_uploader("Seleccione su archivo Excel (.xlsx)", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            # Intentar leer asumiendo formato con instrucciones (fila 9)
            try:
                df = pd.read_excel(uploaded_file, header=8)
                df.columns = df.columns.str.strip()
                columnas_necesarias = ['Test_Inteligencia', 'Test_Personalidad', 'Prueba_Tecnica', 'Desempeno_Real']
                if not all(col in df.columns for col in columnas_necesarias):
                    raise KeyError()
            except Exception:
                # Plan B: Leer directo desde fila 1
                df = pd.read_excel(uploaded_file, header=0)
                df.columns = df.columns.str.strip()
            
            # Limpieza de nulos
            df = df.dropna(subset=['Test_Inteligencia', 'Test_Personalidad', 'Prueba_Tecnica', 'Desempeno_Real'])
            
            X = df[['Test_Inteligencia', 'Test_Personalidad', 'Prueba_Tecnica']]
            y = df['Desempeno_Real']
            
            if len(df) < 3:
                st.error("❌ Se necesitan al menos 3 colaboradores evaluados en el archivo para ejecutar el análisis.")
            else:
                # Ejecutar Regresión
                modelo = LinearRegression()
                modelo.fit(X, y)
                
                r_cuadrado = modelo.score(X, y)
                r_xy_bateria = np.sqrt(r_cuadrado)
                
                # Impactos individuales
                coeficientes = np.abs(modelo.coef_)
                total_coef = np.sum(coeficientes)
                imp_int = (coeficientes[0] / total_coef) * 100 if total_coef > 0 else 33.3
                imp_per = (coeficientes[1] / total_coef) * 100 if total_coef > 0 else 33.3
                imp_tec = (coeficientes[2] / total_coef) * 100 if total_coef > 0 else 33.3
                
                # Guardar en la sesión web para que la pestaña 2 pueda leerlo automáticamente
                st.session_state['r_xy_calculado'] = float(r_xy_bateria)
                
                # Despliegue de Resultados Visuales en la Web (Tarjetas métricas)
                st.success("¡Análisis estadístico completado exitosamente!")
                
                col1, col2, col3 = st.columns(3)
                col1.metric(label="Colaboradores Analizados", value=len(df))
                col2.metric(label="Precisión del Modelo (R²)", value=f"{r_cuadrado:.4f}")
                col3.metric(label="VALIDEZ BATERÍA (rxy)", value=f"{r_xy_bateria:.2f}")
                
                # Diagnóstico dinámico
                if r_xy_bateria < 0.20:
                    st.warning(f"⚠️ **Diagnóstico:** Validez Baja o Inaceptable. Considere reestructurar las pruebas.")
                elif r_xy_bateria <= 0.35:
                    st.info(f"ℹ️ **Diagnóstico:** Validez Moderada/Buena. Acorde a los estándares de mercado.")
                else:
                    st.success(f"🔥 **Diagnóstico:** Validez Excelente. Alta precisión para predecir el desempeño.")
                
                # Gráfico/Bloque de impacto relativo
                st.subheader("💡 Peso Relativo de cada Test en el Desempeño:")
                st.progress(int(imp_int), text=f"Test Inteligencia: {imp_int:.1f}%")
                st.progress(int(imp_per), text=f"Test Personalidad: {imp_per:.1f}%")
                st.progress(int(imp_tec), text=f"Prueba Técnica: {imp_tec:.1f}%")
                
                st.info("🎯 **Efecto de Restricción del Rango:** Recuerde que este coeficiente está subestimado debido a que solo se calcula con los postulantes contratados. ¡El impacto real es aún mayor!")

        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {e}. Verifique que las columnas coincidan de forma exacta.")
    else:
        st.write("Esperando carga de archivo...")

# ==========================================
# PESTAÑA 2: SIMULADOR FINANCIERO BCG
# ==========================================
with tab2:
    st.header("Simulador de Retorno de Inversión (Utility Analysis - BCG)")
    st.write("Evalúe el impacto económico en la productividad de su empresa comparando el Proceso Actual vs el Proceso Nuevo.")
    
    # Intentar jalar el rxy calculado en la Pestaña 1 como valor por defecto
    default_r2 = st.session_state.get('r_xy_calculado', 0.50)
    
    if 'r_xy_calculado' in st.session_state:
        st.info(f"✅ Se ha vinculado automáticamente la validez calculada de la pestaña anterior: **rxy = {default_r2:.2f}**")

    # Formulario con entradas web laterales (Layout de columnas)
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        st.subheader("📊 Parámetros de la Población y Puesto")
        N = st.number_input("Número de seleccionados al año (N)", value=10, min_value=1)
        T = st.number_input("Permanencia promedio en años (T)", value=2.0, min_value=0.1)
        C_actual = st.number_input("Costo de selección por postulante - Proceso Actual ($)", value=50.0)
        C_nuevo = st.number_input("Costo de selección por postulante - Proceso Nuevo ($)", value=120.0)
        
    with col_input2:
        st.subheader("📈 Parámetros de Productividad")
        salario_anual = st.number_input("Sueldo bruto anual promedio ($)", value=24000.0)
        porcentaje_sd = st.slider("Desviación estándar del desempeño (% del sueldo)", min_value=10, max_value=60, value=40)
        SD_y = salario_anual * (porcentaje_sd / 100)
        
        st.caption(f"La variabilidad de productividad estimada (SDy) es de: ${SD_y:,.2f} anuales por trabajador.")

    st.markdown("#### 🔍 Coeficientes de Selección")
    col_input3, col_input4 = st.columns(2)
    
    with col_input3:
        r1 = st.number_input("Validez del Proceso Actual (r1)", value=0.20, min_value=0.0, max_value=1.0)
        r2 = st.number_input("Validez del Proceso Nuevo (r2)", value=default_r2, min_value=0.0, max_value=1.0, help="Si subió un Excel en la pestaña 1, este valor se actualiza solo.")
        
    with col_input4:
        tasa_seleccion = st.slider("Tasa de Selección (Porcentaje de postulantes aceptados)", min_value=1, max_value=100, value=20)
        # Cálculo de la ordenada y la razón de selección (Z/SR)
        SR = tasa_seleccion / 100.0
        # Aproximación matemática rápida de la altura de la curva normal (abscisa lambda)
        from scipy.stats import norm
        phi_lambda = norm.pdf(norm.ppf(1 - SR)) if SR < 1.0 else 0.0
        Z_score_factor = phi_lambda / SR if SR > 0 else 0.0
        
        st.caption(f"Factor de exigencia del filtro (Z/SR): {Z_score_factor:.3f}")

    # --- CÁLCULO FINAL DE RENDIMIENTO BCG ---
    if st.button("💰 Calcular Retorno de Inversión (ROI)", type="primary"):
        # Ecuación de Brogden-Cronbach-Gleser
        utilidad_actual = (N * T * r1 * SD_y * Z_score_factor) - (N * (1/SR) * C_actual)
        utilidad_nueva  = (N * T * r2 * SD_y * Z_score_factor) - (N * (1/SR) * C_nuevo)
        incremento_neto = utilidad_nueva - utilidad_actual
        
        st.markdown("---")
        st.subheader("💵 Informe de Impacto Financiero")
        
        c_res1, c_res2, c_res3 = st.columns(3)
        c_res1.metric(label="Ganancia Proceso Actual", value=f"${utilidad_actual:,.2f}")
        c_res2.metric(label="Ganancia Proceso Nuevo", value=f"${utilidad_nueva:,.2f}")
        
        if incremento_neto > 0:
            c_res3.metric(label="AHORRO / INCREMENTO NETO ANUAL", value=f"${incremento_neto:,.2f}", delta=f"${incremento_neto:,.2f}")
            st.balloons()
            st.success(f"🚀 **Decisión Gerencial:** Implementar el proceso nuevo incrementará el valor patrimonial de la productividad en **${incremento_neto:,.2f}** durante el ciclo de vida de los contratados, justificando plenamente el aumento de los costos de evaluación.")
        else:
            c_res3.metric(label="DIFERENCIA NETA", value=f"${incremento_neto:,.2f}", delta=f"${incremento_neto:,.2f}", delta_color="inverse")
            st.error("⚠️ **Decisión Gerencial:** El incremento en los costos del proceso nuevo o la baja validez no justifican financieramente el cambio de estrategia.")
          
