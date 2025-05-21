import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Comarb +", page_icon="Cazul.png", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Por favor, iniciar sesión desde Inicio.")
    st.warning("Además, debe realizar el scraping para obtener los datos.")
elif "scraping_hecho" not in st.session_state or not st.session_state.scraping_hecho:
    st.success("Sesión iniciada correctamente.")
    st.warning("Aún no se realizó el scraping. Por favor, hazlo en Scraping.")
else:  
    st.title("Gráficos - Coeficiente de Ingresos y Gastos")
    st.markdown(f"Graficando valores para: **{st.session_state.td_element}** desde **{st.session_state.año_min_real}** hasta **{st.session_state.año_max_real}**.")

    df_vacio = st.session_state.df_final.copy()
    
#=======================================================GRAFICO 1=========================================
    
    # 2. Obtener lista de provincias disponibles para ese CUIT y ordenar alfabéticamente
    lista_provincias = df_vacio['Jurisdicción'].unique().tolist()
    lista_provincias.sort()
    
    # 3. Selectbox para elegir la provincia
    
    provincia_seleccionada = st.selectbox("Seleccione la provincia", lista_provincias)

#=========================================================================================================

    st.markdown("""
    <style>
    .legend-container {
        display: flex;
        flex-direction: row;
        gap: 20px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: bold;  /* texto en negrita */
    }
    .circle {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        display: inline-block;
    }
    </style>
    
    <div class="legend-container">
        <div class="legend-item">
            <span class="circle" style="background-color: black;"></span>
            <span>Coeficiente Unificado</span>
        </div>
        <div class="legend-item">
            <span class="circle" style="background-color: green;"></span>
            <span>Coeficiente de Ingresos</span>
        </div>
        <div class="legend-item">
            <span class="circle" style="background-color: red;"></span>
            <span>Coeficiente de Gastos</span>
        </div>
    </div>
""", unsafe_allow_html=True)

#================================================================================================
    
    # 4. Filtrar dataframe por la provincia seleccionada
    df_provincia = df_vacio[df_vacio['Jurisdicción'] == provincia_seleccionada].copy()
    
    # 5. Convertir columnas a numérico
    df_provincia['Coeficiente Unificado'] = df_provincia['Coeficiente Unificado'].astype(str).str.replace(',', '.', regex=False).astype(float)
    df_provincia['Coeficiente de Gastos'] = df_provincia['Coeficiente Gastos'].astype(str).str.replace(',', '.', regex=False).astype(float)
    df_provincia['Coeficiente de Ingresos'] = df_provincia['Coeficiente Ingresos'].astype(str).str.replace(',', '.', regex=False).astype(float)
    
    # 6. Convertir años a texto para eje X
    df_provincia['Año_str'] = df_provincia['Año'].astype(str)
    
    # 7. Crear gráfico con Plotly
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_provincia['Año_str'],
        y=df_provincia['Coeficiente Unificado'],
        name='Coeficiente Unificado',
        mode='lines+markers',
        line=dict(width=4, color='black'),
        marker=dict(size=10, symbol='circle'),
        hovertemplate='<b>Año:</b> %{x}<br><b>Coef. Unificado:</b> %{y:.3f}<extra></extra>',
    ))
    
    fig.add_trace(go.Scatter(
        x=df_provincia['Año_str'],
        y=df_provincia['Coeficiente de Gastos'],
        name='Coeficiente de Gastos',
        mode='lines+markers',
        line=dict(width=4, color='red'),
        marker=dict(size=10, symbol='circle'),
        hovertemplate='<b>Año:</b> %{x}<br><b>Coef. Gastos:</b> %{y:.3f}<extra></extra>',
    ))
    
    fig.add_trace(go.Scatter(
        x=df_provincia['Año_str'],
        y=df_provincia['Coeficiente de Ingresos'],
        name='Coeficiente de Ingresos',
        mode='lines+markers',
        line=dict(width=4, color='green'),
        marker=dict(size=10, symbol='circle'),
        hovertemplate='<b>Año:</b> %{x}<br><b>Coef. Ingresos:</b> %{y:.3f}<extra></extra>',
    ))
    
    fig.update_layout(
        showlegend=False,
        height=500,
        font=dict(family="Verdana", size=14, color="black"),
        xaxis=dict(
            title='Año',
            type='category',
            tickangle=0,
        ),
        yaxis=dict(
            title='Coeficiente',
            tick0=0,
            dtick=0.05,
            range=[0, 1],
            autorange=True,
        ),
        title=f'Coeficientes - {provincia_seleccionada}',
        template='plotly_white',
        hovermode='closest',
    )
    
    # 8. Mostrar gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)

