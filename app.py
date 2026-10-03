import json
import re

import streamlit as st
import anthropic
import streamlit.components.v1 as components
from streamlit_mic_recorder import speech_to_text

MODEL = "claude-sonnet-5-5"

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

    /* Mensajes del chat: fondo claro con texto negro */
    [data-testid="stChatMessage"] {
        background-color: #e6fbff !important;
        border: 1px solid #00f0ff;
        border-radius: 6px;
    }
    [data-testid="stChatMessage"] * {
        color: #000000 !important;
    }

    /* Caja donde se escribe: texto negro */
    [data-testid="stChatInput"] textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #555555 !important;
    }
    </style>
""", unsafe_allow_html=True)


# Función de síntesis de voz (IA habla) con voz masculina de español latino
def speak(text):
    # Quita símbolos de markdown para que no se lean en voz alta
    clean_text = re.sub(r"[*_#`>\[\]]", "", text).replace("\n", " ")
    # json.dumps escapa comillas, barras y saltos de línea de forma segura para JS
    js_text = json.dumps(clean_text)
    js_code = f"""
    <script>
        let synth;
        try {{ synth = window.parent.speechSynthesis; }} catch (e) {{ synth = window.speechSynthesis; }}
        if (!synth) {{ synth = window.speechSynthesis; }}

        // Variantes de español de Latinoamérica
        const LATAM = ['es-mx', 'es-us', 'es-419', 'es-ar', 'es-co', 'es-cl', 'es-pe', 'es-ve'];
        // Nombres de voces masculinas habituales (Windows/Edge, macOS/iOS, Android)
        const MASCULINA = /(jorge|juan|diego|carlos|pablo|ra[uú]l|andr[eé]s|gonzalo|enrique|alonso|tom[aá]s|gerardo|lorenzo|male|hombre|masculin)/i;

        function elegirVoz(voces) {{
            const lang = v => v.lang.replace('_', '-').toLowerCase();
            const es = voces.filter(v => lang(v).startsWith('es'));
            const latam = es.filter(v => LATAM.includes(lang(v)));
            return latam.find(v => MASCULINA.test(v.name))
                || es.find(v => MASCULINA.test(v.name))
                || latam[0] || es[0] || null;
        }}

        function hablar() {{
            const voz = elegirVoz(synth.getVoices());
            const utterance = new SpeechSynthesisUtterance({js_text});
            if (voz) {{ utterance.voice = voz; }}
            utterance.lang = voz ? voz.lang : 'es-MX';
            // Si no hay voz masculina instalada, se baja el tono para que suene más grave
            utterance.pitch = (voz && MASCULINA.test(voz.name)) ? 1.0 : 0.7;
            utterance.rate = 1.0;
            synth.cancel();
            synth.speak(utterance);
        }}

        // Algunos navegadores cargan la lista de voces con retraso
        if (synth.getVoices().length) {{
            hablar();
        }} else {{
            let hecho = false;
            synth.onvoiceschanged = () => {{ if (!hecho) {{ hecho = true; hablar(); }} }};
            setTimeout(() => {{ if (!hecho) {{ hecho = true; hablar(); }} }}, 1000);
        }}
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
        c1, c2, c3 = st.columns([1, 2, 1])
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
    st.markdown("<h1 style='text-align: center;'>⚡ F.O.R.M.U.L.A. ⚡</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #60a5fa; font-size: 12px;'>SISTEMA CENTRAL: ONLINE | NÚCLEO: CLAUDE SONNET 5.5 | ENLACE NEURONAL ACTIVO</p>", unsafe_allow_html=True)
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

            # Entrada de comandos: caja de texto + botón de micrófono al lado
            col_texto, col_mic = st.columns([5, 1], vertical_alignment="bottom")
            with col_texto:
                texto_escrito = st.chat_input("Introduzca directrices operativas o hable con el sistema...")
            with col_mic:
                # Graba la voz y la convierte a texto en el navegador (Chrome/Edge)
                texto_hablado = speech_to_text(
                    language="es-MX",
                    start_prompt="🎙️ Hablar",
                    stop_prompt="⏹️ Enviar",
                    just_once=True,
                    use_container_width=True,
                    key="microfono",
                )

            prompt = texto_escrito or texto_hablado

            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        try:
                            response = client.messages.create(
                                model=MODEL,
                                max_tokens=4000,
                                system="Eres F.O.R.M.U.L.A., una inteligencia artificial analítica avanzada con la estética, precisión y el tono sofisticado de JARVIS en las películas de Tony Stark. Respondes de forma concisa, técnica y ejecutiva en español latinoamericano.",
                                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                            )

                            # La respuesta puede incluir bloques de razonamiento; solo se usan los de texto
                            full_response = "".join(
                                b.text for b in response.content if b.type == "text"
                            ).strip()

                            message_placeholder.markdown(full_response)

                            # Ejecuta la voz sintética
                            speak(full_response)

                            st.session_state.messages.append({"role": "assistant", "content": full_response})
                        except Exception as e:
                            # Se quita el mensaje fallido para no romper el historial
                            st.session_state.messages.pop()
                            st.error(f"Error de enlace con el núcleo ({type(e).__name__}): {e}")
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
                <p style="font-size: 11px; color: #93c5fd;">Pulse 🎙️ Hablar para dictar una directriz y ⏹️ Enviar al terminar. Cada respuesta del núcleo será transmitida con voz masculina en español latino.</p>
            </div>
        """, unsafe_allow_html=True)
