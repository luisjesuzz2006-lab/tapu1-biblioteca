from typing import List, Optional
from db.database import DatabaseManager
from models.usuario import Usuario

class UsuarioRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_usuario(self, row) -> Usuario:
        return Usuario(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            rol=row['rol'],
            activo=bool(row['activo'])
        )

    def obtener_por_username(self, username: str) -> Optional[Usuario]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios_sistema WHERE username = ?", (username,))
            row = cursor.fetchone()
            return self._row_to_usuario(row) if row else None

    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios_sistema WHERE id = ?", (usuario_id,))
            row = cursor.fetchone()
            return self._row_to_usuario(row) if row else None

    def listar_todos((self) -> List[Usuario]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios_sistema ORDER BY username ASC")
            rows = cursor.fetchall()
            return [self._row_to_usuario(row) for row in rows]

    def crear(self, usuario: Usuario) -> Usuario:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usuarios_sistema (username, password_hash, rol, activo)
                VALUES (?, ?, ?, ?)
            """, (usuario.username, usuario.password_hash, usuario.rol, 1 if usuario.activo else 0))
            conn.commit()
            usuario.id = cursor.lastrowid
            return usuario

    def actualizar(self, usuario: Usuario) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE usuarios_sistema
                SET username = ?, password_hash = ?, rol = ?, activo = ?
                WHERE id = ?
            """, (usuario.username, usuario.password_hash, usuario.rol, 1 if usuario.activo else 0, usuario.id))
            conn.commit()
            return cursor.rowcount > 0
