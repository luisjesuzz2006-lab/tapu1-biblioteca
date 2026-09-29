from typing import List, Optional
from db.database import DatabaseManager
from models.libro import Libro

class LibroRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_libro(self, row) -> Libro:
        return Libro(
            id=row['id'],
            isbn=row['isbn'],
            titulo=row['titulo'],
            autor=row['autor'],
            categoria=row['categoria'],
            anio=row['anio'],
            stock_total=row['stock_total'],
            stock_disponible=row['stock_disponible'],
            activo=bool(row['activo'])
        )

    def obtener_por_id(self, libro_id: int) -> Optional[Libro]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM libros WHERE id = ?", (libro_id,))
            row = cursor.fetchone()
            return self._row_to_libro(row) if row else None

    def obtener_por_isbn(self, isbn: str) -> Optional[Libro]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM libros WHERE isbn = ?", (isbn,))
            row = cursor.fetchone()
            return self._row_to_libro(row) if row else None

    def listar_todos(self, solo_activos: bool = False) -> List[Libro]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM libros"
            if solo_activos:
                query += " WHERE activo = 1"
            query += " ORDER BY titulo ASC"
            cursor.execute(query)
            return [self._row_to_libro(row) for row in cursor.fetchall()]

    def buscar_por_filtro(self, filtro: str, solo_activos: bool = False) -> List[Libro]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            pattern = f"%{filtro}%"
            query = """
                SELECT * FROM libros
                WHERE (isbn LIKE ? OR titulo LIKE ? OR autor LIKE ? OR categoria LIKE ?)
            """
            params = [pattern, pattern, pattern, pattern]
            if solo_activos:
                query += " AND activo = 1"
            query += " ORDER BY titulo ASC"
            cursor.execute(query, params)
            return [self._row_to_libro(row) for row in cursor.fetchall()]

    def crear(self, libro: Libro) -> Libro:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO libros (isbn, titulo, autor, categoria, anio, stock_total, stock_disponible, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (libro.isbn, libro.titulo, libro.autor, libro.categoria, libro.anio,
                  libro.stock_total, libro.stock_disponible, 1 if libro.activo else 0))
            conn.commit()
            libro.id = cursor.lastrowid
            return libro

    def actualizar(self, libro: Libro) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE libros
                SET isbn = ?, titulo = ?, autor = ?, categoria = ?, anio = ?,
                    stock_total = ?, stock_disponible = ?, activo = ?
                WHERE id = ?
            """, (libro.isbn, libro.titulo, libro.autor, libro.categoria, libro.anio,
                  libro.stock_total, libro.stock_disponible, 1 if libro.activo else 0, libro.id))
            conn.commit()
            return cursor.rowcount > 0

    def cambiar_estado_activo(self, libro_id: int, activo: bool) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE libros SET activo = ? WHERE id = ?", (1 if activo else 0, libro_id))
            conn.commit()
            return cursor.rowcount > 0

    def actualizar_stock_disponible(self, libro_id: int, delta: int, conn: Optional[sqlite3.Connection] = None) -> bool:
        """Suma o resta al stock disponible (delta +1 o -1). Debe invocarse dentro de una transacción si se pasa conn."""
        query = "UPDATE libros SET stock_disponible = stock_disponible + ? WHERE id = ?"
        if conn:
            cursor = conn.cursor()
            cursor.execute(query, (delta, libro_id))
            return cursor.rowcount > 0
        else:
            with self.db.get_connection() as c:
                cursor = c.cursor()
                cursor.execute(query, (delta, libro_id))
                c.commit()
                return cursor.rowcount > 0
