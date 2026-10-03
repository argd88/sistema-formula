import io
import json
import re

import pandas as pd
import streamlit as st
import anthropic
import streamlit.components.v1 as components
from streamlit_mic_recorder import speech_to_text

MODEL = "claude-sonnet-5-5"

# Límite de caracteres de datos que se envían al modelo (para no exceder su contexto)
MAX_CARACTERES_DATOS = 400_000

SYSTEM_PROMPT = """Eres F.O.R.M.U.L.A., una inteligencia artificial analítica avanzada con la estética, precisión y el tono sofisticado de JARVIS en las películas de Tony Stark. Respondes de forma concisa, técnica y ejecutiva en español latinoamericano.

Puedes analizar los archivos de datos que el usuario cargue; su contenido aparece más abajo en formato CSV.

Cuando el usuario te pida crear o exportar un archivo, escribe su contenido completo dentro de una etiqueta así:
<archivo nombre="nombre_del_archivo.ext">
contenido
</archivo>
Formatos permitidos: .xlsx, .csv, .txt, .md, .json. Para .xlsx y .csv escribe el contenido como CSV separado por comas, con una fila de encabezados; el sistema lo convierte a Excel automáticamente. No uses bloques de código dentro de la etiqueta. Fuera de la etiqueta, explica en una o dos frases qué contiene el archivo."""

PATRON_ARCHIVO = re.compile(r'<archivo\s+nombre="([^"]+)"\s*>\s*(.*?)\s*</archivo>', re.DOTALL)

MIME_TYPES = {
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".csv": "text/csv",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".json": "application/json",
}

# Configuración de la página HUD
st.set_page_config(
    page_title="F.O.R.M.U.L.A.",
    page_icon="⚡",
    layout="wide"
)

# Estilo visual estilo interfaz JARVIS (Iron Man)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

:root {
    --cyan: #00e5ff;
    --cyan-suave: rgba(0, 229, 255, 0.35);
    --panel: rgba(4, 22, 40, 0.62);
    --texto: #cfefff;
    --apagado: #7fb8d6;
}

/* Fondo: degradado azul profundo + cuadrícula holográfica */
.stApp {
    background: radial-gradient(ellipse at top, #0a2540 0%, #020814 55%, #000000 100%);
    color: var(--texto);
}
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0, 229, 255, 0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 229, 255, 0.045) 1px, transparent 1px);
    background-size: 42px 42px;
    pointer-events: none;
}
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.5rem; }

.stApp p, .stApp li, .stApp label, .stMarkdown, .stApp input, .stApp textarea, .stApp button {
    font-family: 'Rajdhani', sans-serif !important;
}

