import sys
import os
import tkinter as tk
from tkinter import messagebox

# Agregar directorio actual al sys.path para importaciones limpias
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import DatabaseManager
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

from ui.login_window import LoginWindow
from ui.main_window import MainWindow

def main():
    # 1. Inicialización de la base de datos (RF-1: Crea el archivo .db y tablas automáticamente)
    db_manager = DatabaseManager()
    try:
        db_manager.initialize_database()
    except Exception as ex:
        root_tmp = tk.Tk()
        root_tmp.withdraw()
        messagebox.showerror("Error Crítico de Base de Datos", f"No se pudo inicializar la base de datos:\n{str(ex)}")
        return

    # 2. Instanciación de Repositorios (Capa de Acceso a Datos - SQL)
    usuario_repo = UsuarioRepository(db_manager)
    libro_repo = LibroRepository(db_manager)
    lector_repo = LectorRepository(db_manager)
    prestamo_repo = PrestamoRepository(db_manager)
    bitacora_repo = BitacoraRepository(db_manager)

    # 3. Instanciación de Servicios (Capa de Lógica de Negocio)
    usuario_service = UsuarioService(usuario_repo, bitacora_repo)
    libro_service = LibroService(libro_repo, prestamo_repo, bitacora_repo)
    lector_service = LectorService(lector_repo, prestamo_repo, bitacora_repo)
    prestamo_service = PrestamoService(prestamo_repo, libro_repo, lector_repo, bitacora_repo)
    reporte_service = ReporteService(prestamo_repo, libro_repo, lector_repo)

    # 4. Crear ventana principal de Tkinter
    root = tk.Tk()
    root.withdraw()  # Ocultar mientras se solicita el login

    # 5. Invocar Pantalla de Login (RF-2, RF-3)
    login_dialog = LoginWindow(root, usuario_service)
    root.wait_window(login_dialog.dialog)

    usuario_autenticado = login_dialog.usuario_logueado

    if not usuario_autenticado:
        # Si el usuario canceló o cerró el login
        root.destroy()
        sys.exit(0)

    # 6. Mostrar ventana principal de la aplicación (MainWindow)
    root.deiconify()
    app = MainWindow(
        root=root,
        usuario_actual=usuario_autenticado,
        usuario_service=usuario_service,
        libro_service=libro_service,
        lector_service=lector_service,
        prestamo_service=prestamo_service,
        reporte_service=reporte_service,
        bitacora_repo=bitacora_repo
    )

    root.mainloop()

if __name__ == '__main__':
    main()
