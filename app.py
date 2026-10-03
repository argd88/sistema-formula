import streamlit as st
import anthropic
import streamlit.components.v1 as components

# Configuración de la página HUD
st.set_page_config(
    page_title="F.O.R.M.U.L.A.",
    page_icon="⚡",
    layout="wide"
)

# Estilo visual avanzado estilo Stark HUD / JARVIS
st.markdown("""
    <style>
    .stApp {
        background-color: #030712;
        color: #00f0ff;
        font-family: 'Courier New', Courier, monospace;
    }
    h1, h2, h3 {
        color: #00f0ff !important;
        letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.4);
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #051124 !important;
        color: #00f0ff !important;
        border: 1px solid #00f0ff !important;
        box-shadow: inset 0 0 8px rgba(0, 240, 255, 0.2);
    }
    .hud-panel {
        background-color: #051124;
        border: 1px solid #00f0ff;
        padding: 12px;
        border-radius: 4px;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);
        margin-bottom: 10px;
    }
    .hud-title {
        font-size: 11px;
        color: #60a5fa;
        text-transform: uppercase;
        border-bottom: 1px solid #1e3a8a;
        padding-bottom: 4px;
        margin-bottom: 8px;
        letter-spacing: 1px;
    }
    </style>
""", unsafe_allow_html=True)

# Función de síntesis de voz (IA habla)
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

# Validación de seguridad de acceso
def check_password():
    if "admin_password" not in st.secrets:
        return True
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("## ⚡ F.O.R.M.U.L.A. // ACCESO RESTRINGIDO")
            pwd = st.text_input("Credencial de autorización:", type="password")
            if pwd:
                if pwd == st.secrets["admin_password"]:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Credencial inválida.")
        return False
    return True

if check_password():
    # Cabecera principal estilo HUD
    st.markdown("<h1 style='text-align: center;'>⚡ F.O.R.M.U.L.A.>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #60a5fa; font-size: 12px;'>SISTEMA CENTRAL: ONLINE | NÚCLEO: CLAUDE 3.5 SONNET | ENLACE NEURONAL ACTIVO</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Layout de 3 columnas estilo interfaz Stark (Paneles laterales + Núcleo Central)
    col_left, col_center, col_right = st.columns([1.2, 2.6, 1.2])

    # --- PANEL IZQUIERDO: Clima & Divisas ---
    with col_left:
        st.markdown("""
            <div class="hud-panel">
                <div class="hud-title">🌤️ Indicador Meteorológico</div>
                <p style="font-size: 18px; font-weight: bold; margin: 0;">SANTIAGO: 18°C</p>
                <p style="font-size: 11px; color: #93c5fd; margin: 0;">Condición: Cielo despejado / Óptimo</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="hud-panel">
                <div class="hud-title">💱 Tasas de Cambio Global</div>
                <p style="font-size: 13px; margin: 4px 0;"><b>USD / CLP:</b> $925.50</p>
                <p style="font-size: 13px; margin: 4px 0;"><b>EUR / CLP:</b> $988.20</p>
                <p style="font-size: 10px; color: #60a5fa; margin: 2px 0;">Actualización de mercado en vivo</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="hud-panel">
                <div class="hud-title">📊 Diagnóstico de Núcleo</div>
                <p style="font-size: 12px; margin: 2px 0;">CPU: 14% | RAM: 32%</p>
                <p style="font-size: 12px; margin: 2px 0;">Latencia Red: 18 ms</p>
                <p style="font-size: 12px; margin: 2px 0;">Seguridad: Blindado (SSL)</p>
            </div>
        """, unsafe_allow_html=True)

    # --- PANEL CENTRAL: Cuadro de Diálogo Principal ---
    with col_center:
        st.markdown("""
            <div class="hud-panel" style="text-align: center; border: 1px solid #00f0ff;">
                <div class="hud-title">💬 NÚCLEO DE DIÁLOGO OPERATIVO (CENTRAL)</div>
            </div>
        """, unsafe_allow_html=True)

        if "anthropic_api_key" in st.secrets:
            client = anthropic.Anthropic(api_key=st.secrets["anthropic_api_key"])
            
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # Contenedor del historial de chat en el centro
            chat_container = st.container()
            with chat_container:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            # Entrada de comandos en el centro
            if prompt := st.chat_input("Introduzca directrices operativas o hable con el sistema..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    try:
                        response = client.messages.create(
                            model="claude-3-5-sonnet-20241022",
                            max_tokens=1500,
                            system="Eres F.O.R.M.U.L.A., una inteligencia artificial analítica avanzada con la estética, precisión y el tono sofisticado de JARVIS en las películas de Tony Stark. Respondes de forma concisa, técnica y ejecutiva en español.",
                            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                        )
                        full_response = response.content[0].text
                        message_placeholder.markdown(full_response)
                        
                        # Ejecuta la voz sintética
                        speak(full_response)
                        
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                    except Exception as e:
                        st.error(f"Error de enlace con el núcleo: {e}")
        else:
            st.warning("Falta configurar la clave de Anthropic en los secretos.")

    # --- PANEL DERECHO: Sección de Noticias y Actividad ---
    with col_right:
        st.markdown("""
            <div class="hud-panel">
                <div class="hud-title">📰 Feed de Noticias Globales</div>
                <p style="font-size: 11px; margin-bottom: 6px;">• <b>Tech:</b> Avances récord en procesamiento de IA cuántica.</p>
                <p style="font-size: 11px; margin-bottom: 6px;">• <b>Mercados:</b> Wall Street abre con tendencia alcista.</p>
                <p style="font-size: 11px; margin-bottom: 6px;">• <b>Logística:</b> Optimización de cadenas de suministro globales activa.</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="hud-panel">
                <div class="hud-title">🎙️ Interacción por Voz</div>
                <p style="font-size: 11px; color: #93c5fd;">El sistema cuenta con sintonizador de voz activo. Cada respuesta del núcleo será transmitida por audio nativo.</p>
            </div>
        """, unsafe_allow_html=True)
