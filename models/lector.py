from dataclasses import dataclass
from typing import Optional

@dataclass
class Lector:
    id: Optional[int]
    folio: str
    nombre: str
    correo: str
    telefono: str
    tipo: str  # 'alumno', 'docente', 'externo'
    activo: bool = True
