mport streamlit as st
import anthropic
import streamlit.components.v1 as components

# Configuración de la página
st.set_page_config(
    page_title="F.O.R.M.U.L.A. // Stark HUD",
    page_icon="⚡",
    layout="wide"
)

# Estilo visual estilo JARVIS (CSS personalizado)
st.markdown("""
    <style>
    .stApp {
        background-color: #050b14;
        color: #00f0ff;
    }
    h1, h2, h3 {
        color: #00f0ff !important;
        font-family: 'Courier New', monospace;
        letter-spacing: 2px;
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #0a192f !important;
        color: #00f0ff !important;
        border: 1px solid #00f0ff !important;
    }
    .metric-card {
        background-color: #0a192f;
        border: 1px solid #00f0ff;
        padding: 15px;
        border-radius: 5px;
        text-align: center;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Función para la síntesis de voz en el navegador
def speak(text):
    clean_text = text.replace('"', '\\"').replace("'", "\\'").replace('\n', ' ')
    js_code = f"""
    <script>
        const synth = window.speechSynthesis;
        const utterance = new SpeechSynthesisUtterance("{clean_text}");
        utterance.lang = 'es-ES';
        utterance.rate = 1.0;
        synth.speak(utterance);
    </script>
    """
    components.html(js_code, height=0)

# Validación de contraseña desde los secretos
def check_password():
    if "admin_password" not in st.secrets:
        return True
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("## ⚡ F.O.R.M.U.L.A. // ACCESO RESTRINGIDO")
            pwd = st.text_input("Ingrese código de autorización:", type="password")
            if pwd:
                if pwd == st.secrets["admin_password"]:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Código de acceso incorrecto.")
        return False
    return True

if check_password():
    # --- PANEL VISUAL ESTILO TONY STARK ---
    st.markdown("# ⚡ F.O.R.M.U.L.A. // HUD OPERATIVO")
    st.markdown("`SISTEMA PRINCIPAL: ONLINE` | `NÚCLEO: CLAUDE 3.5 SONNET` | `VOZ: ACTIVA`")
    st.markdown("---")

    # Panel de métricas e imágenes visuales
    col_img, col_m1, col_m2, col_m3 = st.columns([1.5, 1, 1, 1])

    with col_img:
        st.image("https://images.unsplash.com/photo-1508739773434-c26b3d09e071?q=80&w=600&auto=format&fit=crop", 
                 caption="DIAGNÓSTICO NÚCLEO // HUD v2.1")

    with col_m1:
        st.markdown("""
            <div class="metric-card">
                <h3>ESTADO</h3>
                <p style="color: #00ff66; font-size: 20px; font-weight: bold;">ÓPTIMO</p>
            </div>
        """, unsafe_allow_html=True)

    with col_m2:
        st.markdown("""
            <div class="metric-card">
                <h3>LATENCIA</h3>
                <p style="color: #00f0ff; font-size: 20px; font-weight: bold;">24 ms</p>
            </div>
        """, unsafe_allow_html=True)

    with col_m3:
        st.markdown("""
            <div class="metric-card">
                <h3>SEGURIDAD</h3>
                <p style="color: #00f0ff; font-size: 20px; font-weight: bold;">BLINDADO</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- NÚCLEO DE CHAT CON CLAUDE ---
    if "anthropic_api_key" in st.secrets:
        client = anthropic.Anthropic(api_key=st.secrets["anthropic_api_key"])
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Introduzca datos o directrices operativas..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                try:
                    response = client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=1500,
                        system="Eres F.O.R.M.U.L.A., una inteligencia artificial analítica de alto rendimiento con la estética, precisión y el tono sofisticado de JARVIS en las películas de Tony Stark. Respondes de forma concisa, técnica y ejecutiva en español.",
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    )
                    full_response = response.content[0].text
                    message_placeholder.markdown(full_response)
                    
                    # Llamada a la función de voz en el navegador
                    speak(full_response)
                    
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"Error en el enlace neuronal con la API: {e}")
    else:
        st.warning("Falta configurar la 'anthropic_api_key' en los secretos de Streamlit.")
