import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from services.libro_service import LibroService
from models.usuario import Usuario
from models.libro import Libro

class LibrosView(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, libro_service: LibroService, usuario_actual: Usuario):
        super().__init__(parent)
        self.libro_service = libro_service
        self.usuario_actual = usuario_actual

        self._build_ui()
        self.cargar_datos()

    def _build_ui(self):
        # Header / Barra Superior
        header_frame = ttk.Frame(self, padding=(15, 10))
        header_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(header_frame, text="Catálogo de Libros", style='Header.TLabel')
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

        columns = ('id', 'isbn', 'titulo', 'autor', 'categoria', 'anio', 'stock_total', 'stock_disp', 'estado')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')

        self.tree.heading('id', text='ID')
        self.tree.heading('isbn', text='ISBN')
        self.tree.heading('titulo', text='Título')
        self.tree.heading('autor', text='Autor')
        self.tree.heading('categoria', text='Categoría')
        self.tree.heading('anio', text='Año')
        self.tree.heading('stock_total', text='Stock Total')
        self.tree.heading('stock_disp', text='Stock Disp.')
        self.tree.heading('estado', text='Estatus')

        self.tree.column('id', width=40, anchor=tk.CENTER)
        self.tree.column('isbn', width=120)
        self.tree.column('titulo', width=220)
        self.tree.column('autor', width=150)
        self.tree.column('categoria', width=110)
        self.tree.column('anio', width=60, anchor=tk.CENTER)
        self.tree.column('stock_total', width=80, anchor=tk.CENTER)
        self.tree.column('stock_disp', width=80, anchor=tk.CENTER)
        self.tree.column('estado', width=80, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botonera inferior
        btn_frame = ttk.Frame(self, padding=(15, 10))
        btn_frame.pack(fill=tk.X)

        btn_nuevo = ttk.Button(btn_frame, text="➕ Nuevo Libro", style='Primary.TButton', command=self._abrir_formulario_nuevo)
        btn_nuevo.pack(side=tk.LEFT, padx=5)

        btn_editar = ttk.Button(btn_frame, text="✏️ Editar Libro", command=self._abrir_formulario_editar)
        btn_editar.pack(side=tk.LEFT, padx=5)

        btn_cambiar_estado = ttk.Button(btn_frame, text="🔄 Activar / Desactivar", command=self._toggle_estado)
        btn_cambiar_estado.pack(side=tk.LEFT, padx=5)

    def cargar_datos(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        filtro = self.ent_buscar.get()
        libros = self.libro_service.listar_libros(filtro=filtro)

        for l in libros:
            estado_str = "Activo" if l.activo else "Inactivo"
            self.tree.insert('', tk.END, iid=str(l.id), values=(
                l.id, l.isbn, l.titulo, l.autor, l.categoria, l.anio, l.stock_total, l.stock_disponible, estado_str
            ))

    def _obtener_seleccionado_id(self) -> Optional[int]:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un libro de la lista.")
            return None
        return int(selected[0])

    def _abrir_formulario_nuevo(self):
        LibroFormDialog(self, self.libro_service, self.usuario_actual, None)

    def _abrir_formulario_editar(self):
        libro_id = self._obtener_seleccionado_id()
        if libro_id:
            LibroFormDialog(self, self.libro_service, self.usuario_actual, libro_id)

    def _toggle_estado(self):
        libro_id = self._obtener_seleccionado_id()
        if not libro_id:
            return

        libro = self.libro_service.obtener_libro(libro_id)
        if not libro:
            return

        nuevo_estado = not libro.activo
        accion_str = "activar" if nuevo_estado else "desactivar"

        # RF-9: Confirmación con messagebox
        confirm = messagebox.askyesno(
            "Confirmar Acción",
            f"¿Está seguro de que desea {accion_str} el libro '{libro.titulo}'?",
            icon='question'
        )
        if confirm:
            try:
                self.libro_service.desactivar_o_activar_libro(libro_id, nuevo_estado, self.usuario_actual.username)
                messagebox.showinfo("Éxito", f"El libro ha sido {accion_str}do correctamente.")
                self.cargar_datos()
            except ValueError as ex:
                # RF-10 & RNF-4: Manejo seguro de excepciones sin caídas
                messagebox.showerror("Error de Integridad", str(ex))


class LibroFormDialog:
    def __init__(self, parent_view: LibrosView, libro_service: LibroService, usuario_actual: Usuario, libro_id: Optional[int]):
        self.parent_view = parent_view
        self.libro_service = libro_service
        self.usuario_actual = usuario_actual
        self.libro_id = libro_id

        self.dialog = tk.Toplevel(parent_view.winfo_toplevel())
        self.dialog.title("Editar Libro" if libro_id else "Nuevo Libro")
        self.dialog.geometry("450x520")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent_view.winfo_toplevel())
        self.dialog.grab_set()

        self._build_ui()
        if libro_id:
            self._cargar_datos_libro()

    def _build_ui(self):
        container = ttk.Frame(self.dialog, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="Formulario de Libro", style='Header.TLabel').pack(anchor=tk.W, pady=(0, 15))

        form = ttk.Frame(container)
        form.pack(fill=tk.BOTH, expand=True)

        # ISBN
        ttk.Label(form, text="ISBN:").grid(row=0, column=0, sticky=tk.W, pady=6)
        self.ent_isbn = ttk.Entry(form, width=30)
        self.ent_isbn.grid(row=0, column=1, sticky=tk.W, pady=6)

        # Título
        ttk.Label(form, text="Título:").grid(row=1, column=0, sticky=tk.W, pady=6)
        self.ent_titulo = ttk.Entry(form, width=30)
        self.ent_titulo.grid(row=1, column=1, sticky=tk.W, pady=6)

        # Autor
        ttk.Label(form, text="Autor:").grid(row=2, column=0, sticky=tk.W, pady=6)
        self.ent_autor = ttk.Entry(form, width=30)
        self.ent_autor.grid(row=2, column=1, sticky=tk.W, pady=6)

        # Categoría
        ttk.Label(form, text="Categoría:").grid(row=3, column=0, sticky=tk.W, pady=6)
        self.ent_categoria = ttk.Entry(form, width=30)
        self.ent_categoria.grid(row=3, column=1, sticky=tk.W, pady=6)

        # Año
        ttk.Label(form, text="Año de Pub.:").grid(row=4, column=0, sticky=tk.W, pady=6)
        self.ent_anio = ttk.Entry(form, width=15)
        self.ent_anio.grid(row=4, column=1, sticky=tk.W, pady=6)

        # Stock Total
        ttk.Label(form, text="Stock Total:").grid(row=5, column=0, sticky=tk.W, pady=6)
        self.ent_stock_total = ttk.Entry(form, width=15)
        self.ent_stock_total.grid(row=5, column=1, sticky=tk.W, pady=6)

        # Stock Disponible
        ttk.Label(form, text="Stock Disponible:").grid(row=6, column=0, sticky=tk.W, pady=6)
        self.ent_stock_disp = ttk.Entry(form, width=15)
        self.ent_stock_disp.grid(row=6, column=1, sticky=tk.W, pady=6)

        # Estatus
        self.var_activo = tk.BooleanVar(value=True)
        chk_activo = ttk.Checkbutton(form, text="Registro Activo", variable=self.var_activo)
        chk_activo.grid(row=7, column=1, sticky=tk.W, pady=10)

        # Botones
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, pady=(15, 0))

        ttk.Button(btn_frame, text="Cancelar", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Guardar", style='Primary.TButton', command=self._guardar).pack(side=tk.RIGHT, padx=5)

    def _cargar_datos_libro(self):
        libro = self.libro_service.obtener_libro(self.libro_id)
        if libro:
            self.ent_isbn.insert(0, libro.isbn)
            self.ent_titulo.insert(0, libro.titulo)
            self.ent_autor.insert(0, libro.autor)
            self.ent_categoria.insert(0, libro.categoria)
            self.ent_anio.insert(0, str(libro.anio))
            self.ent_stock_total.insert(0, str(libro.stock_total))
            self.ent_stock_disp.insert(0, str(libro.stock_disponible))
            self.var_activo.set(libro.activo)

    def _guardar(self):
        # RNF-4: Capturar errores de conversión de tipo sin tumbar la app
        try:
            isbn = self.ent_isbn.get()
            titulo = self.ent_titulo.get()
            autor = self.ent_autor.get()
            categoria = self.ent_categoria.get()

            try:
                anio = int(self.ent_anio.get())
            except ValueError:
                raise ValueError("El campo 'Año' debe ser un número entero válido.")

            try:
                stock_total = int(self.ent_stock_total.get())
            except ValueError:
                raise ValueError("El campo 'Stock Total' debe ser un número entero válido.")

            try:
                stock_disp = int(self.ent_stock_disp.get())
            except ValueError:
                raise ValueError("El campo 'Stock Disponible' debe ser un número entero válido.")

            activo = self.var_activo.get()

            self.libro_service.guardar_libro(
                self.libro_id, isbn, titulo, autor, categoria, anio, stock_total, stock_disp, activo, self.usuario_actual.username
            )

            messagebox.showinfo("Éxito", "El libro se ha guardado correctamente.", parent=self.dialog)
            self.parent_view.cargar_datos()
            self.dialog.destroy()
        except ValueError as ex:
            messagebox.showerror("Error de Validación", str(ex), parent=self.dialog)
