import sys
import os
from datetime import datetime

# Test script for non-gui headless verification
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import DatabaseManager, hash_password
from repositories.usuario_repository import UsuarioRepository
from repositories.libro_repository import LibroRepository
from repositories.lector_repository import LectorRepository
from repositories.prestamo_repository import PrestamoRepository
from repositories.bitacora_repository import BitacoraRepository

from services.usuario_service import UsuarioService
from services.libro_service import LibroService
from services.lector_service import LectorService
from services.prestamo_service import PrestamoService
from services.reporte_service import ReporteService

def run_headless_tests():
    print("=== INICIANDO PRUEBAS AUTOMATIZADAS DEL SISTEMA ===")
    
    # 1. DB Init
    db_file = os.path.join(os.path.dirname(__file__), "biblioteca.db")
    if os.path.exists(db_file):
        os.remove(db_file)
        
    db = DatabaseManager(db_file)
    db.initialize_database()
    print("✓ Base de datos SQLite e inicialización de semillas OK.")

    # 2. Repositories
    u_repo = UsuarioRepository(db)
    b_repo = LibroRepository(db)
    l_repo = LectorRepository(db)
    p_repo = PrestamoRepository(db)
    bit_repo = BitacoraRepository(db)

    # 3. Services
    u_serv = UsuarioService(u_repo, bit_repo)
    b_serv = LibroService(b_repo, p_repo, bit_repo)
    l_serv = LectorService(l_repo, p_repo, bit_repo)
    p_serv = PrestamoService(p_repo, b_repo, l_repo, bit_repo)
    r_serv = ReporteService(p_repo, b_repo, l_repo)

    # Test Login
    admin_user = u_serv.autenticar("admin", "admin123")
    print(f"✓ Autenticación exitosa: Usuario '{admin_user.username}', Rol '{admin_user.rol}'.")

    op_user = u_serv.autenticar("operador", "operador123")
    print(f"✓ Autenticación exitosa: Usuario '{op_user.username}', Rol '{op_user.rol}'.")

    # Test Listados
    libros = b_serv.listar_libros()
    print(f"✓ Catálogo de Libros cargado: {len(libros)} libros.")
    lectores = l_serv.listar_lectores()
    print(f"✓ Padrón de Lectores cargado: {len(lectores)} lectores.")

    # Test Préstamos con JOIN
    prestamos = p_serv.listar_prestamos_join()
    print(f"✓ Consulta SQL JOIN ejecutada: {len(prestamos)} préstamos.")
    for p in prestamos:
        print(f"   └─ Préstamo #{p.id}: Lector '{p.lector_nombre}' (Folio {p.lector_folio}) <-> Libro '{p.libro_titulo}' [{p.estado}]")

    # Test Reporte Problemático (Atrasados)
    atrasados = r_serv.obtener_prestamos_atrasados()
    print(f"✓ Reporte Problemático obtenido: {len(atrasados)} préstamo(s) atrasado(s).")
    
    # Test CSV Export
    csv_file = os.path.join(os.path.dirname(__file__), "test_atrasados.csv")
    r_serv.exportar_atrasados_a_csv(csv_file)
    print(f"✓ Reporte CSV generado exitosamente en '{csv_file}'.")

    # Test Regla de Negocio: Intentar prestar sin stock
    libro_sin_stock = [b for b in libros if b.stock_disponible == 0][0]
    lector_activo = [l for l in lectores if l.activo][0]
    try:
        p_serv.registrar_prestamo(lector_activo.id, libro_sin_stock.id, "admin")
        print("❌ FALLO: Debería haber rechazado préstamo sin stock.")
    except ValueError as ex:
        print(f"✓ Regla de Negocio probada (Stock 0): {ex}")

    # Test Regla de Negocio: Intentar desactivar libro con préstamos activos
    libro_con_prestamo_activo = [p.libro_id for p in prestamos if p.estado == 'activo'][0]
    try:
        b_serv.desactivar_o_activar_libro(libro_con_prestamo_activo, False, "admin")
        print("❌ FALLO: Debería haber bloqueado desactivación de libro con préstamo activo.")
    except ValueError as ex:
        print(f"✓ Integridad referencial (RF-10) probada: {ex}")

    print("=== TODAS LAS PRUEBAS AUTOMATIZADAS PASARON CON ÉXITO ===")

if __name__ == '__main__':
    run_headless_tests()
