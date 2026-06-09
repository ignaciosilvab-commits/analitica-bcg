# ==========================================
# SECCIÓN: ACCIONES Y RESULTADOS FINALES CON GRÁFICO DE BARRAS
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

st.markdown("---")

if 'calculado' not in st.session_state:
    st.session_state['calculado'] = False

# --- DESPLIEGUE DEL REPORTE CON GRÁFICO ---
if st.session_state['calculado']:
    import plotly.graph_objects as go
    
    u_act = st.session_state['u_actual_res']
    u_nov = st.session_state['u_nuevo_res']
    c_act = st.session_state['c_unitario_act']
    c_nov = st.session_state['c_unitario_nov']
    
    utilidad_incremental = u_nov - u_act
    por_empleado_ano = utilidad_incremental / (N * T) if (N * T) > 0 else 0.0

    # 1. CONSTRUCCIÓN DEL GRÁFICO DE BARRAS HORIZONTALES (IDÉNTICO A LA CAPTURA)
    # Convertimos los valores brutos a "Miles de Pesos" dividiendo por 1,000,000 para la escala $ M
    val_act_m = u_act / 1000000
    val_nov_m = u_nov / 1000000
    val_inc_m = utilidad_incremental / 1000000

    categorias = ['Proceso Actual', 'Nuevo Proceso', 'DIFERENCIA NETAS']
    valores_m = [val_act_m, val_nov_m, val_inc_m]
    
    # Textos exactos que van al lado de la barra con formato $ y sufijo M
    textos_barra = [f"${u_act:,.1f}M", f"${u_nov:,.1f}M", f"${utilidad_incremental:,.1f}M"]
    colores_barra = ['#94a3b8', '#1f77b4', '#2ca02c'] # Gris, Azul, Verde

    fig = go.Figure(go.Bar(
        x=valores_m,
        y=categorias,
        orientation='h',
        text=textos_barra,
        textposition='outside', # Forzar que el texto aparezca fuera de la barra
        marker_color=colores_barra,
        hovertemplate="<b>%{y}</b><br>Valor: %{text}<extra></extra>"
    ))

    fig.update_layout(
        title=f"<b>Comparativa y Diferencia - {nombre_cargo}</b>",
        title_x=0.5, # Centrar el título del gráfico
        xaxis_title="Miles de Pesos ($ M)",
        xaxis=dict(showgrid=True, gridcolor='LightGray', gridwidth=0.5),
        yaxis=dict(autorange="reversed"), # Invierte el orden para que "Proceso Actual" quede abajo
        plot_bgcolor='white',
        margin=dict(l=120, r=60, t=50, b=50),
        height=400
    )

    # Renderizar el gráfico de Plotly de forma responsiva en la app web
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")

    # 2. BLOQUE DE TEXTO DEL INFORME (ABAJO DEL GRÁFICO)
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
