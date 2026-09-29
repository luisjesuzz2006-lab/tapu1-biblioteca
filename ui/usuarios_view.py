import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from services.usuario_service import UsuarioService
from models.usuario import Usuario

class UsuariosView(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, usuario_service: UsuarioService, usuario_actual: Usuario):
        super().__init__(parent)
        self.usuario_service = usuario_service
        self.usuario_actual = usuario_actual

        self._build_ui()
        self.cargar_datos()

    def _build_ui(self):
        header_frame = ttk.Frame(self, padding=(15, 10))
        header_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(header_frame, text="Administración de Usuarios del Sistema", style='Header.TLabel')
        title_lbl.pack(side=tk.LEFT)

        # Treeview
        tree_frame = ttk.Frame(self, padding=15)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('id', 'username', 'rol', 'estado')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')

        self.tree.heading('id', text='ID')
        self.tree.heading('username', text='Usuario')
        self.tree.heading('rol', text='Rol de Acceso')
        self.tree.heading('estado', text='Estatus')

        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('username', width=200)
        self.tree.column('rol', width=150, anchor=tk.CENTER)
        self.tree.column('estado', width=100, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botonera
        btn_frame = ttk.Frame(self, padding=(15, 10))
        btn_frame.pack(fill=tk.X)

        btn_nuevo = ttk.Button(btn_frame, text="➕ Crear Usuario", style='Primary.TButton', command=self._abrir_formulario_nuevo)
        btn_nuevo.pack(side=tk.LEFT, padx=5)

        btn_toggle = ttk.Button(btn_frame, text="🔄 Activar / Desactivar", command=self._toggle_estado)
        btn_toggle.pack(side=tk.LEFT, padx=5)

    def cargar_datos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        usuarios = self.usuario_service.listar_usuarios()
        for u in usuarios:
            estado_str = "Activo" if u.activo else "Inactivo"
            self.tree.insert('', tk.END, iid=str(u.id), values=(
                u.id, u.username, u.rol.capitalize(), estado_str
            ))

    def _obtener_seleccionado_id(self) -> Optional[int]:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un usuario de la lista.")
            return None
        return int(selected[0])

    def _abrir_formulario_nuevo(self):
        NuevoUsuarioFormDialog(self, self.usuario_service, self.usuario_actual)

    def _toggle_estado(self):
        usuario_id = self._obtener_seleccionado_id()
        if not usuario_id:
            return

        user = self.usuario_service.usuario_repo.obtener_por_id(usuario_id)
        if not user:
            return

        nuevo_estado = not user.activo
        accion_str = "activar" if nuevo_estado else "desactivar"

        confirm = messagebox.askyesno(
            "Confirmar Acción",
            f"¿Está seguro de que desea {accion_str} la cuenta del usuario '{user.username}'?",
            icon='question'
        )
        if confirm:
            try:
                self.usuario_service.cambiar_estado_activo(usuario_id, nuevo_estado, self.usuario_actual.username)
                messagebox.showinfo("Éxito", f"El usuario ha sido {accion_str}do correctamente.")
                self.cargar_datos()
            except ValueError as ex:
                messagebox.showerror("Error", str(ex))


class NuevoUsuarioFormDialog:
    def __init__(self, parent_view: UsuariosView, usuario_service: UsuarioService, usuario_actual: Usuario):
        self.parent_view = parent_view
        self.usuario_service = usuario_service
        self.usuario_actual = usuario_actual

        self.dialog = tk.Toplevel(parent_view.winfo_toplevel())
        self.dialog.title("Crear Usuario del Sistema")
        self.dialog.geometry("400x320")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent_view.winfo_toplevel())
        self.dialog.grab_set()

        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self.dialog, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="Nuevo Usuario de Personal", style='Header.TLabel').pack(anchor=tk.W, pady=(0, 15))

        form = ttk.Frame(container)
        form.pack(fill=tk.BOTH, expand=True)

        ttk.Label(form, text="Usuario:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.ent_username = ttk.Entry(form, width=25)
        self.ent_username.grid(row=0, column=1, sticky=tk.W, pady=8)

        ttk.Label(form, text="Contraseña:").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.ent_pwd = ttk.Entry(form, show="•", width=25)
        self.ent_pwd.grid(row=1, column=1, sticky=tk.W, pady=8)

        ttk.Label(form, text="Rol de Acceso:").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.cmb_rol = ttk.Combobox(form, values=['operador', 'administrador'], state='readonly', width=23)
        self.cmb_rol.set('operador')
        self.cmb_rol.grid(row=2, column=1, sticky=tk.W, pady=8)

        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, pady=(15, 0))

        ttk.Button(btn_frame, text="Cancelar", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Crear Usuario", style='Primary.TButton', command=self._guardar).pack(side=tk.RIGHT, padx=5)

    def _guardar(self):
        try:
            username = self.ent_username.get()
            pwd = self.ent_pwd.get()
            rol = self.cmb_rol.get()

            self.usuario_service.crear_usuario(username, pwd, rol, self.usuario_actual.username)
            messagebox.showinfo("Éxito", f"Usuario '{username}' creado correctamente.", parent=self.dialog)
            self.parent_view.cargar_datos()
            self.dialog.destroy()
        except ValueError as ex:
            messagebox.showerror("Error de Validación", str(ex), parent=self.dialog)
