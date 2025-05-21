import streamlit as st
import requests

st.set_page_config(page_title="Comarb +", page_icon="Cazul.png", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "login_failed" not in st.session_state:
    st.session_state.login_failed = False
if "login_success" not in st.session_state:
    st.session_state.login_success = False

st.title("🔐 Iniciar Sesión")

if not st.session_state.logged_in:
    with st.form("login_form"):
        username = st.text_input("Nombre de usuario", key="username_input")
        password = st.text_input("Contraseña", type="password", key="password_input")
        submit = st.form_submit_button("Iniciar sesión")

        if submit:
            login_url = "https://dgrgw.comarb.gob.ar/dgr/j_security_check"
            payload = {
                "j_username": username,
                "j_password": password,
                "login": "Entrar"
            }

            session = requests.Session()
            response = session.post(login_url, data=payload)

            if "Nombre de usuario o contraseña no válido" in response.text:
                st.session_state.logged_in = False
                st.session_state.login_failed = True
                st.session_state.login_success = False
            else:
                st.session_state.logged_in = True
                st.session_state.login_failed = False
                st.session_state.login_success = True
                st.session_state.session = session  # Guardamos sesión para usar luego

    if st.session_state.login_failed:
        st.error("Credenciales incorrectas. Por favor, intentar nuevamente.")

    # Si el login fue exitoso, fuera del form hacemos rerun para refrescar
    if st.session_state.login_success:
        st.session_state.login_success = False  # Reseteamos la bandera para no recargar infinitamente
        st.rerun()

else:
    st.success("✅ Inicio de sesión exitoso.")
    st.markdown("Usar el menú lateral para acceder a las demás funcionalidades.")

