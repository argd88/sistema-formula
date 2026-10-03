import streamlit as st
import anthropic
import streamlit.components.v1 as components

st.set_page_config(
    page_title="F.O.R.M.U.L.A. // Stark HUD Central",
    page_icon="⚡",
    layout="wide"
)

# Estilo visual avanzado Stark HUD (Azul neón / Oscuro profundo)
st.markdown("""
    <style>
    .stApp {
        background-color: #030812;
        color: #00f0ff;
    }
    h1, h2, h3 {
        color: #00f0ff !important;
        font-family: 'Courier New', monospace;
        letter-spacing: 2px;
        text-align: center;
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #071325 !important;
        color: #00f0ff !important;
        border: 1px solid #00f0ff !important;
        border-radius: 4px;
    }
    .hud-card {
        background-color: #071325;
        border: 1px solid #00f0ff;
        padding: 12px;
        border-radius: 6px;
        text-align: center;
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.25);
        margin-bottom: 10px;
    }
    .hud-card h4 {
        color: #00f0ff;
        margin-bottom: 5px;
        font-size: 14px;
        font-family: 'Courier New', monospace;
    }
    .hud-card p {
        color: #ffffff;
        font-size: 16px;
        margin: 0;
        font-weight: bold;
    }
    /* Centrar barra de chat y dar espacio */
    .stChatInput {
        max-width: 800px;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# Función de Síntesis de Voz (Text-to-Speech)
def speak(text):
    clean_text = text.replace('"', '\\"').replace("'", "\\'").replace('\n', ' ')
    js_code = f"""
    <script>
        const synth = window.speechSynthesis;
        const utterance = new SpeechSynthesisUtterance("{clean_text}");
        utterance.lang = 'es-ES';
        synth.speak(utterance);
    </script>
    """
    components.html(js_code, height=0)

# Validación de seguridad
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
                    st.error("Código incorrecto.")
        return False
    return True

if check_password():
    # --- CABECERA HUD TONY STARK ---
    st.markdown("# ⚡ F.O.R.M.U.L.A. // SISTEMA CENTRAL HUD")
    st.markdown("`ESTADO: NÚCLEO ONLINE` | `ENCRIPTACIÓN: 256-BIT` | `VOZ: ACTIVA`")
    st.markdown("---")

    # --- PANELES LATERALES Y SUPERIORES (Clima, Divisas, Noticias) ---
    col_left, col_center, col_right = st.columns([1.2, 2.6, 1.2])

    with col_left:
        st.markdown("### 🌐 DIAGNÓSTICO & CLIMA")
        st.markdown("""
            <div class="hud-card">
                <h4>ESTADO DE RED</h4>
                <p style="color: #00ff66;">ÓPTIMO (18 ms)</p>
            </div>
            <div class="hud-card">
                <h4>CLIMA LOCAL</h4>
                <p>Santiago: 18°C // Despejado</p>
            </div>
            <div class="hud-card">
                <h4>NÚCLEO IA</h4>
                <p>Claude 3.5 Sonnet</p>
            </div>
        """, unsafe_allow_html=True)

    with col_center:
        st.markdown("### 💱 TASAS DE CAMBIO (DIVISAS)")
        c_usd, c_eur = st.columns(2)
        with c_usd:
            st.markdown("""
                <div class="hud-card">
                    <h4>DOLAR (USD)</h4>
                    <p>1.00 USD = 1.00 REF</p>
                </div>
            """, unsafe_allow_html=True)
        with c_eur:
            st.markdown("""
                <div class="hud-card">
                    <h4>EURO (EUR)</h4>
                    <p>1 EUR = 1.08 USD</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Indicador visual central estilo reactor/arc
        st.image("https://images.unsplash.com/photo-1508739773434-c26b3d09e071?q=80&w=700&auto=format&fit=crop", 
                 caption="HOLOGRAPHIC CORE // STARK INDUSTRIES")

    with col_right:
        st.markdown("### 📰 NOTICIAS RECIENTES")
        st.markdown("""
            <div class="hud-card" style="text-align: left; font-size: 13px;">
                <h4 style="text-align: left;">ACTUALIZACIONES GLOBAL</h4>
                <p style="font-size: 12px; color: #a5f3fc;">• Redes neurales optimizadas al 100%.</p>
                <p style="font-size: 12px; color: #a5f3fc; margin-top: 5px;">• Protocolos de seguridad blindados activos.</p>
                <p style="font-size: 12px; color: #a5f3fc; margin-top: 5px;">• Sincronización orbital completada.</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- SECCIÓN DE DIÁLOGO CENTRAL Y RECONOCIMIENTO DE VOZ ---
    st.markdown("### 💬 CONSOLA DE DIÁLOGO OPERATIVO")

    # Botón interactivo de voz por navegador (Speech Recognition)
    st.markdown("""
        <div style="text-align: center; margin-bottom: 10px;">
            <button onclick="startListening()" style="background-color: #0a192f; color: #00f0ff; border: 1px solid #00f0ff; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-family: 'Courier New'; font-weight: bold;">
                🎙️ ACTIVAR MICRÓFONO DE VOZ
            </button>
        </div>
        <script>
            function startListening() {{
                const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = 'es-ES';
                recognition.start();
                recognition.onresult = function(event) {{
                    const speechToText = event.results[0][0].transcript;
                    const chatInput = document.querySelector('textarea[aria-label*="chat"]');
                    if (chatInput) {{
                        chatInput.value = speechToText;
                        chatInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                }}
            }}
        </script>
    """, unsafe_allow_html=True)

    # Núcleo de chat con Anthropic
    if "anthropic_api_key" in st.secrets:
        client = anthropic.Anthropic(api_key=st.secrets["anthropic_api_key"])
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Introduzca directrices operativas a F.O.R.M.U.L.A...."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                try:
                    response = client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=1500,
                        system="Eres F.O.R.M.U.L.A., una inteligencia artificial de máxima categoría con la estética, precisión y tono sofisticado de JARVIS en las películas de Tony Stark. Respondes de forma técnica, ejecutiva y concisa en español.",
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    )
                    full_response = response.content[0].text
                    message_placeholder.markdown(full_response)
                    
                    # Ejecutar voz alta nativa
                    speak(full_response)
                    
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"Error en el núcleo neuronal: {e}")
    else:
        st.warning("Falta configurar la 'anthropic_api_key' en los secretos de Streamlit.")
