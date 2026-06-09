# --- DESPLIEGUE DEL REPORTE ECONÓMICO Y GRÁFICO (REPORTE CON DESPLAZAMIENTO) ---
if st.session_state['calculado']:
    import plotly.graph_objects as go
    
    u_act = st.session_state['u_actual_res']
    u_nov = st.session_state['u_nuevo_res']
    c_act = st.session_state['c_unitario_act']
    c_nov = st.session_state['c_unitario_nov']
    
    utilidad_incremental = u_nov - u_act
    por_empleado_ano = utilidad_incremental / (N * T) if (N * T) > 0 else 0.0

    # Escala en Millones/Miles de Pesos para el gráfico ($ M)
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
        # fixedrange=False permite que el usuario estire, encoja o mueva el eje horizontal libremente
        xaxis=dict(showgrid=True, gridcolor='LightGray', gridwidth=0.5, fixedrange=False),
        # fixedrange=False permite el desplazamiento y paneo vertical si las barras exceden la pantalla
        yaxis=dict(autorange="reversed", fixedrange=False), 
        plot_bgcolor='white',
        margin=dict(l=120, r=60, t=50, b=50),
        height=380,
        # Activamos la herramienta de "Pan" (Desplazamiento manual/arrastrar de la mano) por defecto
        dragmode='pan'
    )

    # REGLA CLAVE: Pasamos la configuración 'config' a Streamlit para activar las barras y scrolls interactivos
    st.plotly_chart(
        fig, 
        use_container_width=True,
        config={
            'scrollZoom': True,          # Activa el scroll o pellizco táctil para zoom/desplazamiento continuo
            'displayModeBar': True,      # Muestra la barra de herramientas superior (Lupa, Mano de paneo, Reset)
            'modeBarButtonsToRemove': [], # Mantiene todos los botones interactivos visibles
            'editable': False
        }
    )
    
    st.markdown("---")

    # Bloque de texto analítico (permanece abajo del gráfico interactivo)
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
