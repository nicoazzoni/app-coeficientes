import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Comarb +", page_icon="Cazul.png", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Por favor, iniciar sesión desde Inicio.")
    st.warning("Además, debe realizar el scraping para obtener los datos.")
#elif "df_final" not in st.session_state:
elif "scraping_hecho" not in st.session_state or not st.session_state.scraping_hecho:
    st.success("Sesión iniciada correctamente.")
    st.warning("Aún no se realizó el scraping. Por favor, hazlo en Scraping.")
else:  
    st.title("Gráficos - Coeficiente Unificado por Provincia")
    st.markdown(f"Graficando valores para: **{st.session_state.td_element}** desde **{st.session_state.año_min_real}** hasta **{st.session_state.año_max_real}**.")

    df_vacio = st.session_state.df_final.copy()

#========================================================GRAFICO 1==============================================    
    # Asegurarse de que los valores sean numéricos
    df_vacio['Coeficiente Unificado'] = (
        df_vacio['Coeficiente Unificado']
        .astype(str)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )
    
    # Ordenar los años como texto para el eje X
    df_vacio['Año_str'] = df_vacio['Año'].astype(str)
    
    # Paleta de colores
    #colors = px.colors.qualitative.Set1
    colors = px.colors.qualitative.D3 + px.colors.qualitative.Set1 + px.colors.qualitative.G10 

    
    # Crear figura
    fig = go.Figure()
    
    # Crear una línea por jurisdicción
    # Determinar el último año disponible
    ultimo_año = df_vacio['Año'].max()
    
    # Calcular los valores del coeficiente por jurisdicción para ese año
    valores_ultimo_año = (
        df_vacio[df_vacio['Año'] == ultimo_año]
        .groupby('Jurisdicción')['Coeficiente Unificado']
        .mean()
        .sort_values(ascending=False)
    )
    
    # Ordenar las jurisdicciones por ese valor
    jurisdicciones = valores_ultimo_año.index.tolist()
    
    for i, jurisdiccion in enumerate(jurisdicciones):
        df_filtrado = df_vacio[df_vacio['Jurisdicción'] == jurisdiccion]
        fig.add_trace(go.Scatter(
            x=df_filtrado['Año_str'],
            y=df_filtrado['Coeficiente Unificado'],
            name=jurisdiccion,
            mode='lines+markers',
            line=dict(width=4, color=colors[i % len(colors)]),
            marker=dict(size=10, symbol='circle'),
            hovertemplate='<b>Año:</b> %{x}<br><b>Coef. Unificado:</b> %{y:.3f}<br><b>%{fullData.name}</b><extra></extra>',
        ))
    
    # Configuración del gráfico
    fig.update_layout(
        height=500,
        font=dict(family="Verdana", size=14, color="black"),
        xaxis=dict(
            title='Año',
            type='category',
            tickangle=0,
        ),
        yaxis=dict(
            title='Coeficiente Unificado',
            tick0=0,
            dtick=0.05,
            range=[0, 1],
            autorange=True,
            zeroline=True,
        zerolinewidth=2,
        zerolinecolor='gray'
        ),
        title='Coeficiente Unificado por Provincia',
        template='plotly_white',
        hovermode='closest',
        #legend=dict(
        #font=dict(size=9))
    )
    
    st.plotly_chart(fig, use_container_width=True)
#=========================================================GRAFICCO 2=====================================================
    df_vacio['Diferencia'] = (
        df_vacio
        .sort_values(['Jurisdicción', 'Año'])
        .groupby('Jurisdicción')['Coeficiente Unificado']
        .diff()
    )

    # Crear figura para diferencias año a año
    fig2 = go.Figure()
    
    for i, jurisdiccion in enumerate(jurisdicciones):
        df_filtrado = df_vacio[df_vacio['Jurisdicción'] == jurisdiccion]
        fig2.add_trace(go.Scatter(
            x=df_filtrado['Año_str'],
            y=df_filtrado['Diferencia'],
            name=jurisdiccion,
            mode='lines+markers',
            line=dict(width=4, color=colors[i % len(colors)]),
            marker=dict(size=10, symbol='circle'),
            hovertemplate='<b>Año:</b> %{x}<br><b>Diferencia:</b> %{y:.3f}<br><b>%{fullData.name}</b><extra></extra>',
        ))
    
    fig2.update_layout(
        height=500,
        font=dict(family="Verdana", size=14, color="black"),
        xaxis=dict(title='Año', type='category'),
        yaxis=dict(
            title='Coeficiente Unificado - Diferencia',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='gray',
        ),
        title='Coeficiente Unificado - Diferencia Año a Año',
        template='plotly_white',
        hovermode='closest',
     )

    
    st.plotly_chart(fig2, use_container_width=True)

