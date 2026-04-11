from dataclasses import dataclass, field
from typing import Optional

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-DO,es;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

@dataclass
class FiltrosBusqueda:
    operacion: list[str] = field(default_factory=lambda: ["alquiler", "venta"])
    ciudad: Optional[str] = "santo-domingo"
    sectores: list[str] = field(default_factory=list)
    precio_min: Optional[float] = None
    precio_max: Optional[float] = None
    habitaciones_min: Optional[int] = None
    max_paginas: int = 15
    delay: float = 1.0

# ── Configuracion por Defecto ──────────────────────────────────
FILTROS_DEFAULT = FiltrosBusqueda(
    operacion=["alquiler", "venta"],
    ciudad="santo-domingo",
    sectores=[],            
    precio_min=None,
    precio_max=None,
    habitaciones_min=None,
    max_paginas=1, # Por defecto shallow scrape
    delay=1.0,
)