/* Paneles de información: vidrio oscuro, bordes redondeados y brillo */
.hud-panel {
    position: relative;
    background: var(--panel);
    border: 1px solid var(--cyan-suave);
    border-radius: 18px;
    padding: 16px 18px;
    margin-bottom: 14px;
    box-shadow: 0 0 18px rgba(0, 229, 255, 0.12), inset 0 0 24px rgba(0, 229, 255, 0.06);
    backdrop-filter: blur(6px);
}
.hud-panel::before {
    content: "";
    position: absolute;
    top: -1px;
    left: 26px;
    width: 64px;
    height: 2px;
    background: var(--cyan);
    box-shadow: 0 0 10px var(--cyan);
    border-radius: 2px;
}
.hud-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2.5px;
    color: var(--cyan);
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
}
.hud-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--cyan);
    box-shadow: 0 0 8px var(--cyan);
    animation: pulso 2s infinite;
}
.hud-big {
    font-family: 'Orbitron', sans-serif;
    font-size: 30px;
    font-weight: 700;
    color: #e6fdff;
    text-shadow: 0 0 14px var(--cyan);
    line-height: 1.1;
}
.hud-label {
    font-size: 13px;
    color: var(--apagado);
    letter-spacing: 1px;
    text-transform: uppercase;
}
.hud-row {
    display: flex;
    justify-content: space-between;
    font-size: 16px;
    padding: 6px 0;
    border-bottom: 1px solid rgba(0, 229, 255, 0.08);
    color: var(--texto);
}
.hud-row b { font-family: 'Orbitron', sans-serif; font-size: 14px; color: #e6fdff; }
.hud-bar {
    height: 6px;
    background: rgba(0, 229, 255, 0.12);
    border-radius: 6px;
    overflow: hidden;
    margin: 2px 0 10px;
}
.hud-bar > div {
    height: 100%;
    background: linear-gradient(90deg, #00e5ff, #3b82f6);
    box-shadow: 0 0 8px var(--cyan);
    border-radius: 6px;
}
.hud-news {
    font-size: 15px;
    padding: 8px 0;
    border-bottom: 1px solid rgba(0, 229, 255, 0.08);
    color: var(--texto);
}
.hud-tag {
    font-family: 'Orbitron', sans-serif;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #020814;
    background: var(--cyan);
    padding: 2px 7px;
    border-radius: 6px;
    margin-right: 6px;
}
.hud-text { font-size: 15px; color: var(--apagado); margin: 0; }
@keyframes pulso { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

/* Mensajes del chat: burbujas claras redondeadas con texto negro */
[data-testid="stChatMessage"] {
    background: rgba(224, 250, 255, 0.96) !important;
    border: 1px solid var(--cyan);
    border-radius: 18px;
    box-shadow: 0 0 14px rgba(0, 229, 255, 0.22);
    margin-bottom: 10px;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] * {
    color: #000000 !important;
    font-size: 16px;
}

/* Caja de escritura: redondeada, fondo blanco, texto negro, borde cian */
[data-testid="stChatInput"] {
    border-radius: 18px !important;
    border: 1px solid var(--cyan) !important;
    box-shadow: 0 0 16px rgba(0, 229, 255, 0.25);
    background: #ffffff !important;
}
[data-testid="stChatInput"] textarea {
    background: #ffffff !important;
    color: #000000 !important;
    font-size: 16px !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #5b6b75 !important; }

/* Carga de archivos */
[data-testid="stFileUploaderDropzone"] {
    background: var(--panel) !important;
    border: 1px dashed var(--cyan) !important;
    border-radius: 16px !important;
}
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploaderFileName"] { color: var(--apagado) !important; }

/* Botones (descargas, limpiar, subir) */
.stDownloadButton button, .stButton button, [data-testid="stFileUploaderDropzone"] button {
    background: rgba(0, 229, 255, 0.08) !important;
    color: var(--cyan) !important;
    border: 1px solid var(--cyan) !important;
    border-radius: 12px !important;
    letter-spacing: 1px;
    transition: all 0.2s;
}
.stDownloadButton button:hover, .stButton button:hover, [data-testid="stFileUploaderDropzone"] button:hover {
    background: rgba(0, 229, 255, 0.2) !important;
    box-shadow: 0 0 14px var(--cyan);
}

/* Vista previa de tablas */
[data-testid="stExpander"] details {
    background: var(--panel);
    border: 1px solid var(--cyan-suave) !important;
    border-radius: 14px !important;
}

/* Barra de desplazamiento del chat */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: var(--cyan-suave); border-radius: 6px; }
</style>
""", unsafe_allow_html=True)


# Cabecera animada: reactor ARC, título y reloj en vivo (va en un iframe para poder usar JavaScript)
CABECERA_HTML = """
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@500;600&display=swap" rel="stylesheet">
<style>
    body { margin: 0; background: transparent; font-family: 'Rajdhani', sans-serif; color: #cfefff; overflow: hidden; }
    .wrap { display: flex; align-items: center; justify-content: space-between; padding: 6px 4px; }
    .centro { display: flex; align-items: center; gap: 26px; }
    .reactor { position: relative; width: 112px; height: 112px; flex-shrink: 0; }
    .ring { position: absolute; border-radius: 50%; border: 2px solid rgba(0, 229, 255, 0.6); }
    .r1 { inset: 0; border-style: dashed; animation: girar 14s linear infinite; }
    .r2 { inset: 12px; border: 3px solid rgba(0, 229, 255, 0.25); border-top-color: #00e5ff; border-bottom-color: #00e5ff; animation: girar 4s linear infinite reverse; }
    .r3 { inset: 27px; border-width: 1px; border-style: dotted; animation: girar 9s linear infinite; }
    .core { position: absolute; inset: 40px; border-radius: 50%;
            background: radial-gradient(circle, #ffffff 0%, #9ff4ff 30%, #00e5ff 60%, transparent 75%);
            box-shadow: 0 0 30px #00e5ff, 0 0 60px rgba(0, 229, 255, 0.6); animation: latir 3s ease-in-out infinite; }
    @keyframes girar { to { transform: rotate(360deg); } }
    @keyframes latir { 50% { opacity: 0.65; transform: scale(0.9); } }
    @keyframes pulso { 50% { opacity: 0.3; } }
    h1 { font-family: 'Orbitron', sans-serif; font-weight: 900; font-size: 46px; letter-spacing: 10px; margin: 0;
         color: #e6fdff; text-shadow: 0 0 18px #00e5ff, 0 0 40px rgba(0, 229, 255, 0.4); }
    .sub { font-family: 'Orbitron', sans-serif; font-size: 11px; letter-spacing: 5px; color: #7fb8d6; margin-top: 4px; }
    .estado { display: flex; gap: 10px; margin-top: 12px; flex-wrap: wrap; }
    .pill { border: 1px solid rgba(0, 229, 255, 0.4); border-radius: 999px; padding: 4px 14px;
            background: rgba(0, 229, 255, 0.06); font-size: 14px; font-weight: 600; letter-spacing: 1px; }
    .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #22ff88;
           box-shadow: 0 0 8px #22ff88; margin-right: 6px; animation: pulso 2s infinite; }
    .lado { text-align: right; min-width: 200px; }
    .reloj { font-family: 'Orbitron', sans-serif; font-size: 34px; font-weight: 700; color: #e6fdff; text-shadow: 0 0 12px #00e5ff; }
    .fecha { font-size: 14px; color: #7fb8d6; letter-spacing: 2px; text-transform: uppercase; }
    @media (max-width: 900px) { .lado { display: none; } h1 { font-size: 28px; letter-spacing: 5px; } .reactor { width: 80px; height: 80px; } }
</style>
<div class="wrap">
    <div class="lado" style="text-align:left">
        <div class="fecha">Ubicación</div>
        <div class="reloj" style="font-size:20px">SANTIAGO · CL</div>
    </div>
    <div class="centro">
        <div class="reactor"><div class="ring r1"></div><div class="ring r2"></div><div class="ring r3"></div><div class="core"></div></div>
        <div>
            <h1>F.O.R.M.U.L.A.</h1>
            <div class="sub">ASISTENTE ANALÍTICO PERSONAL</div>
            <div class="estado">
                <span class="pill"><span class="dot"></span>SISTEMA ONLINE</span>
                <span class="pill">NÚCLEO: __MODELO__</span>
                <span class="pill">ENLACE NEURONAL ACTIVO</span>
            </div>
        </div>
    </div>
    <div class="lado">
        <div class="reloj" id="reloj">--:--:--</div>
        <div class="fecha" id="fecha"></div>
    </div>
</div>
<script>
    function actualizar() {
        const ahora = new Date();
        const zona = { timeZone: 'America/Santiago' };
        document.getElementById('reloj').textContent = ahora.toLocaleTimeString('es-CL', { ...zona, hour12: false });
        document.getElementById('fecha').textContent = ahora.toLocaleDateString('es-CL', { ...zona, weekday: 'long', day: 'numeric', month: 'long' });
    }
    actualizar();
    setInterval(actualizar, 1000);
</script>
"""


# Panel HUD reutilizable
def panel(titulo, contenido):
    # Se quitan las sangrías para que Markdown no lo confunda con un bloque de código
    contenido = "".join(linea.strip() for linea in contenido.splitlines())
    st.markdown(
        f'<div class="hud-panel"><div class="hud-title"><span class="hud-dot"></span>{titulo}</div>{contenido}</div>',
        unsafe_allow_html=True,
    )


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


# Lee un .csv o .xlsx cargado y devuelve {nombre_de_tabla: DataFrame}
@st.cache_data(show_spinner=False)
def leer_archivo(nombre, contenido):
    if nombre.lower().endswith(".csv"):
        try:
            return {nombre: pd.read_csv(io.BytesIO(contenido))}
        except UnicodeDecodeError:
            # CSV exportados desde Excel en español suelen venir en latin-1 y con ;
            return {nombre: pd.read_csv(io.BytesIO(contenido), encoding="latin-1", sep=None, engine="python")}
    # Excel: se leen todas las hojas
    hojas = pd.read_excel(io.BytesIO(contenido), sheet_name=None)
    return {f"{nombre} / hoja {hoja}": df for hoja, df in hojas.items()}


# Convierte las tablas cargadas en texto para el modelo; avisa si hubo que recortar
def datos_para_modelo(tablas):
    partes = []
    recortado = False
    restante = MAX_CARACTERES_DATOS
    for nombre, df in tablas.items():
        csv = df.to_csv(index=False)
        encabezado = f"### Archivo: {nombre} ({len(df)} filas, {len(df.columns)} columnas)\n"
        if len(csv) > restante:
            csv = csv[:max(restante, 0)].rsplit("\n", 1)[0]
            encabezado += "AVISO: los datos están recortados por tamaño; solo se incluyen las primeras filas.\n"
            recortado = True
        restante -= len(csv)
        partes.append(encabezado + csv)
    return "\n\n".join(partes), recortado


# Separa los archivos generados por el agente del texto de la respuesta
def extraer_archivos(texto):
    archivos = []
    for nombre, contenido in PATRON_ARCHIVO.findall(texto):
        # Por si el modelo envolvió el contenido en ``` igualmente
        contenido = re.sub(r"^```\w*\n|\n?```$", "", contenido.strip())
        extension = "." + nombre.rsplit(".", 1)[-1].lower() if "." in nombre else ".txt"
        if extension not in MIME_TYPES:
            nombre, extension = nombre + ".txt", ".txt"
        if extension == ".xlsx":
            try:
                buffer = io.BytesIO()
                pd.read_csv(io.StringIO(contenido)).to_excel(buffer, index=False)
                datos = buffer.getvalue()
            except Exception:
                # Si el contenido no es una tabla válida, se entrega como CSV
                nombre, extension = nombre[:-5] + ".csv", ".csv"
                datos = contenido.encode("utf-8-sig")
        elif extension == ".csv":
            # utf-8-sig para que Excel muestre bien las tildes
            datos = contenido.encode("utf-8-sig")
        else:
            datos = contenido.encode("utf-8")
        archivos.append({"nombre": nombre, "datos": datos, "mime": MIME_TYPES[extension]})
    return archivos


# Texto de la respuesta sin el contenido de los archivos (para mostrar y leer en voz alta)
def texto_visible(texto):
    return PATRON_ARCHIVO.sub(lambda m: f"\n\n📎 *Archivo generado: {m.group(1)}* (ver panel de descargas)\n\n", texto).strip()


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
    # Cabecera animada con reactor ARC y reloj
    components.html(CABECERA_HTML.replace("__MODELO__", "CLAUDE SONNET 5.5"), height=150)

    # Layout de 3 columnas estilo interfaz Stark (Paneles laterales + Núcleo Central)
    col_left, col_center, col_right = st.columns([1.2, 2.6, 1.2], gap="medium")

    # --- PANEL IZQUIERDO: Clima, Divisas, Diagnóstico y Carga de Datos ---
    with col_left:
        panel("Meteorología", """
            <div class="hud-label">Santiago, Chile</div>
            <div class="hud-big">18°C</div>
            <p class="hud-text">Cielo despejado · Condición óptima</p>
        """)

        panel("Tasas de cambio", """
            <div class="hud-row"><span>USD / CLP</span><b>$925.50</b></div>
            <div class="hud-row"><span>EUR / CLP</span><b>$988.20</b></div>
            <p class="hud-text" style="margin-top:8px; font-size:13px;">Actualización de mercado en vivo</p>
        """)

        panel("Diagnóstico de núcleo", """
            <div class="hud-row" style="border:none"><span>CPU</span><b>14%</b></div>
            <div class="hud-bar"><div style="width:14%"></div></div>
            <div class="hud-row" style="border:none"><span>RAM</span><b>32%</b></div>
            <div class="hud-bar"><div style="width:32%"></div></div>
            <div class="hud-row"><span>Latencia</span><b>18 ms</b></div>
            <div class="hud-row" style="border:none"><span>Seguridad</span><b>SSL</b></div>
        """)

        # --- Carga de archivos de datos ---
        panel("Carga de datos", '<p class="hud-text">Suba archivos .xlsx o .csv para que el núcleo los analice.</p>')
        archivos_cargados = st.file_uploader(
            "Archivos de datos",
            type=["xlsx", "csv"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        tablas = {}
        for archivo in archivos_cargados or []:
            try:
                tablas.update(leer_archivo(archivo.name, archivo.getvalue()))
            except Exception as e:
                st.error(f"No se pudo leer {archivo.name}: {e}")

        for nombre, df in tablas.items():
            with st.expander(f"👁️ {nombre} ({len(df)} filas)"):
                st.dataframe(df.head(50), use_container_width=True)

    # --- PANEL CENTRAL: Cuadro de Diálogo Principal ---
    with col_center:
        panel("Núcleo de diálogo operativo", '<p class="hud-text">Escriba o dicte sus directrices. El núcleo responde por texto y voz.</p>')

        if "anthropic_api_key" in st.secrets:
            client = anthropic.Anthropic(api_key=st.secrets["anthropic_api_key"])

            if "messages" not in st.session_state:
                st.session_state.messages = []

            # Instrucciones + datos cargados; el bloque de datos se guarda en caché para no pagarlo en cada mensaje
            system = [{"type": "text", "text": SYSTEM_PROMPT}]
            if tablas:
                texto_datos, recortado = datos_para_modelo(tablas)
                system.append({
                    "type": "text",
                    "text": "## Archivos cargados por el usuario\n\n" + texto_datos,
                    "cache_control": {"type": "ephemeral"},
                })
                if recortado:
                    st.warning("Los archivos son muy grandes: el núcleo solo recibirá las primeras filas.")

            # Contenedor del historial de chat en el centro
            chat_container = st.container(height=520, border=False)
            with chat_container:
                if not st.session_state.messages:
                    st.markdown(
                        '<div style="text-align:center; padding-top:170px; font-family:Orbitron; letter-spacing:4px; '
                        'color:#7fb8d6; font-size:13px;">SISTEMA LISTO · ESPERANDO DIRECTRICES</div>',
                        unsafe_allow_html=True,
                    )
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(texto_visible(message["content"]))

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
                                max_tokens=16000,
                                system=system,
                                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                            )

                            # La respuesta puede incluir bloques de razonamiento; solo se usan los de texto
                            full_response = "".join(
                                b.text for b in response.content if b.type == "text"
                            ).strip()

                            if response.stop_reason == "max_tokens":
                                st.warning("La respuesta se cortó por longitud; un archivo muy grande puede haber quedado incompleto.")

                            # Guarda los archivos que haya creado el agente para el panel de descargas
                            if "archivos_generados" not in st.session_state:
                                st.session_state.archivos_generados = []
                            st.session_state.archivos_generados.extend(extraer_archivos(full_response))

                            respuesta_visible = texto_visible(full_response)
                            message_placeholder.markdown(respuesta_visible)

                            # Ejecuta la voz sintética (sin leer el contenido de los archivos)
                            speak(respuesta_visible)

                            st.session_state.messages.append({"role": "assistant", "content": full_response})
                        except Exception as e:
                            # Se quita el mensaje fallido para no romper el historial
                            st.session_state.messages.pop()
                            st.error(f"Error de enlace con el núcleo ({type(e).__name__}): {e}")
        else:
            st.warning("Falta configurar la clave de Anthropic en los secretos.")

    # --- PANEL DERECHO: Descargas, Noticias y Actividad ---
    with col_right:
        # --- Archivos creados por el agente ---
        panel("Archivos generados", '<p class="hud-text">Pida al núcleo que cree un archivo (Excel, CSV, texto…) y aparecerá aquí.</p>')
        archivos_generados = st.session_state.get("archivos_generados", [])
        for i, archivo in enumerate(reversed(archivos_generados)):
            st.download_button(
                f"⬇️ {archivo['nombre']}",
                data=archivo["datos"],
                file_name=archivo["nombre"],
                mime=archivo["mime"],
                key=f"descarga_{len(archivos_generados) - i}",
                use_container_width=True,
            )
        if archivos_generados and st.button("🗑️ Limpiar lista", use_container_width=True):
            st.session_state.archivos_generados = []
            st.rerun()

        panel("Noticias globales", """
            <div class="hud-news"><span class="hud-tag">TECH</span>Avances récord en procesamiento de IA cuántica.</div>
            <div class="hud-news"><span class="hud-tag">MERCADOS</span>Wall Street abre con tendencia alcista.</div>
            <div class="hud-news" style="border:none"><span class="hud-tag">LOGÍSTICA</span>Optimización de cadenas de suministro globales activa.</div>
        """)

        panel("Interacción por voz", """
            <p class="hud-text">Pulse <b style="color:#00e5ff">🎙️ Hablar</b> para dictar una directriz y <b style="color:#00e5ff">⏹️ Enviar</b> al terminar.
            Cada respuesta del núcleo se transmite con voz masculina en español latino.</p>
        """)
