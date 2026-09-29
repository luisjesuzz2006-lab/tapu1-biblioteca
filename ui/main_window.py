import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import ThemeManager
from ui.libros_view import LibrosView
from ui.lectores_view import LectoresView
from ui.prestamos_view import PrestamosView
from ui.reportes_view import ReportesView
from ui.usuarios_view import UsuariosView
from ui.bitacora_view import BitacoraView
from services.usuario_service import UsuarioService
from services.libro_service import LibroService
from services.lector_service import LectorService
from services.prestamo_service import PrestamoService
from services.reporte_service import ReporteService
from repositories.bitacora_repository import BitacoraRepository
from models.usuario import Usuario

class MainWindow:
    def __init__(self, root: tk.Tk, usuario_actual: Usuario,
                 usuario_service: UsuarioService, libro_service: LibroService,
                 lector_service: LectorService, prestamo_service: PrestamoService,
                 reporte_service: ReporteService, bitacora_repo: BitacoraRepository):

        self.root = root
        self.usuario_actual = usuario_actual
        self.usuario_service = usuario_service
        self.libro_service = libro_service
        self.lector_service = lector_service
        self.prestamo_service = prestamo_service
        self.reporte_service = reporte_service
        self.bitacora_repo = bitacora_repo

        self.theme_manager = ThemeManager(root)

        self.root.title("Biblioteca Central TAP - Sistema de Gestión")
        self.root.geometry("1100x680")
        self.root.minsize(900, 580)

        # Centrar ventana principal
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        self._crear_menu_bar()
        self._build_ui()

    def _crear_menu_bar(self):
        menubar = tk.Menu(self.root)

        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menu_archivo.add_command(label="Cambiar Tema (Claro/Oscuro)", command=self._toggle_tema)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Cerrar Sesión", command=self._cerrar_sesion)
        menu_archivo.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)

        # Menú Catálogos
        menu_catalogos = tk.Menu(menubar, tearoff=0)
        menu_catalogos.add_command(label="Libros", command=lambda: self.notebook.select(0))
        menu_catalogos.add_command(label="Lectores", command=lambda: self.notebook.select(1))
        menubar.add_cascade(label="Catálogos", menu=menu_catalogos)

        # Menú Préstamos
        menu_prestamos = tk.Menu(menubar, tearoff=0)
        menu_prestamos.add_command(label="Gestión de Préstamos", command=lambda: self.notebook.select(2))
        menubar.add_cascade(label="Movimientos", menu=menu_prestamos)

        # Menú Reportes
        menu_reportes = tk.Menu(menubar, tearoff=0)
        menu_reportes.add_command(label="Préstamos Atrasados (CSV & Gráfica)", command=lambda: self.notebook.select(3))
        menubar.add_cascade(label="Reportes", menu=menu_reportes)

        # Menú Ayuda
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menu_ayuda.add_command(label="Acerca de", command=self._mostrar_acerca_de)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)

        self.root.config(menu=menubar)

    def _build_ui(self):
        # Header Banner
        header = ttk.Frame(self.root, padding=(20, 10), style='Card.TFrame')
        header.pack(fill=tk.X)

        title_lbl = ttk.Label(header, text="📚 Biblioteca Central TAP", font=('Segoe UI', 16, 'bold'))
        title_lbl.pack(side=tk.LEFT)

        # Info de usuario activo
        user_info_frame = ttk.Frame(header)
        user_info_frame.pack(side=tk.RIGHT)

        user_text = f"👤 {self.usuario_actual.username} ({self.usuario_actual.rol.capitalize()})"
        ttk.Label(user_info_frame, text=user_text, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 15))

        btn_theme = ttk.Button(user_info_frame, text="🌓 Tema", command=self._toggle_tema)
        btn_theme.pack(side=tk.LEFT, padx=(0, 10))

        btn_logout = ttk.Button(user_info_frame, text="🚪 Salir", command=self._cerrar_sesion)
        btn_logout.pack(side=tk.LEFT)

        # Notebook (Pestañas)
        self.notebook = ttk.Notebook(self.root, padding=10)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Pestaña 1: Libros
        self.libros_view = LibrosView(self.notebook, self.libro_service, self.usuario_actual)
        self.notebook.add(self.libros_view, text=" 📖 Libros ")

        # Pestaña 2: Lectores
        self.lectores_view = LectoresView(self.notebook, self.lector_service, self.usuario_actual)
        self.notebook.add(self.lectores_view, text=" 👥 Lectores ")

        # Pestaña 3: Préstamos
        self.prestamos_view = PrestamosView(
            self.notebook, self.prestamo_service, self.libro_service, self.lector_service, self.usuario_actual
        )
        self.notebook.add(self.prestamos_view, text=" 🔄 Préstamos ")

        # Pestaña 4: Reportes
        self.reportes_view = ReportesView(self.notebook, self.reporte_service, self.usuario_actual)
        self.notebook.add(self.reportes_view, text=" 📊 Reportes ")

        # Pestaña 5: Bitácora
        self.bitacora_view = BitacoraView(self.notebook, self.bitacora_repo)
        self.notebook.add(self.bitacora_view, text=" 📜 Bitácora ")

        # Pestaña 6: Usuarios del Sistema (Solo Administrador)
        if self.usuario_actual.es_admin:
            self.usuarios_view = UsuariosView(self.notebook, self.usuario_service, self.usuario_actual)
            self.notebook.add(self.usuarios_view, text=" ⚙️ Usuarios ")

        # Evento de cambio de pestaña para actualizar datos
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event):
        selected_tab = self.notebook.select()
        widget = self.notebook.nametowidget(selected_tab)
        if hasattr(widget, 'cargar_datos'):
            widget.cargar_datos()

    def _toggle_tema(self):
        nuevo_tema = self.theme_manager.toggle_theme()
        # Refrescar vista actual
        self._on_tab_changed(None)

    def _cerrar_sesion(self):
        confirm = messagebox.askyesno("Cerrar Sesión", "¿Está seguro de que desea cerrar la sesión actual?")
        if confirm:
            self.bitacora_repo.registrar(self.usuario_actual.username, "Cierre de sesión")
            self.root.destroy()

    def _mostrar_acerca_de(self):
        messagebox.showinfo(
            "Acerca de",
            "Biblioteca Central TAP v1.0\n"
            "Proyecto Final - Tópicos Avanzados de Programación (Unidad 1)\n\n"
            "• Lenguaje: Python 3.10+\n"
            "• Interfaz: Tkinter / ttk\n"
            "• Persistencia: SQLite 3 con Foreign Keys\n"
            "• Arquitectura: Layered OOP (UI / Models / Repositories / Services)\n"
            "• Opción 1: Sistema de Biblioteca"
        )
