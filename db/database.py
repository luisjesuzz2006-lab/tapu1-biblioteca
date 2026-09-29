import sqlite3
import hashlib
import os
from datetime import datetime, timedelta

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "biblioteca.db")

def hash_password(password: str) -> str:
    """Genera hash SHA-256 para contraseñas."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

class DatabaseManager:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def initialize_database(self):
        """Crea las tablas y realiza la siembra inicial de datos de prueba."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Tabla usuarios_sistema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios_sistema (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    rol TEXT NOT NULL CHECK(rol IN ('administrador', 'operador')),
                    activo INTEGER NOT NULL DEFAULT 1
                );
            """)

            # 2. Tabla libros
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS libros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isbn TEXT UNIQUE NOT NULL,
                    titulo TEXT NOT NULL,
                    autor TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    anio INTEGER NOT NULL,
                    stock_total INTEGER NOT NULL CHECK(stock_total >= 0),
                    stock_disponible INTEGER NOT NULL CHECK(stock_disponible >= 0),
                    activo INTEGER NOT NULL DEFAULT 1
                );
            """)

            # 3. Tabla lectores
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lectores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    folio TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    correo TEXT UNIQUE NOT NULL,
                    telefono TEXT NOT NULL,
                    tipo TEXT NOT NULL CHECK(tipo IN ('alumno', 'docente', 'externo')),
                    activo INTEGER NOT NULL DEFAULT 1
                );
            """)

            # 4. Tabla prestamos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prestamos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lector_id INTEGER NOT NULL,
                    libro_id INTEGER NOT NULL,
                    fecha_prestamo TEXT NOT NULL,
                    fecha_vencimiento TEXT NOT NULL,
                    fecha_devolucion TEXT,
                    estado TEXT NOT NULL CHECK(estado IN ('activo', 'devuelto')),
                    FOREIGN KEY (lector_id) REFERENCES lectores (id),
                    FOREIGN KEY (libro_id) REFERENCES libros (id)
                );
            """)

            # 5. Tabla bitacora (Extra)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bitacora (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT NOT NULL,
                    accion TEXT NOT NULL,
                    fecha_hora TEXT NOT NULL
                );
            """)

            # Siembra de usuarios iniciales si la tabla está vacía
            cursor.execute("SELECT COUNT(*) as cant FROM usuarios_sistema")
            if cursor.fetchone()['cant'] == 0:
                cursor.execute("""
                    INSERT INTO usuarios_sistema (username, password_hash, rol, activo)
                    VALUES (?, ?, ?, 1)
                """, ('admin', hash_password('admin123'), 'administrador'))

                cursor.execute("""
                    INSERT INTO usuarios_sistema (username, password_hash, rol, activo)
                    VALUES (?, ?, ?, 1)
                """, ('operador', hash_password('operador123'), 'operador'))

            # Siembra de Libros de prueba
            cursor.execute("SELECT COUNT(*) as cant FROM libros")
            if cursor.fetchone()['cant'] == 0:
                libros_data = [
                    ('978-0131103627', 'El Lenguaje de Programación C', 'Brian W. Kernighan', 'Programación', 1988, 5, 5, 1),
                    ('978-0132350884', 'Clean Code: A Handbook of Agile Software Craftsmanship', 'Robert C. Martin', 'Ingeniería de Software', 2008, 4, 2, 1),
                    ('978-0201616224', 'The Pragmatic Programmer', 'Andrew Hunt & David Thomas', 'Ingeniería de Software', 1999, 4, 3, 1),
                    ('978-0596007126', 'Head First Design Patterns', 'Eric Freeman', 'Patrones de Diseño', 2004, 2, 0, 1),
                    ('978-0321573513', 'Algorithms 4th Edition', 'Robert Sedgewick', 'Algoritmos', 2011, 3, 3, 1),
                    ('978-0134685991', 'Effective Java', 'Joshua Bloch', 'Programación', 2017, 3, 3, 1),
                    ('978-1449355739', 'Learning Python', 'Mark Lutz', 'Programación', 2013, 4, 4, 1),
                    ('978-0262033848', 'Introduction to Algorithms', 'Thomas H. Cormen', 'Algoritmos', 2009, 2, 2, 1),
                    ('978-0000000000', 'Enciclopedia Desactualizada (Inactivo)', 'Varios Autores', 'General', 1990, 0, 0, 0)
                ]
                cursor.executemany("""
                    INSERT INTO libros (isbn, titulo, autor, categoria, anio, stock_total, stock_disponible, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, libros_data)

            # Siembra de Lectores de prueba
            cursor.execute("SELECT COUNT(*) as cant FROM lectores")
            if cursor.fetchone()['cant'] == 0:
                lectores_data = [
                    ('LEC-001', 'Juan Pérez Gómez', 'juan.perez@alumnos.edu.mx', '555-1234', 'alumno', 1),
                    ('LEC-002', 'Dra. María Rodríguez', 'maria.rodriguez@profesores.edu.mx', '555-5678', 'docente', 1),
                    ('LEC-003', 'Carlos Eduardo López', 'carlos.lopez@alumnos.edu.mx', '555-8765', 'alumno', 1),
                    ('LEC-004', 'Ing. Ana Sofía Martínez', 'ana.martinez@externo.org', '555-4321', 'externo', 1),
                    ('LEC-005', 'Luis Fernando Hernández', 'luis.hernandez@alumnos.edu.mx', '555-9988', 'alumno', 1),
                    ('LEC-006', 'Pedro Inactivo Gómez', 'pedro.inactivo@test.com', '555-0000', 'alumno', 0)
                ]
                cursor.executemany("""
                    INSERT INTO lectores (folio, nombre, correo, telefono, tipo, activo)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, lectores_data)

            # Siembra de Préstamos de prueba
            cursor.execute("SELECT COUNT(*) as cant FROM prestamos")
            if cursor.fetchone()['cant'] == 0:
                hoy = datetime.now().date()
                hace_3_dias = (hoy - timedelta(days=3)).isoformat()
                vence_en_4 = (hoy + timedelta(days=4)).isoformat()

                hace_15_dias = (hoy - timedelta(days=15)).isoformat()
                vencio_hace_8 = (hoy - timedelta(days=8)).isoformat()

                hace_20_dias = (hoy - timedelta(days=20)).isoformat()
                vencio_hace_13 = (hoy - timedelta(days=13)).isoformat()
                devuelto_hace_12 = (hoy - timedelta(days=12)).isoformat()

                # Obtener IDs reales
                cursor.execute("SELECT id FROM lectores WHERE folio = 'LEC-001'")
                lec1_id = cursor.fetchone()['id']
                cursor.execute("SELECT id FROM lectores WHERE folio = 'LEC-003'")
                lec3_id = cursor.fetchone()['id']
                cursor.execute("SELECT id FROM lectores WHERE folio = 'LEC-002'")
                lec2_id = cursor.fetchone()['id']

                cursor.execute("SELECT id FROM libros WHERE isbn = '978-0132350884'") # Clean Code
                lib_cleancode = cursor.fetchone()['id']
                cursor.execute("SELECT id FROM libros WHERE isbn = '978-0201616224'") # Pragmatic Programmer
                lib_pragmatic = cursor.fetchone()['id']

                prestamos_seed = [
                    # 1. Préstamo Vigente (LEC-001 -> Clean Code)
                    (lec1_id, lib_cleancode, hace_3_dias, vence_en_4, None, 'activo'),
                    # 2. Préstamo Atrasado / Problemático (LEC-003 -> Pragmatic Programmer)
                    (lec3_id, lib_pragmatic, hace_15_dias, vencio_hace_8, None, 'activo'),
                    # 3. Préstamo Devuelto / Cerrado (LEC-002 -> Clean Code)
                    (lec2_id, lib_cleancode, hace_20_dias, vencio_hace_13, devuelto_hace_12, 'devuelto')
                ]

                cursor.executemany("""
                    INSERT INTO prestamos (lector_id, libro_id, fecha_prestamo, fecha_vencimiento, fecha_devolucion, estado)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, prestamos_seed)

                # Registrar auditoría de inicio
                cursor.execute("""
                    INSERT INTO bitacora (usuario, accion, fecha_hora)
                    VALUES ('sistema', 'Inicialización automática de base de datos y datos de prueba', ?)
                """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))

            conn.commit()
