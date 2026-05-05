"""
ESG KPI PDF Highlighter — Streamlit App
Estilo visual inspirado na Aplanet (verde corporativo, UI limpa e profissional)
"""

import streamlit as st
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# ── Deve ser o primeiro comando Streamlit ─────────────────────────────────────
st.set_page_config(
    page_title="ESG PDF Highlighter · Aplanet",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS: Estilo Aplanet ───────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@400;600;700&display=swap');

/* ── Variáveis de cor Aplanet ── */
:root {
    --green-dark:   #1a3d2b;
    --green-mid:    #2d6a4f;
    --green-accent: #40916c;
    --green-light:  #74c69d;
    --green-pale:   #d8f3dc;
    --white:        #ffffff;
    --gray-50:      #f8faf9;
    --gray-100:     #eef2f0;
    --gray-200:     #d5ddd9;
    --gray-500:     #6b7c74;
    --gray-700:     #374840;
    --orange:       #e76f51;
    --yellow:       #f4a261;
    --shadow-sm:    0 1px 3px rgba(26,61,43,.08);
    --shadow-md:    0 4px 16px rgba(26,61,43,.12);
    --radius:       10px;
}

/* ── Reset global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: var(--gray-700);
}

/* ── Fundo principal ── */
.stApp {
    background: var(--gray-50);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--green-dark) !important;
    border-right: none;
}
section[data-testid="stSidebar"] * {
    color: var(--white) !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stCheckbox label,
section[data-testid="stSidebar"] p {
    color: rgba(255,255,255,0.85) !important;
    font-size: 0.85rem;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15);
}

/* ── Header principal ── */
.aplanet-header {
    background: linear-gradient(135deg, var(--green-dark) 0%, var(--green-mid) 100%);
    border-radius: var(--radius);
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    box-shadow: var(--shadow-md);
}
.aplanet-logo {
    font-family: 'Sora', sans-serif;
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--white);
    letter-spacing: -0.5px;
}
.aplanet-logo span {
    color: var(--green-light);
}
.aplanet-tagline {
    font-size: 0.88rem;
    color: rgba(255,255,255,0.7);
    margin-top: 2px;
    font-weight: 400;
}

/* ── Cards ── */
.card {
    background: var(--white);
    border-radius: var(--radius);
    padding: 1.5rem 1.75rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--gray-100);
    margin-bottom: 1rem;
}
.card-title {
    font-family: 'Sora', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--green-dark);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Métricas customizadas ── */
.metric-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.25rem;
    flex-wrap: wrap;
}
.metric-box {
    flex: 1;
    min-width: 120px;
    background: var(--white);
    border: 1px solid var(--gray-100);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    box-shadow: var(--shadow-sm);
    text-align: center;
}
.metric-value {
    font-family: 'Sora', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--green-accent);
    line-height: 1;
}
.metric-label {
    font-size: 0.75rem;
    color: var(--gray-500);
    margin-top: 4px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.metric-box.warn .metric-value  { color: var(--orange); }
.metric-box.info .metric-value  { color: var(--yellow); }

/* ── Status tags ── */
.tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.tag-found    { background: var(--green-pale); color: var(--green-dark); }
.tag-notfound { background: #fce8e2; color: #b33b1f; }
.tag-skipped  { background: var(--gray-100); color: var(--gray-500); }

/* ── Tabela de resultados ── */
.result-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.84rem;
}
.result-table th {
    background: var(--gray-50);
    color: var(--gray-500);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.72rem;
    padding: 0.6rem 0.9rem;
    border-bottom: 1px solid var(--gray-200);
    text-align: left;
}
.result-table td {
    padding: 0.65rem 0.9rem;
    border-bottom: 1px solid var(--gray-100);
    vertical-align: middle;
}
.result-table tr:last-child td { border-bottom: none; }
.result-table tr:hover td { background: var(--gray-50); }

/* ── Botão principal ── */
div.stButton > button {
    background: var(--green-accent) !important;
    color: var(--white) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 1.6rem !important;
    transition: background 0.18s ease;
    letter-spacing: 0.01em;
}
div.stButton > button:hover {
    background: var(--green-mid) !important;
}

/* ── Download button ── */
div.stDownloadButton > button {
    background: var(--green-dark) !important;
    color: var(--white) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100%;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--gray-200) !important;
    border-radius: var(--radius) !important;
    background: var(--white) !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--green-light) !important;
}

/* ── Progress bar ── */
.stProgress > div > div {
    background: var(--green-accent) !important;
}