#============================================================GRAFICO 3=======================================
           # Calcular diferencia porcentual año a año por jurisdicción
    df_vacio['Diferencia_Porcentual'] = (
        df_vacio
        .sort_values(['Jurisdicción', 'Año'])
        .groupby('Jurisdicción')['Coeficiente Unificado']
        .pct_change()
    ) * 100  # multiplicar por 100 para obtener porcentaje
    
    # Crear figura para diferencia porcentual
    fig3 = go.Figure()
    
    for i, jurisdiccion in enumerate(jurisdicciones):
        df_filtrado = df_vacio[df_vacio['Jurisdicción'] == jurisdiccion]
        fig3.add_trace(go.Scatter(
            x=df_filtrado['Año_str'],
            y=df_filtrado['Diferencia_Porcentual'],
            name=jurisdiccion,
            mode='lines+markers',
            line=dict(width=4, color=colors[i % len(colors)]),
            marker=dict(size=10, symbol='circle'),
            hovertemplate='<b>Año:</b> %{x}<br><b>Variación:</b> %{y:.0f}%<br><b>%{fullData.name}</b><extra></extra>',
        ))
    
    fig3.update_layout(
        height=500,
        font=dict(family="Verdana", size=14, color="black"),
        xaxis=dict(title='Año', type='category'),
        yaxis=dict(
            title='Var(%)',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='gray',
            tickformat=".0f%"
        ),
        title='Coeficiente Unificado - Variación Porcentual Año a Año',
        template='plotly_white',
        hovermode='closest',
    )
    
    st.plotly_chart(fig3, use_container_width=True)

#====================================================GRAFICO 4=============================================
    # Calcular índice base 100
    df_vacio = df_vacio.sort_values(['Jurisdicción', 'Año'])
    df_vacio['Base'] = df_vacio.groupby('Jurisdicción')['Coeficiente Unificado'].transform('first')
    df_vacio['Indice Base 100'] = (df_vacio['Coeficiente Unificado'] / df_vacio['Base']) * 100
    
    # Crear figura para índice base 100
    fig4 = go.Figure()
    
    for i, jurisdiccion in enumerate(jurisdicciones):
        df_filtrado = df_vacio[df_vacio['Jurisdicción'] == jurisdiccion]
        fig4.add_trace(go.Scatter(
            x=df_filtrado['Año_str'],
            y=df_filtrado['Indice Base 100'],
            name=jurisdiccion,
            mode='lines+markers',
            line=dict(width=4, color=colors[i % len(colors)]),
            marker=dict(size=10, symbol='circle'),
            hovertemplate='<b>Año:</b> %{x}<br><b>Índice Base 100:</b> %{y:.0f}<br><b>%{fullData.name}</b><extra></extra>',
        ))
    
    fig4.update_layout(
        height=500,
        font=dict(family="Verdana", size=14, color="black"),
        xaxis=dict(title='Año', type='category'),
        yaxis=dict(title='Índice Base 100'),
        shapes=[
            dict(
                type='line',
                y0=100, y1=100,
                xref='paper', x0=0,
                x1=1,
                line=dict(color='gray', width=2, dash='solid'),
            )
        ],
        title=f"Coeficiente Unificado - Índice base 100 (Año base = {st.session_state.año_min_real})",
        template='plotly_white',
        hovermode='closest',
    )
    
    st.plotly_chart(fig4, use_container_width=True)