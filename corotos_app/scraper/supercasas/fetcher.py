import requests
from typing import Dict, List, Optional

from ...core.config import HEADERS, FiltrosBusqueda
from .config import BASE_URL


def build_urls(filtros: FiltrosBusqueda) -> List[Dict]:
    urls = []
    for op in filtros.operacion:
        url = f"{BASE_URL}/apartamentos-{op}-{filtros.ciudad}" if filtros.ciudad else f"{BASE_URL}/apartamentos-{op}"
        urls.append({"url": url, "operacion": op, "sector": "todos"})
    return urls


def fetch_html(url: str, params: Optional[Dict[str, str]] = None) -> str:
    resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.text
