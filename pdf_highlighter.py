"""
PDF Highlighter — ESG KPI Extractor
====================================
Recebe o JSON exportado pelo artifact e o PDF original.
Destaca as citações verbatim verificadas directamente no PDF.

Uso:
    pip install pymupdf
    python pdf_highlighter.py --pdf relatorio.pdf --json kpis_2024-01-01.json

Output:
    relatorio_highlighted.pdf  — PDF original com highlights amarelos
    highlight_report.txt       — log de quais citações foram encontradas/não encontradas
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import fitz  # pymupdf
except ImportError:
    print("Erro: pymupdf não está instalado.")
    print("Instala com: pip install pymupdf")
    sys.exit(1)


# ── Cores dos highlights ──────────────────────────────────────────────────────
HIGHLIGHT_VERIFIED   = (1.0, 0.95, 0.0)   # amarelo — citação verificada
HIGHLIGHT_UNVERIFIED = (1.0, 0.7,  0.3)   # laranja — citação não verificada (opcional)

# ── Normalização de texto para matching ──────────────────────────────────────
def normalize(text: str) -> str:
    """Remove espaços extra e converte para lowercase."""
    return re.sub(r'\s+', ' ', text or '').strip().lower()


def find_quote_in_page(page: fitz.Page, quote: str) -> list:
    """
    Tenta encontrar uma citação numa página do PDF.
    Devolve lista de Rect (coordenadas) onde a citação foi encontrada.
    Faz múltiplas tentativas com variações do texto.
    """
    if not quote or len(quote.strip()) < 5:
        return []

    attempts = [
        quote.strip(),
        # Remove pontuação do início/fim
        quote.strip().strip('.,;:()[]"\''),
        # Primeiras 80 chars (evita citações muito longas)
        quote.strip()[:80],
        # Primeiras 50 chars
        quote.strip()[:50],
    ]

    for attempt in attempts:
        if len(attempt) < 5:
            continue
        try:
            rects = page.search_for(attempt, quads=False)
            if rects:
                return rects
        except Exception:
            continue

    return []


def highlight_pdf(pdf_path: str, json_path: str, output_path: str = None,
                  include_unverified: bool = False) -> dict:
    """
    Processo principal de highlight.

    Args:
        pdf_path: caminho para o PDF original
        json_path: caminho para o JSON exportado pelo artifact
        output_path: caminho do PDF de output (default: <nome>_highlighted.pdf)
        include_unverified: se True, também destaca citações não verificadas (laranja)

    Returns:
        dict com estatísticas do processo
    """
    pdf_path = Path(pdf_path)
    json_path = Path(json_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")
    if not json_path.exists():
        raise FileNotFoundError(f"JSON não encontrado: {json_path}")

    # Output path
    if output_path is None:
        output_path = pdf_path.parent / f"{pdf_path.stem}_highlighted.pdf"
    output_path = Path(output_path)

    # Carregar JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    kpis = data.get('kpis', [])
    source_file = data.get('source_file', pdf_path.name)

    print(f"\n{'─'*60}")
    print(f"  ESG PDF Highlighter")
    print(f"{'─'*60}")
    print(f"  PDF:    {pdf_path.name}")
    print(f"  JSON:   {json_path.name} ({len(kpis)} KPIs)")
    print(f"  Output: {output_path.name}")
    print(f"{'─'*60}\n")

    # Abrir PDF
    doc = fitz.open(str(pdf_path))
    total_pages = len(doc)

    stats = {
        'total_kpis': len(kpis),
        'highlighted': 0,
        'not_found': 0,
        'skipped_unverified': 0,
        'details': []
    }

    for kpi in kpis:
        kpi_id    = kpi.get('id', '?')
        kpi_name  = kpi.get('kpi_name', '')
        quote     = kpi.get('verbatim_quote', '')
        verified  = kpi.get('verified', False)
        kpi_type  = kpi.get('type', 'TEXT')
        value     = kpi.get('value', '')

        # Decidir se processa este KPI
        if not verified and not include_unverified:
            stats['skipped_unverified'] += 1
            continue

        if not quote or len(quote.strip()) < 5:
            stats['details'].append({
                'id': kpi_id, 'kpi': kpi_name,
                'status': 'skipped', 'reason': 'citação vazia'
            })
            continue

        color = HIGHLIGHT_VERIFIED if verified else HIGHLIGHT_UNVERIFIED
        found_on_pages = []

        # Procurar em todas as páginas
        for page_num in range(total_pages):
            page = doc[page_num]
            rects = find_quote_in_page(page, quote)

            for rect in rects:
                # Adicionar highlight
                annot = page.add_highlight_annot(rect)
                annot.set_colors(stroke=color)

                # Adicionar nota lateral com o nome do KPI
                note_text = f"[{kpi_id}] {kpi_name}"
                if value:
                    note_text += f"\nValor: {value}"
                if not verified:
                    note_text += "\n⚠ Não verificado"

                annot.set_info(title="ESG KPI", content=note_text)
                annot.update()
                found_on_pages.append(page_num + 1)

        if found_on_pages:
            stats['highlighted'] += 1
            stats['details'].append({
                'id': kpi_id, 'kpi': kpi_name, 'type': kpi_type,
                'status': 'found', 'pages': found_on_pages,
                'quote_preview': quote[:60] + ('...' if len(quote) > 60 else '')
            })
            pages_str = ', '.join(f"p.{p}" for p in sorted(set(found_on_pages)))
            print(f"  ✓ [{kpi_id:>3}] {kpi_name[:45]:<45} → {pages_str}")
        else:
            stats['not_found'] += 1
            stats['details'].append({
                'id': kpi_id, 'kpi': kpi_name, 'type': kpi_type,
                'status': 'not_found',
                'quote_preview': quote[:60] + ('...' if len(quote) > 60 else '')
            })
            print(f"  ✗ [{kpi_id:>3}] {kpi_name[:45]:<45} → não encontrado")

    # Guardar PDF
    doc.save(str(output_path), garbage=4, deflate=True)
    doc.close()

    # Gerar log
    log_path = output_path.parent / f"{output_path.stem}_log.txt"
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"ESG PDF Highlighter — Log\n")
        f.write(f"{'='*60}\n")
        f.write(f"PDF fonte:     {source_file}\n")
        f.write(f"JSON:          {json_path.name}\n")
        f.write(f"Total KPIs:    {stats['total_kpis']}\n")
        f.write(f"Destacados:    {stats['highlighted']}\n")
        f.write(f"Não encontrados: {stats['not_found']}\n")
        f.write(f"Ignorados (não verificados): {stats['skipped_unverified']}\n")
        f.write(f"\n{'─'*60}\n\n")

        for d in stats['details']:
            status_icon = '✓' if d['status'] == 'found' else ('✗' if d['status'] == 'not_found' else '–')
            f.write(f"{status_icon} [{d['id']}] {d['kpi']}\n")
            if d['status'] == 'found':
                f.write(f"   Páginas: {d.get('pages', [])}\n")
            if 'quote_preview' in d:
                f.write(f"   Citação: \"{d['quote_preview']}\"\n")
            f.write('\n')

    # Sumário final
    print(f"\n{'─'*60}")
    print(f"  Destacados:      {stats['highlighted']}/{stats['total_kpis'] - stats['skipped_unverified']}")
    print(f"  Não encontrados: {stats['not_found']}")
    print(f"  Output PDF:      {output_path}")
    print(f"  Log:             {log_path}")
    print(f"{'─'*60}\n")

    return stats


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description='Destaca citações ESG num PDF com base no JSON do KPI Extractor'
    )
    parser.add_argument('--pdf',  required=True, help='Caminho para o PDF original')
    parser.add_argument('--json', required=True, help='Caminho para o JSON exportado pelo artifact')
    parser.add_argument('--output', default=None,
                        help='Caminho do PDF de output (default: <nome>_highlighted.pdf)')
    parser.add_argument('--include-unverified', action='store_true',
                        help='Também destaca citações não verificadas (em laranja)')

    args = parser.parse_args()

    try:
        stats = highlight_pdf(
            pdf_path=args.pdf,
            json_path=args.json,
            output_path=args.output,
            include_unverified=args.include_unverified
        )
    except FileNotFoundError as e:
        print(f"\nErro: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        raise


if __name__ == '__main__':
    main()