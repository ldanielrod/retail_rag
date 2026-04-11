from typing import Dict, List, Optional, Tuple

from ...core.base_scraper import BaseScraper
from ...core.config import FiltrosBusqueda
from ...core.models import AnuncioBase, AnuncioDetalle
from .fetcher import build_urls, fetch_html
from .parser import parse_detalle_anuncio, parse_lista_anuncios


class CorotosScraper(BaseScraper):
    """Scraper para corotos.com.do"""

    def build_urls(self, filtros: FiltrosBusqueda) -> List[Dict]:
        return build_urls(filtros)

    def fetch_listing_page(self, url: str, params: Optional[Dict] = None) -> str:
        return fetch_html(url, params)

    def parse_listing_page(self, html: str, page: int) -> Tuple[List[AnuncioBase], bool]:
        return parse_lista_anuncios(html, page)

    def fetch_detail_page(self, url: str) -> str:
        return fetch_html(url)

    def parse_detail_page(
        self, html: str, url: str, operacion: str, sector: str
    ) -> Optional[AnuncioDetalle]:
        return parse_detalle_anuncio(html, url, operacion, sector)