#======================================================GRAFICO 2======================================================
    # Ordenar por año
    df_provincia = df_provincia.sort_values('Año')
    
    # Calcular diferencias año a año
    df_provincia['Dif Coeficiente Unificado'] = df_provincia['Coeficiente Unificado'].diff()
    df_provincia['Dif Coeficiente de Gastos'] = df_provincia['Coeficiente de Gastos'].diff()
    df_provincia['Dif Coeficiente de Ingresos'] = df_provincia['Coeficiente de Ingresos'].diff()
    
    # Convertir años a texto para eje X
    df_provincia['Año_str'] = df_provincia['Año'].astype(str)
    
    # Crear gráfico diferencias año a año
    fig_diff = go.Figure()
    
    fig_diff.add_trace(go.Scatter(
        x=df_provincia['Año_str'],
        y=df_provincia['Dif Coeficiente Unificado'],
        name='Dif Coeficiente Unificado',
        mode='lines+markers',
        line=dict(width=4, color='black'),
        marker=dict(size=10, symbol='circle'),
        hovertemplate='<b>Año:</b> %{x}<br><b>Dif. Unificado:</b> %{y:.3f}<extra></extra>',
    ))
    
    fig_diff.add_trace(go.Scatter(
        x=df_provincia['Año_str'],
        y=df_provincia['Dif Coeficiente de Gastos'],
        name='Dif Coeficiente de Gastos',
        mode='lines+markers',
        line=dict(width=4, color='red'),
        marker=dict(size=10, symbol='circle'),
        hovertemplate='<b>Año:</b> %{x}<br><b>Dif. Gastos:</b> %{y:.3f}<extra></extra>',
    ))
    
    fig_diff.add_trace(go.Scatter(
        x=df_provincia['Año_str'],
        y=df_provincia['Dif Coeficiente de Ingresos'],
        name='Dif Coeficiente de Ingresos',
        mode='lines+markers',
        line=dict(width=4, color='green'),
        marker=dict(size=10, symbol='circle'),
        hovertemplate='<b>Año:</b> %{x}<br><b>Dif. Ingresos:</b> %{y:.3f}<extra></extra>',
    ))
    
    fig_diff.update_layout(
        showlegend=False,
        height=500,
        font=dict(family="Verdana", size=14, color="black"),
        xaxis=dict(
            title='Año',
            type='category',
            tickangle=0,
        ),
        yaxis=dict(
            title='Diferencia',
            zeroline=True,
            zerolinecolor='gray',
            zerolinewidth=2,
        ),
        title=f'Diferencia Año a Año - {provincia_seleccionada}',
        template='plotly_white',
        hovermode='closest',
    )
    
    st.plotly_chart(fig_diff, use_container_width=True)


