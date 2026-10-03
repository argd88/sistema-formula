import streamlit as st
from anthropic import Anthropic

# 1. Configuración visual
st.set_page_config(page_title="F.O.R.M.U.L.A. // Central", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: #00e5ff; font-family: 'Courier New', Courier, monospace; }
    .stChatMessage { border-left: 2px solid #00e5ff; background-color: rgba(0, 229, 255, 0.05); }
    </style>
""", unsafe_allow_html=True)

# 2. Control de acceso
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["admin_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("F.O.R.M.U.L.A. // ACCESO RESTRINGIDO")
        st.text_input("Ingrese código de autorización:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("ACCESO DENEGADO")
        st.text_input("Código incorrecto. Reintente:", type="password", on_change=password_entered, key="password")
        st.error("Protocolo de seguridad en alerta.")
        return False
    return True

# 3. Terminal operativa
if check_password():
    st.title("F.O.R.M.U.L.A. // TERMINAL OPERATIVA")
    st.caption("Protocolos activos. Conexión segura lista.")

    client = Anthropic(api_key=st.secrets["anthropic_api_key"])

    SYSTEM_PROMPT = """
    Eres F.O.R.M.U.L.A., un sistema de inteligencia artificial configurado como Controlador de Gestión y Analista Comercial.
    - Tono: Formal, pulcro, educado y con sutil ironía británica. Tratas a la usuaria de 'Señora'.
    - Estructura: Tablas ejecutivas, listas concisas o fórmulas/scripts listos para copiar.
    - Especialidad: Control de gestión, operaciones multitienda, costeo y métricas de rentabilidad.
    """

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Introduzca datos o directrices operativas..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            reply_text = response.content[0].text
            with st.chat_message("assistant"):
                st.markdown(reply_text)
            st.session_state.messages.append({"role": "assistant", "content": reply_text})
        except Exception as e:
            st.error(f"Error de enlace: {e}")
