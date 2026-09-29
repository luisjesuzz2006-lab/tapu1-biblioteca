import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from services.lector_service import LectorService
from models.usuario import Usuario
from models.lector import Lector

class LectoresView(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, lector_service: LectorService, usuario_actual: Usuario):
        super().__init__(parent)
        self.lector_service = lector_service
        self.usuario_actual = usuario_actual

        self._build_ui()
        self.cargar_datos()

    def _build_ui(self):
        # Header / Barra Superior
        header_frame = ttk.Frame(self, padding=(15, 10))
        header_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(header_frame, text="Padrón de Lectores", style='Header.TLabel')
        title_lbl.pack(side=tk.LEFT)

        # Buscador
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT)

        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        self.ent_buscar = ttk.Entry(search_frame, width=25)
        self.ent_buscar.pack(side=tk.LEFT, padx=(0, 5))
        self.ent_buscar.bind('<KeyRelease>', lambda e: self.cargar_datos())

        # Tabla Treeview
        tree_frame = ttk.Frame(self, padding=15)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('id', 'folio', 'nombre', 'correo', 'telefono', 'tipo', 'estado')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')

        self.tree.heading('id', text='ID')
        self.tree.heading('folio', text='Folio')
        self.tree.heading('nombre', text='Nombre Completo')
        self.tree.heading('correo', text='Correo Electrónico')
        self.tree.heading('telefono', text='Teléfono')
        self.tree.heading('tipo', text='Tipo')
        self.tree.heading('estado', text='Estatus')

        self.tree.column('id', width=40, anchor=tk.CENTER)
        self.tree.column('folio', width=100)
        self.tree.column('nombre', width=220)
        self.tree.column('correo', width=200)
        self.tree.column('telefono', width=120)
        self.tree.column('tipo', width=100, anchor=tk.CENTER)
        self.tree.column('estado', width=80, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botonera inferior
        btn_frame = ttk.Frame(self, padding=(15, 10))
        btn_frame.pack(fill=tk.X)

        btn_nuevo = ttk.Button(btn_frame, text="➕ Nuevo Lector", style='Primary.TButton', command=self._abrir_formulario_nuevo)
        btn_nuevo.pack(side=tk.LEFT, padx=5)

        btn_editar = ttk.Button(btn_frame, text="✏️ Editar Lector", command=self._abrir_formulario_editar)
        btn_editar.pack(side=tk.LEFT, padx=5)

        btn_cambiar_estado = ttk.Button(btn_frame, text="🔄 Activar / Desactivar", command=self._toggle_estado)
        btn_cambiar_estado.pack(side=tk.LEFT, padx=5)

    def cargar_datos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        filtro = self.ent_buscar.get()
        lectores = self.lector_service.listar_lectores(filtro=filtro)

        for l in lectores:
            estado_str = "Activo" if l.activo else "Inactivo"
            self.tree.insert('', tk.END, iid=str(l.id), values=(
                l.id, l.folio, l.nombre, l.correo, l.telefono, l.tipo.capitalize(), estado_str
            ))

    def _obtener_seleccionado_id(self) -> Optional[int]:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un lector de la lista.")
            return None
        return int(selected[0])

    def _abrir_formulario_nuevo(self):
        LectorFormDialog(self, self.lector_service, self.usuario_actual, None)

    def _abrir_formulario_editar(self):
        lector_id = self._obtener_seleccionado_id()
        if lector_id:
            LectorFormDialog(self, self.lector_service, self.usuario_actual, lector_id)

    def _toggle_estado(self):
        lector_id = self._obtener_seleccionado_id()
        if not lector_id:
            return

        lector = self.lector_service.obtener_lector(lector_id)
        if not lector:
            return

        nuevo_estado = not lector.activo
        accion_str = "activar" if nuevo_estado else "desactivar"

        # RF-9: Confirmación con messagebox
        confirm = messagebox.askyesno(
            "Confirmar Acción",
            f"¿Está seguro de que desea {accion_str} al lector '{lector.nombre}'?",
            icon='question'
        )
        if confirm:
            try:
                self.lector_service.desactivar_o_activar_lector(lector_id, nuevo_estado, self.usuario_actual.username)
                messagebox.showinfo("Éxito", f"El lector ha sido {accion_str}do correctamente.")
                self.cargar_datos()
            except ValueError as ex:
                # RF-10 & RNF-4: Captura de error de integridad sin caídas
                messagebox.showerror("Error de Integridad", str(ex))


class LectorFormDialog:
    def __init__(self, parent_view: LectoresView, lector_service: LectorService, usuario_actual: Usuario, lector_id: Optional[int]):
        self.parent_view = parent_view
        self.lector_service = lector_service
        self.usuario_actual = usuario_actual
        self.lector_id = lector_id

        self.dialog = tk.Toplevel(parent_view.winfo_toplevel())
        self.dialog.title("Editar Lector" if lector_id else "Nuevo Lector")
        self.dialog.geometry("450x450")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent_view.winfo_toplevel())
        self.dialog.grab_set()

        self._build_ui()
        if lector_id:
            self._cargar_datos_lector()

    def _build_ui(self):
        container = ttk.Frame(self.dialog, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="Formulario de Lector", style='Header.TLabel').pack(anchor=tk.W, pady=(0, 15))

        form = ttk.Frame(container)
        form.pack(fill=tk.BOTH, expand=True)

        # Folio
        ttk.Label(form, text="Folio:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.ent_folio = ttk.Entry(form, width=30)
        self.ent_folio.grid(row=0, column=1, sticky=tk.W, pady=8)

        # Nombre
        ttk.Label(form, text="Nombre Completo:").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.ent_nombre = ttk.Entry(form, width=30)
        self.ent_nombre.grid(row=1, column=1, sticky=tk.W, pady=8)

        # Correo
        ttk.Label(form, text="Correo Electrónico:").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.ent_correo = ttk.Entry(form, width=30)
        self.ent_correo.grid(row=2, column=1, sticky=tk.W, pady=8)

        # Teléfono
        ttk.Label(form, text="Teléfono:").grid(row=3, column=0, sticky=tk.W, pady=8)
        self.ent_telefono = ttk.Entry(form, width=30)
        self.ent_telefono.grid(row=3, column=1, sticky=tk.W, pady=8)

        # Tipo
        ttk.Label(form, text="Tipo de Lector:").grid(row=4, column=0, sticky=tk.W, pady=8)
        self.cmb_tipo = ttk.Combobox(form, values=['alumno', 'docente', 'externo'], state='readonly', width=28)
        self.cmb_tipo.set('alumno')
        self.cmb_tipo.grid(row=4, column=1, sticky=tk.W, pady=8)

        # Estatus
        self.var_activo = tk.BooleanVar(value=True)
        chk_activo = ttk.Checkbutton(form, text="Lector Activo", variable=self.var_activo)
        chk_activo.grid(row=5, column=1, sticky=tk.W, pady=10)

        # Botones
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, pady=(15, 0))

        ttk.Button(btn_frame, text="Cancelar", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Guardar", style='Primary.TButton', command=self._guardar).pack(side=tk.RIGHT, padx=5)

    def _cargar_datos_lector(self):
        lector = self.lector_service.obtener_lector(self.lector_id)
        if lector:
            self.ent_folio.insert(0, lector.folio)
            self.ent_nombre.insert(0, lector.nombre)
            self.ent_correo.insert(0, lector.correo)
            self.ent_telefono.insert(0, lector.telefono)
            self.cmb_tipo.set(lector.tipo)
            self.var_activo.set(lector.activo)

    def _guardar(self):
        try:
            folio = self.ent_folio.get()
            nombre = self.ent_nombre.get()
            correo = self.ent_correo.get()
            telefono = self.ent_telefono.get()
            tipo = self.cmb_tipo.get()
            activo = self.var_activo.get()

            self.lector_service.guardar_lector(
                self.lector_id, folio, nombre, correo, telefono, tipo, activo, self.usuario_actual.username
            )

            messagebox.showinfo("Éxito", "El lector se ha guardado correctamente.", parent=self.dialog)
            self.parent_view.cargar_datos()
            self.dialog.destroy()
        except ValueError as ex:
            messagebox.showerror("Error de Validación", str(ex), parent=self.dialog)
