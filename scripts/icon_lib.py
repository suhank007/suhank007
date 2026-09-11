"""Shared monoline icon library for the profile SVGs.

Icons are cached locally in scripts/icon_cache/ (fetched once from
simple-icons for brand logos and lucide-static for generic glyphs, both
MIT/ISC licensed). This module extracts each icon's inner markup and
re-renders it as a small <g> scaled/recolored to fit the terminal
palette, so every generated SVG stays fully self-contained (no runtime
network calls, safe for GitHub's <img> sandboxing).
"""
import re
from pathlib import Path

CACHE = Path(__file__).resolve().parent / "icon_cache"

# name used in category chip lists -> (cache file stem, "fill" for simple-icons
# brand marks or "stroke" for lucide glyphs)
ICON_MAP = {
    # BI & Visualisation
    "Power BI": ("cloud", "stroke"),
    "Tableau": ("tableau", "fill"),
    "QlikView": ("qlik", "fill"),
    "Oracle BI": ("oracle", "fill"),
    "MicroStrategy": ("bar-chart-3", "stroke"),
    "Cognos": ("layout-dashboard", "stroke"),
    "Spotfire": ("layout-dashboard", "stroke"),
    "Sigma BI": ("sigma", "stroke"),
    # Data Platforms
    "Databricks": ("databricks", "fill"),
    "Snowflake": ("snowflake", "fill"),
    "Azure Data Factory": ("workflow", "stroke"),
    "DBT": ("dbt", "fill"),
    "SQL Server": ("database", "stroke"),
    "ETL": ("shuffle", "stroke"),
    # PLM & Enterprise
    "ENOVIA": ("box", "stroke"),
    "3DEXPERIENCE": ("boxes", "stroke"),
    "SAP": ("sap", "fill"),
    "EBOM/MBOM": ("list-tree", "stroke"),
    # Cloud
    "Azure": ("cloud", "stroke"),
    "Microsoft Fabric": ("layers", "stroke"),
    "AWS": ("server", "stroke"),
    "Azure DevOps": ("git-branch", "stroke"),
    "Power Platform": ("zap", "stroke"),
    # Languages
    "Python": ("python", "fill"),
    "SQL (T-SQL, Oracle)": ("database", "stroke"),
    "R": ("r", "fill"),
    # AI & ML
    "Claude": ("anthropic", "fill"),
    "Anthropic API": ("anthropic", "fill"),
    "OpenAI API": ("openai", "fill"),
    "RAG": ("search", "stroke"),
    "LangGraph": ("workflow", "stroke"),
    "MCP": ("plug", "stroke"),
    "Agent Orchestration": ("bot", "stroke"),
    "Hugging Face": ("huggingface", "fill"),
    "Ollama": ("ollama", "fill"),
    "Embeddings": ("scatter-chart", "stroke"),
    "pgvector": ("postgresql", "fill"),
    "Pinecone": ("boxes", "stroke"),
    "Azure AI Search": ("search", "stroke"),
    "Reranking": ("arrow-up-down", "stroke"),
    "PyTorch": ("pytorch", "fill"),
    "Scikit-learn": ("scikitlearn", "fill"),
    "Docker": ("docker", "fill"),
    "Kubernetes": ("kubernetes", "fill"),
    "CI/CD": ("infinity", "stroke"),
    "Prompt Engineering": ("terminal", "stroke"),
}

_cache_raw: dict[str, str] = {}


def _load(stem: str, kind: str) -> str:
    key = f"{kind}:{stem}"
    if key in _cache_raw:
        return _cache_raw[key]
    fname = f"lucide_{stem}.svg" if kind == "stroke" else f"{stem}.svg"
    path = CACHE / fname
    raw = path.read_text()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", raw, re.S).group(1)
    inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S)
    _cache_raw[key] = inner.strip()
    return _cache_raw[key]


def render_icon(name: str, x: float, y: float, size: float, color: str) -> str:
    """Render the icon registered for `name` as a <g> positioned with its
    top-left at (x, y), scaled to `size`x`size`, recolored to `color`.
    Returns "" if `name` has no icon mapping."""
    entry = ICON_MAP.get(name)
    if entry is None:
        return ""
    stem, kind = entry
    try:
        inner = _load(stem, kind)
    except FileNotFoundError:
        return ""
    scale = size / 24.0
    if kind == "stroke":
        style = f'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    else:
        style = f'fill="{color}"'
    return (
        f'<g transform="translate({x:.1f},{y:.1f}) scale({scale:.4f})" {style}>{inner}</g>'
    )


def has_icon(name: str) -> bool:
    return name in ICON_MAP
