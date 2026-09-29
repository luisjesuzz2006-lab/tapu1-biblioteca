import tkinter as tk
from tkinter import ttk, messagebox
from services.usuario_service import UsuarioService
from models.usuario import Usuario

class LoginWindow:
    def __init__(self, parent: tk.Tk, usuario_service: UsuarioService):
        self.parent = parent
        self.usuario_service = usuario_service
        self.usuario_logueado: Usuario = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Inicio de Sesión - Biblioteca TAP")
        self.dialog.geometry("420x460")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Centrar ventana
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

        self._build_ui()
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        container = ttk.Frame(self.dialog, padding=25)
        container.pack(fill=tk.BOTH, expand=True)

        # Header Icon/Title
        title_label = ttk.Label(
            container,
            text="📚 Biblioteca Central",
            font=('Segoe UI', 18, 'bold')
        )
        title_label.pack(pady=(0, 5))

        subtitle_label = ttk.Label(
            container,
            text="Tópicos Avanzados de Programación",
            font=('Segoe UI', 10),
            foreground='#64748b'
        )
        subtitle_label.pack(pady=(0, 20))

        # Form Group
        form_frame = ttk.LabelFrame(container, text=" Acceso al Sistema ", padding=15)
        form_frame.pack(fill=tk.X, pady=10)

        # Username
        ttk.Label(form_frame, text="Usuario:", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W, pady=(5, 2))
        self.ent_username = ttk.Entry(form_frame, font=('Segoe UI', 10))
        self.ent_username.pack(fill=tk.X, pady=(0, 10))
        self.ent_username.insert(0, "admin")  # Prefill para comodidad del usuario

        # Password
        ttk.Label(form_frame, text="Contraseña:", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W, pady=(5, 2))
        self.ent_password = ttk.Entry(form_frame, show="•", font=('Segoe UI', 10))
        self.ent_password.pack(fill=tk.X, pady=(0, 15))
        self.ent_password.insert(0, "admin123")  # Prefill para comodidad del usuario

        # Botón Iniciar Sesión
        btn_login = ttk.Button(
            form_frame,
            text="Iniciar Sesión",
            style='Primary.TButton',
            command=self._intentar_login
        )
        btn_login.pack(fill=tk.X, pady=5)

        # Tecla Enter para enviar
        self.dialog.bind('<Return>', lambda e: self._intentar_login())

        # Indicador de Credenciales de prueba
        info_frame = ttk.Frame(container)
        info_frame.pack(fill=tk.X, pady=(15, 0))
        ttk.Label(info_frame, text="Usuarios de prueba:", font=('Segoe UI', 8, 'bold')).pack(anchor=tk.W)
        ttk.Label(info_frame, text="• Admin: admin / admin123\n• Operador: operador / operador123", font=('Segoe UI', 8), foreground='#64748b').pack(anchor=tk.W)

    def _intentar_login(self):
        username = self.ent_username.get()
        password = self.ent_password.get()

        try:
            user = self.usuario_service.autenticar(username, password)
            self.usuario_logueado = user
            self.dialog.destroy()
        except ValueError as ex:
            messagebox.showerror("Error de Autenticación", str(ex), parent=self.dialog)

    def _on_close(self):
        self.usuario_logueado = None
        self.dialog.destroy()
        self.parent.destroy()
