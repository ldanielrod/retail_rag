import time
from typing import Dict, List, Optional
import pandas as pd

from ..core.base_scraper import BaseScraper
from ..core.config import FiltrosBusqueda
from .processor import aplicar_filtros


def ejecutar_scraper(
    filtros: FiltrosBusqueda,
    scrapers: Optional[List[BaseScraper]] = None,
) -> List[Dict]:
    """
    Ejecuta uno o varios scrapers usando los filtros dados.

    Args:
        filtros:  Configuración de búsqueda (ciudad, precio, páginas, etc.)
        scrapers: Lista de scrapers a ejecutar. Si se omite, usa CorotosScraper
                  por defecto. Para agregar otro sitio, pasa sus instancias aquí:
                      ejecutar_scraper(filtros, scrapers=[CorotosScraper(), OtroSitioScraper()])
    """
    if scrapers is None:
        from .corotos.scraper import CorotosScraper
        scrapers = [CorotosScraper()]

    todos: List[Dict] = []
    urls_vistas: set[str] = set()

    for scraper in scrapers:
        urls_busqueda = scraper.build_urls(filtros)

        for busqueda in urls_busqueda:
            op       = busqueda["operacion"]
            sector   = busqueda["sector"]
            base_url = busqueda["url"]

            for page in range(1, filtros.max_paginas + 1):
                try:
                    html_lista = scraper.fetch_listing_page(base_url, params={"page": str(page)})
                    items, hay_siguiente = scraper.parse_listing_page(html_lista, page)
                except Exception:
                    break

                nuevos = [i for i in items if i.url not in urls_vistas]
                if not nuevos:
                    break

                for item in nuevos:
                    urls_vistas.add(item.url)
                    try:
                        print(f"🤖 Scrapeando: {item.titulo[:40]}...")
                        html_detalle = scraper.fetch_detail_page(item.url)
                        detalle = scraper.parse_detail_page(html_detalle, item.url, op, sector)
                        if detalle:
                            todos.append(detalle.to_dict())
                        time.sleep(filtros.delay)
                    except Exception:
                        pass

                if not hay_siguiente:
                    break
                time.sleep(filtros.delay)

    if todos:
        df = pd.DataFrame(todos).drop_duplicates(subset="url").reset_index(drop=True)
        df = aplicar_filtros(df, filtros)
        return df.to_dict("records")
    return []
