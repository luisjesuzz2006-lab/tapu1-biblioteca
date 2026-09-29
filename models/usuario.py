from dataclasses import dataclass
from typing import Optional

@dataclass
class Usuario:
    id: Optional[int]
    username: str
    password_hash: str
    rol: str  # 'administrador' o 'operador'
    activo: bool = True

    @property
    def es_admin(self) -> bool:
        return self.rol.lower() == 'administrador'
