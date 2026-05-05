"""
ESG KPI PDF Highlighter — Streamlit App
Estilo visual Aplanet (violeta #7B61FF, sidebar oscura, fondo gris claro)
Idioma: Español
"""

import streamlit as st
import json
import tempfile
from pathlib import Path
from datetime import datetime

# ── Primer comando Streamlit ──────────────────────────────────────────────────
st.set_page_config(
    page_title="ESG PDF Highlighter · Aplanet",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS: Colores y estilo Aplanet real ────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --purple:        #7B61FF;
    --purple-dark:   #5B43D6;
    --purple-pale:   #EDE9FF;
    --purple-mid:    #A993FF;
    --sidebar-bg:    #1A1A2E;
    --white:         #FFFFFF;
    --bg:            #F4F4F8;
    --card-bg:       #FFFFFF;
    --gray-100:      #EBEBF0;
    --gray-200:      #D5D5DF;
    --gray-400:      #9898A8;
    --gray-600:      #55556A;
    --gray-800:      #2A2A3C;
    --red-pale:      #FDECEA;
    --red:           #D93025;
    --shadow-sm:     0 1px 4px rgba(60,60,100,.07);
    --shadow-md:     0 4px 18px rgba(60,60,100,.11);
    --radius:        10px;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--gray-800);
}

.stApp { background: var(--bg); }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: none !important;
}
section[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.88) !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.1) !important;
}
section[data-testid="stSidebar"] .stCheckbox label {
    font-size: 0.85rem !important;
    color: rgba(255,255,255,0.8) !important;
}

/* ── Header ── */
.ap-header {
    background: var(--sidebar-bg);
    border-radius: var(--radius);
    padding: 1.6rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-md);
}
.ap-logo-text {
    font-size: 1.45rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.3px;
}
.ap-logo-text span { color: var(--purple-mid); }
.ap-badge {
    background: var(--purple);
    color: #fff;
    font-size: 0.68rem;
    font-weight: 700;
    padding: 2px 9px;
    border-radius: 999px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-left: 8px;
    vertical-align: middle;
}
.ap-tagline {
    font-size: 0.83rem;
    color: rgba(255,255,255,0.45);
    margin-top: 4px;
}

/* ── Cards ── */
.card {
    background: var(--card-bg);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--gray-100);
    margin-bottom: 1rem;
}
.card-title {
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--gray-600);
    margin-bottom: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Métricas ── */