#=========================================GRAFICO 3==========================================

    # 4. Calcular variación porcentual
    df_provincia = df_provincia.sort_values('Año')
    df_provincia['Var % Coeficiente Unificado'] = df_provincia['Coeficiente Unificado'].pct_change() * 100
    df_provincia['Var % Coeficiente de Gastos'] = df_provincia['Coeficiente de Gastos'].pct_change() * 100
    df_provincia['Var % Coeficiente de Ingresos'] = df_provincia['Coeficiente de Ingresos'].pct_change() * 100
    
    # 5. Crear gráfico con Plotly
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_provincia['Año_str'],
        y=df_provincia['Var % Coeficiente Unificado'],
        name='Coeficiente Unificado',
        mode='lines+markers',
        line=dict(width=4, color='black'),
        marker=dict(size=10, symbol='circle'),
        hovertemplate='<b>Año:</b> %{x}<br><b>Var(%) Unificado:</b> %{y:.0f} %<extra></extra>',
    ))
    
    fig.add_trace(go.Scatter(
        x=df_provincia['Año_str'],
        y=df_provincia['Var % Coeficiente de Gastos'],
        name='Coeficiente de Gastos',
        mode='lines+markers',
        line=dict(width=4, color='red'),
        marker=dict(size=10, symbol='circle'),
        hovertemplate='<b>Año:</b> %{x}<br><b>Var(%) Gastos:</b> %{y:.0f} %<extra></extra>',
    ))
    
    fig.add_trace(go.Scatter(
        x=df_provincia['Año_str'],
        y=df_provincia['Var % Coeficiente de Ingresos'],
        name='Coeficiente de Ingresos',
        mode='lines+markers',
        line=dict(width=4, color='green'),
        marker=dict(size=10, symbol='circle'),
        hovertemplate='<b>Año:</b> %{x}<br><b>Var(%) Ingresos:</b> %{y:.0f} %<extra></extra>',
    ))
    
    fig.update_layout(
        showlegend=False,
        height=500,
        font=dict(family="Verdana", size=14, color="black"),
        xaxis=dict(title='Año', type='category'),
        yaxis=dict(
                title='Var(%)',
                zeroline=True,
                zerolinecolor='gray',
                zerolinewidth=2,
            ),
        title=f'Variación Porcentual Año a Año - {provincia_seleccionada}',
        template='plotly_white',
        hovermode='closest',
    )

    # 6. Mostrar gráfico
    st.plotly_chart(fig, use_container_width=True)

#===========================================================GRAFICO 4===================================================
    df_provincia = df_provincia.sort_values('Año')
    # 6. Calcular índice base 100
    base_unificado = df_provincia['Coeficiente Unificado'].iloc[0]
    base_gastos = df_provincia['Coeficiente de Gastos'].iloc[0]
    base_ingresos = df_provincia['Coeficiente de Ingresos'].iloc[0]
    
    df_provincia['Índice Unificado'] = df_provincia['Coeficiente Unificado'] / base_unificado * 100
    df_provincia['Índice Gastos'] = df_provincia['Coeficiente de Gastos'] / base_gastos * 100
    df_provincia['Índice Ingresos'] = df_provincia['Coeficiente de Ingresos'] / base_ingresos * 100
    
    # 7. Crear gráfico con Plotly
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_provincia['Año_str'],
        y=df_provincia['Índice Unificado'],
        name='Coeficiente Unificado',
        mode='lines+markers',
        line=dict(width=4, color='black'),
        marker=dict(size=10),
        hovertemplate='<b>Año:</b> %{x}<br><b>Índice Unificado:</b> %{y:.0f}<extra></extra>',
    ))
    
    fig.add_trace(go.Scatter(
        x=df_provincia['Año_str'],
        y=df_provincia['Índice Gastos'],
        name='Coeficiente de Gastos',
        mode='lines+markers',
        line=dict(width=4, color='red'),
        marker=dict(size=10),
        hovertemplate='<b>Año:</b> %{x}<br><b>Índice Gastos:</b> %{y:.0f}<extra></extra>',
    ))
    
    fig.add_trace(go.Scatter(
        x=df_provincia['Año_str'],
        y=df_provincia['Índice Ingresos'],
        name='Coeficiente de Ingresos',
        mode='lines+markers',
        line=dict(width=4, color='green'),
        marker=dict(size=10),
        hovertemplate='<b>Año:</b> %{x}<br><b>Índice Ingresos:</b> %{y:.0f}<extra></extra>',
    ))
    
    fig.update_layout(
        title=f'Índice base 100 (Año base = {st.session_state.año_min_real}) - {provincia_seleccionada}',
        xaxis_title='Año',
        yaxis_title='Índice (Base 100)',
        yaxis=dict(tick0=0, dtick=10, autorange=True),
        template='plotly_white',
        font=dict(family="Verdana", size=14, color="black"),
        height=500,
        hovermode='closest',
        showlegend=False,
        shapes=[
            dict(
                type='line',
                y0=100, y1=100,
                xref='paper', x0=0,
                x1=1,
                line=dict(color='gray', width=2, dash='solid'),
            )
        ],
    )
    
    # 8. Mostrar gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)

