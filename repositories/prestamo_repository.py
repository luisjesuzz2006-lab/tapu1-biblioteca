from typing import List, Optional
from datetime import datetime
from db.database import DatabaseManager
from models.prestamo import Prestamo

class PrestamoRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_prestamo(self, row) -> Prestamo:
        return Prestamo(
            id=row['id'],
            lector_id=row['lector_id'],
            libro_id=row['libro_id'],
            fecha_prestamo=row['fecha_prestamo'],
            fecha_vencimiento=row['fecha_vencimiento'],
            fecha_devolucion=row['fecha_devolucion'],
            estado=row['estado'],
            lector_folio=row['lector_folio'] if 'lector_folio' in row.keys() else None,
            lector_nombre=row['lector_nombre'] if 'lector_nombre' in row.keys() else None,
            libro_isbn=row['libro_isbn'] if 'libro_isbn' in row.keys() else None,
            libro_titulo=row['libro_titulo'] if 'libro_titulo' in row.keys() else None
        )

    def obtener_por_id(self, prestamo_id: int) -> Optional[Prestamo]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, l.folio as lector_folio, l.nombre as lector_nombre,
                       b.isbn as libro_isbn, b.titulo as libro_titulo
                FROM prestamos p
                JOIN lectores l ON p.lector_id = l.id
                JOIN libros b ON p.libro_id = b.id
                WHERE p.id = ?
            """, (prestamo_id,))
            row = cursor.fetchone()
            return self._row_to_prestamo(row) if row else None

    def listar_con_join(self, filtro: str = "", estado_filtro: str = "todos") -> List[Prestamo]:
        """Consulta SQL obligatoria con JOIN relacionando Préstamos, Lectores y Libros."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT p.id, p.lector_id, p.libro_id, p.fecha_prestamo,
                       p.fecha_vencimiento, p.fecha_devolucion, p.estado,
                       l.folio as lector_folio, l.nombre as lector_nombre,
                       b.isbn as libro_isbn, b.titulo as libro_titulo
                FROM prestamos p
                JOIN lectores l ON p.lector_id = l.id
                JOIN libros b ON p.libro_id = b.id
                WHERE 1=1
            """
            params = []

            if estado_filtro.lower() in ('activo', 'devuelto'):
                query += " AND p.estado = ?"
                params.append(estado_filtro.lower())

            if filtro.strip():
                pattern = f"%{filtro.strip()}%"
                query += """ AND (l.folio LIKE ? OR l.nombre LIKE ? OR b.isbn LIKE ? OR b.titulo LIKE ?)"""
                params.extend([pattern, pattern, pattern, pattern])

            query += " ORDER BY p.id DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_prestamo(row) for row in rows]

    def listar_prestamos_atrasados(self, fecha_referencia: Optional[str] = None) -> List[Prestamo]:
        """Reporte problemático del dominio: Préstamos activos cuya fecha de vencimiento es previa a la fecha actual."""
        if not fecha_referencia:
            fecha_referencia = datetime.now().date().isoformat()

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT p.id, p.lector_id, p.libro_id, p.fecha_prestamo,
                       p.fecha_vencimiento, p.fecha_devolucion, p.estado,
                       l.folio as lector_folio, l.nombre as lector_nombre,
                       b.isbn as libro_isbn, b.titulo as libro_titulo
                FROM prestamos p
                JOIN lectores l ON p.lector_id = l.id
                JOIN libros b ON p.libro_id = b.id
                WHERE p.estado = 'activo' AND p.fecha_vencimiento < ?
                ORDER BY p.fecha_vencimiento ASC
            """
            cursor.execute(query, (fecha_referencia,))
            return [self._row_to_prestamo(row) for row in cursor.fetchall()]

    def contar_prestamos_activos_por_lector_y_libro(self, lector_id: int, libro_id: int) -> int:
        """Verifica si un lector ya posee un préstamo activo del mismo libro."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as cant FROM prestamos
                WHERE lector_id = ? AND libro_id = ? AND estado = 'activo'
            """, (lector_id, libro_id))
            return cursor.fetchone()['cant']

    def contar_prestamos_activos_por_lector(self, lector_id: int) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as cant FROM prestamos
                WHERE lector_id = ? AND estado = 'activo'
            """, (lector_id,))
            return cursor.fetchone()['cant']

    def contar_prestamos_activos_por_libro(self, libro_id: int) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as cant FROM prestamos
                WHERE libro_id = ? AND estado = 'activo'
            """, (libro_id,))
            return cursor.fetchone()['cant']

    def registrar_prestamo_transaccional(self, prestamo: Prestamo) -> Prestamo:
        """Registra un nuevo préstamo y descuenta 1 del stock disponible en una única transacción atómica."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # 1. Insertar préstamo
            cursor.execute("""
                INSERT INTO prestamos (lector_id, libro_id, fecha_prestamo, fecha_vencimiento, fecha_devolucion, estado)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (prestamo.lector_id, prestamo.libro_id, prestamo.fecha_prestamo,
                  prestamo.fecha_vencimiento, prestamo.fecha_devolucion, prestamo.estado))
            prestamo_id = cursor.lastrowid

            # 2. Descontar stock disponible del libro
            cursor.execute("""
                UPDATE libros
                SET stock_disponible = stock_disponible - 1
                WHERE id = ? AND stock_disponible > 0
            """, (prestamo.libro_id,))

            if cursor.rowcount == 0:
                raise ValueError("No hay stock disponible suficiente para realizar el préstamo del libro.")

            conn.commit()
            prestamo.id = prestamo_id
            return prestamo

    def registrar_devolucion_transaccional(self, prestamo_id: int, fecha_devolucion: str) -> bool:
        """Registra la devolución de un libro e incrementa el stock disponible en una transacción atómica."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # Obtener datos del préstamo
            cursor.execute("SELECT libro_id, estado FROM prestamos WHERE id = ?", (prestamo_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError("El préstamo especificado no existe.")
            if row['estado'] == 'devuelto':
                raise ValueError("El préstamo ya se encuentra marcado como devuelto.")

            libro_id = row['libro_id']

            # 1. Actualizar préstamo a devuelto
            cursor.execute("""
                UPDATE prestamos
                SET estado = 'devuelto', fecha_devolucion = ?
                WHERE id = ? AND estado = 'activo'
            """, (fecha_devolucion, prestamo_id))

            # 2. Incrementar stock disponible sin exceder el stock total
            cursor.execute("""
                UPDATE libros
                SET stock_disponible = stock_disponible + 1
                WHERE id = ? AND stock_disponible < stock_total
            """, (libro_id,))

            conn.commit()
            return True
