from typing import List, Optional
from db.database import DatabaseManager
from models.lector import Lector

class LectorRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_lector(self, row) -> Lector:
        return Lector(
            id=row['id'],
            folio=row['folio'],
            nombre=row['nombre'],
            correo=row['correo'],
            telefono=row['telefono'],
            tipo=row['tipo'],
            activo=bool(row['activo'])
        )

    def obtener_por_id(self, lector_id: int) -> Optional[Lector]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lectores WHERE id = ?", (lector_id,))
            row = cursor.fetchone()
            return self._row_to_lector(row) if row else None

    def obtener_por_folio(self, folio: str) -> Optional[Lector]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lectores WHERE folio = ?", (folio,))
            row = cursor.fetchone()
            return self._row_to_lector(row) if row else None

    def obtener_por_correo(self, correo: str) -> Optional[Lector]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lectores WHERE correo = ?", (correo,))
            row = cursor.fetchone()
            return self._row_to_lector(row) if row else None

    def listar_todos(self, solo_activos: bool = False) -> List[Lector]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM lectores"
            if solo_activos:
                query += " WHERE activo = 1"
            query += " ORDER BY nombre ASC"
            cursor.execute(query)
            return [self._row_to_lector(row) for row in cursor.fetchall()]

    def buscar_por_filtro(self, filtro: str, solo_activos: bool = False) -> List[Lector]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            pattern = f"%{filtro}%"
            query = """
                SELECT * FROM lectores
                WHERE (folio LIKE ? OR nombre LIKE ? OR correo LIKE ? OR telefono LIKE ? OR tipo LIKE ?)
            """
            params = [pattern, pattern, pattern, pattern, pattern]
            if solo_activos:
                query += " AND activo = 1"
            query += " ORDER BY nombre ASC"
            cursor.execute(query, params)
            return [self._row_to_lector(row) for row in cursor.fetchall()]

    def crear(self, lector: Lector) -> Lector:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lectores (folio, nombre, correo, telefono, tipo, activo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (lector.folio, lector.nombre, lector.correo, lector.telefono, lector.tipo, 1 if lector.activo else 0))
            conn.commit()
            lector.id = cursor.lastrowid
            return lector

    def actualizar(self, lector: Lector) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE lectores
                SET folio = ?, nombre = ?, correo = ?, telefono = ?, tipo = ?, activo = ?
                WHERE id = ?
            """, (lector.folio, lector.nombre, lector.correo, lector.telefono, lector.tipo,
                  1 if lector.activo else 0, lector.id))
            conn.commit()
            return cursor.rowcount > 0

    def cambiar_estado_activo(self, lector_id: int, activo: bool) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE lectores SET activo = ? WHERE id = ?", (1 if activo else 0, lector_id))
            conn.commit()
            return cursor.rowcount > 0
