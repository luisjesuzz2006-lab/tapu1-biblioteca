from dataclasses import dataclass
from typing import Optional

@dataclass
class BitacoraEntry:
    id: Optional[int]
    usuario: str
    accion: str
    fecha_hora: str
