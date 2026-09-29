from dataclasses import dataclass
from typing import Optional

@dataclass
class Prestamo:
    id: Optional[int]
    lector_id: int
    libro_id: int
    fecha_prestamo: str    # ISO format YYYY-MM-DD
    fecha_vencimiento: str # ISO format YYYY-MM-DD
    fecha_devolucion: Optional[str]  # ISO format YYYY-MM-DD or None
    estado: str  # 'activo' o 'devuelto'

    # Campos opcionales poblados por SQL JOIN
    lector_folio: Optional[str] = None
    lector_nombre: Optional[str] = None
    libro_isbn: Optional[str] = None
    libro_titulo: Optional[str] = None