/* ── Alerts ── */
.stAlert { border-radius: var(--radius) !important; }

/* ── Oculta menu padrão Streamlit ── */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Helper: importar o highlighter ───────────────────────────────────────────
def load_highlighter():
    try:
        import fitz  # noqa
        return True
    except ImportError:
        return False


def run_highlight(pdf_bytes, json_data, include_unverified):
    """Executa o highlight em arquivos temporários e retorna (pdf_bytes, stats)."""
    import sys, importlib, types

    # Importar pdf_highlighter dinamicamente (mesmo diretório ou via sys.path)
    try:
        from pdf_highlighter import highlight_pdf
    except ImportError:
        # Tenta carregar do mesmo diretório do app.py
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "pdf_highlighter",
            Path(__file__).parent / "pdf_highlighter.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        highlight_pdf = mod.highlight_pdf

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        pdf_in  = tmpdir / "input.pdf"
        json_in = tmpdir / "kpis.json"
        pdf_out = tmpdir / "output.pdf"

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
    <div style="padding: 1rem 0 0.5rem;">
        <div style="font-family:'Sora',sans-serif; font-size:1.25rem; font-weight:700; color:#fff;">
            🌿 aplanet
        </div>
        <div style="font-size:0.75rem; color:rgba(255,255,255,0.55); margin-top:2px;">
            ESG Intelligence Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**⚙️ Configurações**")

    include_unverified = st.checkbox(
        "Incluir não verificados",
        value=False,
        help="Destaca em laranja as citações marcadas como não verificadas no JSON"
    )

    st.markdown("---")
    st.markdown("**📘 Como usar**")
    st.markdown("""
<div style="font-size:0.8rem; color:rgba(255,255,255,0.75); line-height:1.7;">
1. Faça upload do <b>PDF</b> do relatório ESG<br>
2. Faça upload do <b>JSON</b> exportado pelo KPI Extractor<br>
3. Clique em <b>Processar</b><br>
4. Baixe o PDF com os highlights
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
<div style="font-size:0.72rem; color:rgba(255,255,255,0.4); text-align:center; padding-top:0.5rem;">
    ESG PDF Highlighter v1.0<br>Powered by PyMuPDF
</div>
""", unsafe_allow_html=True)


# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="aplanet-header">
    <div>
        <div class="aplanet-logo">🌿 aplanet <span>ESG</span></div>
        <div class="aplanet-tagline">PDF Highlighter · Extração e verificação de KPIs ESG</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── VERIFICAR DEPENDÊNCIAS ────────────────────────────────────────────────────
if not load_highlighter():
    st.error("⚠️ **PyMuPDF não instalado.** Execute: `pip install pymupdf`")
    st.stop()

