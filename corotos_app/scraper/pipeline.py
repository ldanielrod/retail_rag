import time
from typing import List, Dict
import pandas as pd

from ..core.config import FiltrosBusqueda
from .fetcher import build_urls, fetch_html
from .parser import parse_lista_anuncios, parse_detalle_anuncio
from .processor import aplicar_filtros

def ejecutar_scraper(filtros: FiltrosBusqueda) -> List[Dict]:
    """
    Ejecuta el scraper silenciosamente usando los filtros dados.
    """
    urls_busqueda = build_urls(filtros)
    todos: List[Dict] = []
    urls_vistas: set[str] = set()

    for busqueda in urls_busqueda:
        op       = busqueda["operacion"]
        sector   = busqueda["sector"]
        base_url = busqueda["url"]

        for page in range(1, filtros.max_paginas + 1):
            try:
                html_lista = fetch_html(base_url, params={"page": str(page)})
                items, hay_siguiente = parse_lista_anuncios(html_lista, page)
            except Exception:
                break

            nuevos = [i for i in items if i.url not in urls_vistas]
            if not nuevos: break

            for item in nuevos:
                urls_vistas.add(item.url)
                try:
                    print(f"🤖 Scrapeando: {item.titulo[:40]}...")
                    html_detalle = fetch_html(item.url)
                    detalle = parse_detalle_anuncio(html_detalle, item.url, op, sector)
                    todos.append(detalle.to_dict())
                    time.sleep(filtros.delay)
                except Exception:
                    pass

            if not hay_siguiente:
                break
            time.sleep(filtros.delay)

    # Filtrar antes de devolver
    if todos:
        df = pd.DataFrame(todos).drop_duplicates(subset="url").reset_index(drop=True)
        df = aplicar_filtros(df, filtros)
        return df.to_dict("records")
    return []
