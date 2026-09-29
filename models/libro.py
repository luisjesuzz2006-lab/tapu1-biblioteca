from dataclasses import dataclass
from typing import Optional

@dataclass
class Libro:
    id: Optional[int]
    isbn: str
    titulo: str
    autor: str
    categoria: str
    anio: int
    stock_total: int
    stock_disponible: int
    activo: bool = True

    @property
    def esta_disponible(self) -> bool:
        return self.activo and self.stock_disponible > 0
