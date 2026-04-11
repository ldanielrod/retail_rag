import requests
from typing import Dict, List, Optional
from urllib.parse import quote

from ...core.config import HEADERS, FiltrosBusqueda
from .config import BASE_URL


def build_urls(filtros: FiltrosBusqueda) -> List[Dict]:
    urls = []
    ciudad_slug = filtros.ciudad or ""
    for op in filtros.operacion:
        categoria = f"inmuebles-en-{op}"
        if filtros.sectores:
            for sector in filtros.sectores:
                sector_slug = quote(sector)
                url = (
                    f"{BASE_URL}/l/{ciudad_slug}/sc/{categoria}/apartamentos/{sector_slug}"
                    if ciudad_slug
                    else f"{BASE_URL}/sc/{categoria}/apartamentos/{sector_slug}"
                )
                urls.append({"url": url, "operacion": op, "sector": sector})
        else:
            url = (
                f"{BASE_URL}/l/{ciudad_slug}/sc/{categoria}/apartamentos"
                if ciudad_slug
                else f"{BASE_URL}/sc/{categoria}/apartamentos"
            )
            urls.append({"url": url, "operacion": op, "sector": "todos"})
    return urls


def fetch_html(url: str, params: Optional[Dict[str, str]] = None) -> str:
    resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.text