.metric-row {
    display: flex;
    gap: 0.85rem;
    margin-bottom: 1.25rem;
    flex-wrap: wrap;
}
.metric-box {
    flex: 1;
    min-width: 110px;
    background: var(--card-bg);
    border: 1px solid var(--gray-100);
    border-radius: var(--radius);
    padding: 1rem 1.1rem;
    box-shadow: var(--shadow-sm);
    text-align: center;
}
.metric-box.accent { border-top: 3px solid var(--purple); }
.metric-box.warn   { border-top: 3px solid var(--red); }
.metric-box.muted  { border-top: 3px solid var(--gray-200); }
.metric-box.ok     { border-top: 3px solid #22C55E; }

.metric-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: var(--purple);
    line-height: 1;
}
.metric-box.warn  .metric-value { color: var(--red); }
.metric-box.muted .metric-value { color: var(--gray-400); }
.metric-box.ok    .metric-value { color: #22C55E; }
.metric-label {
    font-size: 0.72rem;
    color: var(--gray-400);
    margin-top: 5px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Tags de estado ── */
.tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.71rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.tag-found    { background: #E8F5E9; color: #2E7D32; }
.tag-notfound { background: var(--red-pale); color: var(--red); }
.tag-skipped  { background: var(--gray-100); color: var(--gray-400); }

/* ── Código de indicador (estilo Aplanet) ── */
.kpi-code {
    display: inline-block;
    background: var(--purple-pale);
    color: var(--purple-dark);
    border: 1px solid #C9BFFF;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 1px 8px;
    letter-spacing: 0.03em;
    white-space: nowrap;
}

/* ── Tabla ── */
.result-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.83rem;
}
.result-table th {
    background: var(--bg);
    color: var(--gray-400);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.7rem;
    padding: 0.6rem 0.85rem;
    border-bottom: 1px solid var(--gray-200);
    text-align: left;
}
.result-table td {
    padding: 0.6rem 0.85rem;
    border-bottom: 1px solid var(--gray-100);
    vertical-align: middle;
}
.result-table tr:last-child td { border-bottom: none; }
.result-table tr:hover td { background: #F9F9FC; }

/* ── Botón principal ── */
div.stButton > button {
    background: var(--purple) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.8rem !important;
    transition: background 0.15s;
}
div.stButton > button:hover {
    background: var(--purple-dark) !important;
}
div.stButton > button:disabled {
    background: var(--gray-200) !important;
    color: var(--gray-400) !important;
}

/* ── Botón de descarga ── */
div.stDownloadButton > button {
    background: var(--purple) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}
div.stDownloadButton > button:hover {
    background: var(--purple-dark) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--gray-200) !important;
    border-radius: var(--radius) !important;
    background: #FAFAFA !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--purple-mid) !important;
}

/* ── Progress bar ── */
.stProgress > div > div {
    background: var(--purple) !important;
}

/* ── Ocultar menú Streamlit ── */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def check_pymupdf():
    try:
        import fitz  # noqa
        return True
    except ImportError:
        return False


def run_highlight(pdf_bytes, json_data, include_unverified):
    """Ejecuta el highlighter en archivos temporales y devuelve (pdf_bytes, stats)."""
    try:
        from pdf_highlighter import highlight_pdf
    except ImportError:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "pdf_highlighter",
            Path(__file__).parent / "pdf_highlighter.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        highlight_pdf = mod.highlight_pdf

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir   = Path(tmpdir)
        pdf_in   = tmpdir / "input.pdf"
        json_in  = tmpdir / "kpis.json"
        pdf_out  = tmpdir / "output.pdf"

        pdf_in.write_bytes(pdf_bytes)
        json_in.write_text(json.dumps(json_data), encoding="utf-8")

        stats = highlight_pdf(
            pdf_path=str(pdf_in),
            json_path=str(json_in),
            output_path=str(pdf_out),
            include_unverified=include_unverified,
        )

        result_pdf = pdf_out.read_bytes() if pdf_out.exists() else None

    return result_pdf, stats


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.1rem 0 0.6rem;">
        <div style="font-size:1.2rem;font-weight:700;color:#fff;letter-spacing:-0.2px;">
            aplanet <span style="color:#A993FF;">ESG</span>
        </div>
        <div style="font-size:0.73rem;color:rgba(255,255,255,0.35);margin-top:2px;">
            Intelligence Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.73rem;font-weight:700;color:rgba(255,255,255,0.4);"
        "text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.6rem;'>"
        "⚙️ Configuración</div>",
        unsafe_allow_html=True
    )

    include_unverified = st.checkbox(
        "Incluir no verificados",
        value=False,
        help="Resalta en naranja las citas marcadas como no verificadas en el JSON"
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.73rem;font-weight:700;color:rgba(255,255,255,0.4);"
        "text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.6rem;'>"
        "📘 Cómo usar</div>",
        unsafe_allow_html=True
    )
    st.markdown("""
<div style="font-size:0.8rem;color:rgba(255,255,255,0.6);line-height:1.9;">
1. Sube el <b style="color:#A993FF;">PDF</b> del informe ESG<br>
2. Sube el <b style="color:#A993FF;">JSON</b> del KPI Extractor<br>
3. Haz clic en <b style="color:#A993FF;">Procesar</b><br>
4. Descarga el PDF resaltado
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
<div style="font-size:0.7rem;color:rgba(255,255,255,0.2);text-align:center;padding-top:0.3rem;">
    ESG PDF Highlighter v1.0<br>Desarrollado con PyMuPDF
</div>
""", unsafe_allow_html=True)


# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ap-header">
    <div class="ap-logo-text">
        aplanet <span>ESG</span>
        <span class="ap-badge">PDF Highlighter</span>
    </div>
    <div class="ap-tagline">Extracción y verificación de indicadores ESG · Resaltado automático en PDF</div>
</div>
""", unsafe_allow_html=True)

# ── VERIFICAR DEPENDENCIAS ────────────────────────────────────────────────────
if not check_pymupdf():
    st.error("⚠️ **PyMuPDF no está instalado.** Ejecuta: `pip install pymupdf`")
    st.stop()

# ── CARGA DE ARCHIVOS ─────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="card"><div class="card-title">📄 Informe PDF</div>', unsafe_allow_html=True)
    pdf_file = st.file_uploader(
        "Arrastra o selecciona el PDF",
        type=["pdf"],
        label_visibility="collapsed",
        key="pdf_upload"
    )
    if pdf_file:
        size_kb = len(pdf_file.getvalue()) / 1024
        st.markdown(
            f"<div style='font-size:0.8rem;color:#7B61FF;margin-top:0.5rem;font-weight:500;'>"
            f"✓ {pdf_file.name} &nbsp;·&nbsp; {size_kb:.0f} KB</div>",
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><div class="card-title">📊 JSON de indicadores</div>', unsafe_allow_html=True)
    json_file = st.file_uploader(
        "Arrastra o selecciona el JSON",
        type=["json"],
        label_visibility="collapsed",
        key="json_upload"
    )
    if json_file:
        try:
            _jdata = json.loads(json_file.getvalue())
            n_kpis = len(_jdata.get("kpis", []))
            st.markdown(
                f"<div style='font-size:0.8rem;color:#7B61FF;margin-top:0.5rem;font-weight:500;'>"
                f"✓ {json_file.name} &nbsp;·&nbsp; {n_kpis} indicadores detectados</div>",
                unsafe_allow_html=True
            )
        except Exception:
            st.error("JSON no válido.")
            json_file = None
    st.markdown("</div>", unsafe_allow_html=True)

# ── BOTÓN PROCESAR ────────────────────────────────────────────────────────────
st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)

can_process = pdf_file is not None and json_file is not None
process_btn = st.button(
    "🔍  Procesar y resaltar indicadores",
    disabled=not can_process,
    use_container_width=False
)

if not can_process:
    st.markdown(
        "<div style='font-size:0.81rem;color:#9898A8;margin-top:0.3rem;'>"
        "Sube el PDF y el JSON para continuar.</div>",
        unsafe_allow_html=True
    )

# ── PROCESAMIENTO ─────────────────────────────────────────────────────────────
if process_btn and can_process:
    progress = st.progress(0, text="Iniciando procesamiento…")
    try:
        json_data = json.loads(json_file.getvalue())
        progress.progress(20, text="JSON cargado…")
        progress.progress(40, text="Abriendo PDF…")

        result_pdf, stats = run_highlight(
            pdf_bytes=pdf_file.getvalue(),
            json_data=json_data,
            include_unverified=include_unverified,
        )
        progress.progress(100, text="¡Completado!")

        st.session_state["result_pdf"]  = result_pdf
        st.session_state["stats"]       = stats
        st.session_state["source_name"] = pdf_file.name

    except Exception as e:
        progress.empty()
        st.error(f"Error durante el procesamiento: {e}")
        st.exception(e)

# ── RESULTADOS ────────────────────────────────────────────────────────────────
if "stats" in st.session_state and st.session_state.get("result_pdf"):
    stats       = st.session_state["stats"]
    result_pdf  = st.session_state["result_pdf"]
    source_name = st.session_state.get("source_name", "informe.pdf")

    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:1rem;font-weight:700;color:#2A2A3C;margin-bottom:0.8rem;'>"
        "Resultados del procesamiento</div>",
        unsafe_allow_html=True
    )

    # Métricas
    highlighted = stats.get("highlighted", 0)
    not_found   = stats.get("not_found", 0)
    skipped     = stats.get("skipped_unverified", 0)
    total       = stats.get("total_kpis", 0)
    pct         = round(highlighted / max(total - skipped, 1) * 100)

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-box accent">
            <div class="metric-value">{highlighted}</div>
            <div class="metric-label">Resaltados</div>
        </div>
        <div class="metric-box warn">
            <div class="metric-value">{not_found}</div>
            <div class="metric-label">No encontrados</div>
        </div>
        <div class="metric-box muted">
            <div class="metric-value">{skipped}</div>
            <div class="metric-label">Omitidos</div>
        </div>
        <div class="metric-box ok">
            <div class="metric-value">{pct}%</div>
            <div class="metric-label">Tasa de éxito</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Descarga
    stem    = Path(source_name).stem
    ts      = datetime.now().strftime("%Y%m%d_%H%M")
    dl_name = f"{stem}_resaltado_{ts}.pdf"

    st.download_button(
        label="⬇️  Descargar PDF resaltado",
        data=result_pdf,
        file_name=dl_name,
        mime="application/pdf",
        use_container_width=False,
    )

    # Tabla detalle
    details = stats.get("details", [])
    if details:
        st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📋 Detalle por indicador</div>', unsafe_allow_html=True)

        rows_html = ""
        for d in details:
            status = d.get("status", "skipped")
            if status == "found":
                tag   = '<span class="tag tag-found">✓ Encontrado</span>'
                pages = ", ".join(f"p.{p}" for p in sorted(set(d.get("pages", []))))
            elif status == "not_found":
                tag   = '<span class="tag tag-notfound">✗ No encontrado</span>'
                pages = "—"
            else:
                tag   = '<span class="tag tag-skipped">– Omitido</span>'
                pages = "—"

            kpi_id        = d.get("id", "")
            kpi_name      = d.get("kpi", "")
            quote_preview = d.get("quote_preview", "")

            rows_html += f"""
            <tr>
                <td><span class="kpi-code">{kpi_id}</span></td>
                <td style="font-weight:500;color:#2A2A3C;">{kpi_name}</td>
                <td>{tag}</td>
                <td style="color:#9898A8;font-size:0.81rem;">{pages}</td>
                <td style="color:#9898A8;font-size:0.77rem;font-style:italic;
                    max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                    {quote_preview}
                </td>
            </tr>
            """

        st.markdown(f"""
        <div style="overflow-x:auto;">
        <table class="result-table">
            <thead>
                <tr>
                    <th>Código</th>
                    <th>Indicador</th>
                    <th>Estado</th>
                    <th>Páginas</th>
                    <th>Cita (vista previa)</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Leyenda
    st.markdown("""
    <div style="margin-top:1rem;font-size:0.79rem;color:#9898A8;display:flex;gap:1.5rem;flex-wrap:wrap;">
        <span>🟡 <b>Amarillo</b> — cita verificada</span>
        <span>🟠 <b>Naranja</b> — cita no verificada</span>
    </div>
    """, unsafe_allow_html=True)
