from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from .models import AnuncioBase, AnuncioDetalle
from .config import FiltrosBusqueda


class BaseScraper(ABC):
    """
    Interfaz que debe implementar cada scraper de sitio.

    Para agregar un nuevo sitio, crea una clase que herede de BaseScraper
    e implementa los 5 métodos abstractos. Luego pásala a ejecutar_scraper().

    Ejemplo:
        class MiSitioScraper(BaseScraper):
            def build_urls(self, filtros): ...
            def fetch_listing_page(self, url, params=None): ...
            def parse_listing_page(self, html, page): ...
            def fetch_detail_page(self, url): ...
            def parse_detail_page(self, html, url, operacion, sector): ...

        resultados = ejecutar_scraper(filtros, scrapers=[MiSitioScraper()])
    """

    @abstractmethod
    def build_urls(self, filtros: FiltrosBusqueda) -> List[Dict]:
        """Devuelve lista de dicts {url, operacion, sector} a recorrer."""

    @abstractmethod
    def fetch_listing_page(self, url: str, params: Optional[Dict] = None) -> str:
        """Descarga el HTML de una página de listado."""

    @abstractmethod
    def parse_listing_page(self, html: str, page: int) -> Tuple[List[AnuncioBase], bool]:
        """
        Extrae los anuncios de una página de listado.
        Devuelve (lista_de_anuncios, hay_siguiente_pagina).
        """

    @abstractmethod
    def fetch_detail_page(self, url: str) -> str:
        """Descarga el HTML de la página de detalle de un anuncio."""

    @abstractmethod
    def parse_detail_page(
        self, html: str, url: str, operacion: str, sector: str
    ) -> Optional[AnuncioDetalle]:
        """Extrae el AnuncioDetalle de la página de detalle. Retorna None si falla."""
