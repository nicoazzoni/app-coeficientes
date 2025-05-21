import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Comarb +", page_icon="Cazul.png", layout="wide")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Por favor, iniciar sesión desde Inicio.")
    st.stop()

# Inicializamos variables si no existen
if "scraping_hecho" not in st.session_state:
    st.session_state.scraping_hecho = False
if "td_element" not in st.session_state:
    st.session_state.td_element = None
if "cuit" not in st.session_state:
    st.session_state.cuit = ""
if "año_inicio" not in st.session_state:
    st.session_state.año_inicio = 2000
if "año_final" not in st.session_state:
    st.session_state.año_final = 2025

# Mostrar inputs solo si no se hizo scraping
if not st.session_state.scraping_hecho:
    st.title("Scraping Declaraciones Juradas Anuales COMARB")
    cuit = st.text_input("Ingresar el CUIT", value=st.session_state.cuit)
    año_inicio = st.number_input("Año de inicio", min_value=2000, max_value=2025, value=st.session_state.año_inicio)
    año_final = st.number_input("Año de fin", min_value=2000, max_value=2025, value=st.session_state.año_final)


    if st.button("Ejecutar scraping"):
        st.session_state.cuit = cuit
        st.session_state.año_inicio = año_inicio
        st.session_state.año_final = año_final

        año_inicio_real = año_inicio - 1
        año_final_real = año_final - 1

        s = st.session_state.session  # Reutilizamos la sesión iniciada

        secure_url = f"https://dgrgw.comarb.gob.ar/dgr/sfrDdjjAnual.do?method=buscarAnuales&cuit={cuit}&anioDesdeStr={año_inicio_real}&anioHastaStr={año_final_real}"
        r = s.get(secure_url)
        soup = BeautifulSoup(r.text, "html.parser")
#=======================================================Obtenemos el nombre de la empresa====================================        
        td_element = soup.find_all('td', class_='hdrData')[2].text.strip()
        st.session_state.td_element = td_element
#=======================================================Hacemos el scrap de verdad ==========================================
        t_trans = soup.find('table', id='transaccion')

        if not t_trans:
            st.error("No se encontró la tabla de transacciones. Verifica los datos ingresados.")
        else:
            encabezado = t_trans.find("thead")
            encabezado2 = encabezado.find_all("a")
            titulos_encabezado = [titulo.text for titulo in encabezado2]
            titulos_encabezado.insert(0, "N_Transaccion")
    
            df = pd.DataFrame(columns=titulos_encabezado)
    
            column_data = t_trans.find_all("tr")
            for row in column_data[1:]:
                row_data = row.find_all("td")
                individual_row_data = []
                for data in row_data:
                    link = data.find("a")
                    if link and link.has_attr("href"):
                        individual_row_data.append(link["href"])
                    else:
                        individual_row_data.append(data.text)
                df.loc[len(df)] = individual_row_data
    
            df["N_Transaccion"] = df["N_Transaccion"].str.extract(r"transaccionAfip=(\d+)")
            df_copiado = df.copy()
            df_filtrado = df_copiado[df_copiado["Banco / Sucursal"] == "993 - Afip"]
            df_filtrado[['Fecha_Presen', 'N']] = df_filtrado['Anticipo'].str.split(' - ', expand=True)
            df_filtrado['N'] = pd.to_numeric(df_filtrado['N'])
            df_final = df_filtrado.loc[df_filtrado.groupby('Fecha_Presen')['N'].idxmax()]
            diccionario = df_final[['N_Transaccion', 'Fecha_Presen']].to_dict(orient='records')
    
            nombres_columnas = ["Jurisdicción","Ingresos","Coeficiente Ingresos","Gastos","Coeficiente Gastos","Coeficiente Unificado","Año"]
            df_vacio = pd.DataFrame(columns=nombres_columnas)
    
            for i, item in enumerate(diccionario, start=1):
                trans = item["N_Transaccion"]
                fecha = int(item["Fecha_Presen"]) + 1
                secure_url_2 = f"https://dgrgw.comarb.gob.ar/dgr/sfrDdjjAnual.do?transaccionAfip={trans}&method=detalleAnual"
                z = s.get(secure_url_2)
                soup_2 = BeautifulSoup(z.text, "html.parser")
                tablas = soup_2.find_all('table', id='elem')
                tabla_jur = tablas[2]
                tabla_jur2 = tabla_jur.find('tbody')
                tabla_jur3 = tabla_jur2.find_all("tr")
    
                for row in tabla_jur3:
                    row_data_2 = row.find_all("td")
                    individual_row_data_2 = [data.text for data in row_data_2]
                    individual_row_data_2.append(fecha)
                    df_vacio.loc[len(df_vacio)] = individual_row_data_2
    
            df_vacio[['N_Jur', 'Jurisdicción']] = df_vacio['Jurisdicción'].str.split(' - ', n=1, expand=True)
    
            # Guardar en session_state para que no desaparezca al cambiar de página
            st.session_state.scraping_hecho = True
            st.session_state.df_final = df_vacio
            # Calcular el año mínimo y máximo realmente disponibles en los datos scrapings
            año_min_real = int(st.session_state.df_final['Año'].min())
            año_max_real = int(st.session_state.df_final['Año'].max())
            
            # Guardarlos en session_state para usarlos en otras páginas
            st.session_state.año_min_real = año_min_real
            st.session_state.año_max_real = año_max_real
#========================================Metes un rerun para que se actualice todo=========            
        st.rerun()

#========================================================================================================================
# Mostrar resultado si ya se hizo scraping
if st.session_state.scraping_hecho:
    if st.button("🔁 Realizar un nuevo scraping"):
            st.session_state.scraping_hecho = False
            st.rerun()
        
    st.title("Scrap realizado con los siguientes datos:")
    st.markdown(f"CUIT: **{st.session_state.cuit}**")
    st.markdown(f"Contribuyente: **{st.session_state.td_element}**")
    st.markdown(f"Desde el año: **{st.session_state.año_min_real}**")
    st.markdown(f"Hasta el año: **{st.session_state.año_max_real}**")

    st.dataframe(st.session_state.df_final)

    