# ── UPLOAD DE ARQUIVOS ────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="card"><div class="card-title">📄 Relatório PDF</div>', unsafe_allow_html=True)
    pdf_file = st.file_uploader(
        "Arraste ou clique para selecionar",
        type=["pdf"],
        label_visibility="collapsed",
        key="pdf_upload"
    )
    if pdf_file:
        size_kb = len(pdf_file.getvalue()) / 1024
        st.markdown(f"<div style='font-size:0.8rem;color:#2d6a4f;margin-top:0.5rem;'>✓ {pdf_file.name} &nbsp;·&nbsp; {size_kb:.0f} KB</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><div class="card-title">📊 JSON de KPIs</div>', unsafe_allow_html=True)
    json_file = st.file_uploader(
        "Arraste ou clique para selecionar",
        type=["json"],
        label_visibility="collapsed",
        key="json_upload"
    )
    if json_file:
        try:
            json_data = json.loads(json_file.getvalue())
            n_kpis = len(json_data.get("kpis", []))
            st.markdown(f"<div style='font-size:0.8rem;color:#2d6a4f;margin-top:0.5rem;'>✓ {json_file.name} &nbsp;·&nbsp; {n_kpis} KPIs detectados</div>", unsafe_allow_html=True)
        except Exception:
            st.error("JSON inválido.")
            json_file = None
    st.markdown("</div>", unsafe_allow_html=True)

# ── BOTÃO PROCESSAR ───────────────────────────────────────────────────────────
st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

can_process = pdf_file is not None and json_file is not None
process_btn = st.button("🔍 Processar e Destacar KPIs", disabled=not can_process, use_container_width=False)

if not can_process:
    st.markdown(
        "<div style='font-size:0.82rem;color:#6b7c74;margin-top:0.25rem;'>Faça upload do PDF e do JSON para continuar.</div>",
        unsafe_allow_html=True
    )

# ── PROCESSAMENTO ─────────────────────────────────────────────────────────────
if process_btn and can_process:
    progress = st.progress(0, text="Iniciando processamento…")

    try:
        json_data = json.loads(json_file.getvalue())
        progress.progress(20, text="JSON carregado…")

        progress.progress(40, text="Abrindo PDF…")
        result_pdf, stats = run_highlight(
            pdf_bytes=pdf_file.getvalue(),
            json_data=json_data,
            include_unverified=include_unverified,
        )
        progress.progress(100, text="Concluído!")

        # ── Guardar resultados na session ────────────────────────────────────
        st.session_state["result_pdf"]  = result_pdf
        st.session_state["stats"]       = stats
        st.session_state["source_name"] = pdf_file.name

    except Exception as e:
        progress.empty()
        st.error(f"Erro durante o processamento: {e}")
        st.exception(e)

# ── RESULTADOS ────────────────────────────────────────────────────────────────
if "stats" in st.session_state and st.session_state.get("result_pdf"):
    stats       = st.session_state["stats"]
    result_pdf  = st.session_state["result_pdf"]
    source_name = st.session_state.get("source_name", "relatorio.pdf")

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    st.markdown("### Resultados")

    # ── Métricas ─────────────────────────────────────────────────────────────
    highlighted = stats.get("highlighted", 0)
    not_found   = stats.get("not_found", 0)
    skipped     = stats.get("skipped_unverified", 0)
    total       = stats.get("total_kpis", 0)
    pct         = round(highlighted / max(total - skipped, 1) * 100)

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-box">
            <div class="metric-value">{highlighted}</div>
            <div class="metric-label">Destacados</div>
        </div>
        <div class="metric-box warn">
            <div class="metric-value">{not_found}</div>
            <div class="metric-label">Não encontrados</div>
        </div>
        <div class="metric-box info">
            <div class="metric-value">{skipped}</div>
            <div class="metric-label">Ignorados</div>
        </div>
        <div class="metric-box">
            <div class="metric-value">{pct}%</div>
            <div class="metric-label">Taxa de acerto</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Download ──────────────────────────────────────────────────────────────
    stem = Path(source_name).stem
    ts   = datetime.now().strftime("%Y%m%d_%H%M")
    dl_name = f"{stem}_highlighted_{ts}.pdf"

    st.download_button(
        label="⬇️  Baixar PDF com Highlights",
        data=result_pdf,
        file_name=dl_name,
        mime="application/pdf",
        use_container_width=False,
    )

    # ── Tabela de detalhes ────────────────────────────────────────────────────
    details = stats.get("details", [])
    if details:
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📋 Detalhe por KPI</div>', unsafe_allow_html=True)

        rows_html = ""
        for d in details:
            status = d.get("status", "skipped")
            if status == "found":
                tag = '<span class="tag tag-found">✓ Encontrado</span>'
                pages = ", ".join(f"p.{p}" for p in sorted(set(d.get("pages", []))))
            elif status == "not_found":
                tag = '<span class="tag tag-notfound">✗ Não encontrado</span>'
                pages = "—"
            else:
                tag = '<span class="tag tag-skipped">– Ignorado</span>'
                pages = "—"

            quote_preview = d.get("quote_preview", "")
            kpi_name      = d.get("kpi", "")
            kpi_id        = d.get("id", "")

            rows_html += f"""
            <tr>
                <td style="color:#6b7c74;font-size:0.78rem;white-space:nowrap;">{kpi_id}</td>
                <td style="font-weight:500;">{kpi_name}</td>
                <td>{tag}</td>
                <td style="color:#6b7c74;font-size:0.82rem;">{pages}</td>
                <td style="color:#6b7c74;font-size:0.78rem;font-style:italic;max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{quote_preview}</td>
            </tr>
            """

        st.markdown(f"""
        <div style="overflow-x:auto;">
        <table class="result-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>KPI</th>
                    <th>Status</th>
                    <th>Páginas</th>
                    <th>Citação (prévia)</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Legenda de cores ──────────────────────────────────────────────────────
    st.markdown("""
    <div style="margin-top:1rem; font-size:0.8rem; color:#6b7c74; display:flex; gap:1.5rem; flex-wrap:wrap;">
        <span>🟡 <b>Amarelo</b> — citação verificada</span>
        <span>🟠 <b>Laranja</b> — citação não verificada</span>
    </div>
    """, unsafe_allow_html=True)
