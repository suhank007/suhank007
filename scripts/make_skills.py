#!/usr/bin/env python3
"""Full skills panel: category label followed by wrapped, staggered
chips. Same visual language as the career-log client chips."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WIDTH = 860
BG = "#0d1117"
BORDER = "#30363d"
TITLEBAR = "#161b22"
CATEGORY_COLOR = "#7dd3fc"
CHIP_BG = "#161b22"
CHIP_TEXT = "#c9d1d9"

CATEGORIES = [
    ("BI & Visualisation", ["Power BI", "Tableau", "QlikView", "Oracle BI", "MicroStrategy", "Cognos", "Spotfire", "Sigma BI"]),
    ("Data Platforms", ["Databricks", "Snowflake", "Azure Data Factory", "DBT", "SQL Server", "ETL"]),
    ("PLM & Enterprise", ["ENOVIA", "3DEXPERIENCE", "SAP", "EBOM/MBOM"]),
    ("Cloud", ["Azure", "Microsoft Fabric", "AWS", "Azure DevOps", "Power Platform"]),
    ("Languages", ["Python", "SQL (T-SQL, Oracle)", "R"]),
    ("AI & Machine Learning", [
        "Claude", "Anthropic API", "OpenAI API", "RAG", "LangGraph", "MCP",
        "Agent Orchestration", "Hugging Face", "Ollama", "Embeddings",
        "pgvector", "Pinecone", "Azure AI Search", "Reranking", "PyTorch",
        "Scikit-learn", "Docker", "Kubernetes", "CI/CD", "Prompt Engineering",
    ]),
]

TOP_PAD = 30
CAT_GAP = 22
CHIP_H = 26
CHIP_ROW_GAP = 8
CHIP_PAD_X = 14
CHIP_CHAR_W = 6.6
CHIP_STAGGER_MS = 22
CAT_STAGGER_MS = 260


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def layout_chips(items, max_w):
    cx, cy = 0, 0
    placed = []
    for name in items:
        w = len(name) * CHIP_CHAR_W + CHIP_PAD_X * 2
        if cx + w > max_w and cx > 0:
            cx = 0
            cy += CHIP_H + CHIP_ROW_GAP
        placed.append((name, cx, cy, w))
        cx += w + 8
    return placed, cy + CHIP_H


def build_svg(static: bool) -> str:
    max_w = WIDTH - 56
    y = TOP_PAD
    blocks = []
    chip_index = 0

    for cat_i, (category, items) in enumerate(CATEGORIES):
        cat_delay = cat_i * CAT_STAGGER_MS
        if static:
            cat_opacity = 'opacity="1"'
            cat_style = ""
        else:
            cat_opacity = 'opacity="0"'
            cat_style = f'style="animation: fade-in 260ms ease-out {cat_delay}ms forwards"'
        blocks.append(
            f'<text x="28" y="{y + 12}" {cat_opacity} {cat_style} font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="12.5" font-weight="600" fill="{CATEGORY_COLOR}">{esc(category)}</text>'
        )
        chips_top = y + 26
        placed, block_h = layout_chips(items, max_w)
        for name, cx, cy_, w in placed:
            x = 28 + cx
            cy_abs = chips_top + cy_
            delay = cat_delay + 120 + chip_index * CHIP_STAGGER_MS
            chip_index += 1
            if static:
                chip_opacity = 'opacity="1"'
                chip_transform = ""
                chip_style = ""
            else:
                chip_opacity = 'opacity="0"'
                chip_transform = 'transform="translate(0,6)"'
                chip_style = f'style="animation: chip-in 220ms ease-out {delay}ms forwards"'
            blocks.append(
                f'''<g {chip_opacity} {chip_transform} {chip_style}>
  <rect x="{x}" y="{cy_abs}" width="{w:.1f}" height="{CHIP_H}" rx="13" fill="{CHIP_BG}" stroke="{BORDER}"/>
  <text x="{x + w / 2:.1f}" y="{cy_abs + 17}" text-anchor="middle" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="11" fill="{CHIP_TEXT}">{esc(name)}</text>
</g>'''
            )
        y = chips_top + block_h + CAT_GAP

    height = y + 10

    keyframes = "" if static else """
    @keyframes fade-in {
      from { opacity: 0; }
      to   { opacity: 1; }
    }
    @keyframes chip-in {
      from { opacity: 0; transform: translate(0, 6px); }
      to   { opacity: 1; transform: translate(0, 0); }
    }
    """

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height:.0f}" viewBox="0 0 {WIDTH} {height:.1f}">
  <style>{keyframes}</style>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1:.1f}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="34" rx="10" fill="{TITLEBAR}"/>
  <rect x="0.5" y="24.5" width="{WIDTH - 1}" height="10" fill="{TITLEBAR}"/>
  <line x1="0.5" y1="34.5" x2="{WIDTH - 0.5}" y2="34.5" stroke="{BORDER}"/>
  <circle cx="24" cy="17" r="6" fill="#ff5f56"/>
  <circle cx="44" cy="17" r="6" fill="#ffbd2e"/>
  <circle cx="64" cy="17" r="6" fill="#27c93f"/>
{chr(10).join(blocks)}
</svg>'''


if __name__ == "__main__":
    static = os.environ.get("STATIC") == "1"
    out = ROOT / "skills.svg"
    out.write_text(build_svg(static))
    print(f"Wrote {out}")
