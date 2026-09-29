from typing import List
from datetime import datetime
from db.database import DatabaseManager
from models.bitacora import BitacoraEntry

class BitacoraRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def registrar(self, usuario: str, accion: str) -> bool:
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bitacora (usuario, accion, fecha_hora)
                VALUES (?, ?, ?)
            """, (usuario, accion, fecha_hora))
            conn.commit()
            return True

    def listar_recientes(self, limite: int = 100) -> List[BitacoraEntry]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM bitacora
                ORDER BY id DESC
                LIMIT ?
            """, (limite,))
            return [BitacoraEntry(
                id=row['id'],
                usuario=row['usuario'],
                accion=row['accion'],
                fecha_hora=row['fecha_hora']
            ) for row in cursor.fetchall()]
