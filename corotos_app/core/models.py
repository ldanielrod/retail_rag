from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class AnuncioBase:
    titulo: str
    precio_texto: str
    url: str

@dataclass
class AnuncioDetalle:
    titulo: str
    operacion: str
    sector_buscado: str
    precio_texto: str
    precio_num: Optional[float]
    moneda: str
    habitaciones: Optional[int]
    banos: Optional[int]
    metros_m2: Optional[int]
    amueblado: str
    ubicacion: str
    url: str

    def to_dict(self):
        return asdict(self)
