import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional
from services.prestamo_service import PrestamoService
from services.libro_service import LibroService
from services.lector_service import LectorService
from models.usuario import Usuario

class PrestamosView(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, prestamo_service: PrestamoService,
                 libro_service: LibroService, lector_service: LectorService, usuario_actual: Usuario):
        super().__init__(parent)
        self.prestamo_service = prestamo_service
        self.libro_service = libro_service
        self.lector_service = lector_service
        self.usuario_actual = usuario_actual

        self._build_ui()
        self.cargar_datos()

    def _build_ui(self):
        # Header / Barra Superior
        header_frame = ttk.Frame(self, padding=(15, 10))
        header_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(header_frame, text="Gestión de Préstamos (Movimiento de Negocio)", style='Header.TLabel')
        title_lbl.pack(side=tk.LEFT)

        # Buscador y Filtro de Estado
        filter_frame = ttk.Frame(header_frame)
        filter_frame.pack(side=tk.RIGHT)

        ttk.Label(filter_frame, text="Estado:").pack(side=tk.LEFT, padx=(0, 5))
        self.cmb_estado = ttk.Combobox(filter_frame, values=['Todos', 'Activo', 'Devuelto'], state='readonly', width=10)
        self.cmb_estado.set('Todos')
        self.cmb_estado.pack(side=tk.LEFT, padx=(0, 10))
        self.cmb_estado.bind('<<ComboboxSelected>>', lambda e: self.cargar_datos())

        ttk.Label(filter_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        self.ent_buscar = ttk.Entry(filter_frame, width=20)
        self.ent_buscar.pack(side=tk.LEFT, padx=(0, 5))
        self.ent_buscar.bind('<KeyRelease>', lambda e: self.cargar_datos())

        # Tabla Treeview con JOIN
        tree_frame = ttk.Frame(self, padding=15)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('id', 'folio', 'lector', 'isbn', 'libro', 'f_prestamo', 'f_venc', 'f_dev', 'estado')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')

        self.tree.heading('id', text='ID')
        self.tree.heading('folio', text='Folio Lector')
        self.tree.heading('lector', text='Lector')
        self.tree.heading('isbn', text='ISBN Libro')
        self.tree.heading('libro', text='Título Libro')
        self.tree.heading('f_prestamo', text='Préstamo')
        self.tree.heading('f_venc', text='Vencimiento')
        self.tree.heading('f_dev', text='Devolución')
        self.tree.heading('estado', text='Estatus')

        self.tree.column('id', width=40, anchor=tk.CENTER)
        self.tree.column('folio', width=90)
        self.tree.column('lector', width=180)
        self.tree.column('isbn', width=110)
        self.tree.column('libro', width=200)
        self.tree.column('f_prestamo', width=90, anchor=tk.CENTER)
        self.tree.column('f_venc', width=90, anchor=tk.CENTER)
        self.tree.column('f_dev', width=90, anchor=tk.CENTER)
        self.tree.column('estado', width=80, anchor=tk.CENTER)

        # Tags de colores para indicar atrasos
        self.tree.tag_configure('atrasado', background='#fee2e2', foreground='#991b1b')
        self.tree.tag_configure('devuelto', background='#f1f5f9', foreground='#64748b')

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botonera inferior
        btn_frame = ttk.Frame(self, padding=(15, 10))
        btn_frame.pack(fill=tk.X)

        btn_nuevo = ttk.Button(btn_frame, text="➕ Registrar Préstamo", style='Primary.TButton', command=self._abrir_formulario_prestamo)
        btn_nuevo.pack(side=tk.LEFT, padx=5)

        btn_devolucion = ttk.Button(btn_frame, text="↩️ Registrar Devolución", command=self._registrar_devolucion)
        btn_devolucion.pack(side=tk.LEFT, padx=5)

    def cargar_datos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        filtro = self.ent_buscar.get()
        estado_filtro = self.cmb_estado.get()

        prestamos = self.prestamo_service.listar_prestamos_join(filtro=filtro, estado=estado_filtro)
        hoy_str = datetime.now().date().isoformat()

        for p in prestamos:
            f_dev_str = p.fecha_devolucion if p.fecha_devolucion else "---"
            tag = ""
            if p.estado == 'activo' and p.fecha_vencimiento < hoy_str:
                tag = 'atrasado'
            elif p.estado == 'devuelto':
                tag = 'devuelto'

            self.tree.insert('', tk.END, iid=str(p.id), values=(
                p.id, p.lector_folio, p.lector_nombre, p.libro_isbn, p.libro_titulo,
                p.fecha_prestamo, p.fecha_vencimiento, f_dev_str, p.estado.capitalize()
            ), tags=(tag,))

    def _obtener_seleccionado_id(self) -> Optional[int]:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección requerida", "Por favor seleccione un préstamo de la lista.")
            return None
        return int(selected[0])

    def _abrir_formulario_prestamo(self):
        NuevoPrestamoFormDialog(self, self.prestamo_service, self.libro_service, self.lector_service, self.usuario_actual)

    def _registrar_devolucion(self):
        prestamo_id = self._obtener_seleccionado_id()
        if not prestamo_id:
            return

        prestamo = self.prestamo_service.prestamo_repo.obtener_por_id(prestamo_id)
        if not prestamo:
            return

        if prestamo.estado == 'devuelto':
            messagebox.showinfo("Información", "El préstamo ya fue devuelto anteriormente.")
            return

        # RF-9: Confirmación con messagebox
        confirm = messagebox.askyesno(
            "Confirmar Devolución",
            f"¿Desea registrar la devolución del libro '{prestamo.libro_titulo}' prestado a '{prestamo.lector_nombre}'?",
            icon='question'
        )
        if confirm:
            try:
                self.prestamo_service.registrar_devolucion(prestamo_id, self.usuario_actual.username)
                messagebox.showinfo("Éxito", "La devolución del libro ha sido registrada correctamente. Stock actualizado.")
                self.cargar_datos()
            except ValueError as ex:
                messagebox.showerror("Error", str(ex))


class NuevoPrestamoFormDialog:
    def __init__(self, parent_view: PrestamosView, prestamo_service: PrestamoService,
                 libro_service: LibroService, lector_service: LectorService, usuario_actual: Usuario):
        self.parent_view = parent_view
        self.prestamo_service = prestamo_service
        self.libro_service = libro_service
        self.lector_service = lector_service
        self.usuario_actual = usuario_actual

        self.dialog = tk.Toplevel(parent_view.winfo_toplevel())
        self.dialog.title("Registrar Nuevo Préstamo")
        self.dialog.geometry("520x450")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent_view.winfo_toplevel())
        self.dialog.grab_set()

        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self.dialog, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="Nuevo Préstamo de Libro", style='Header.TLabel').pack(anchor=tk.W, pady=(0, 15))

        # Cargar lectores activos y libros disponibles
        self.lectores_activos = self.lector_service.listar_lectores(solo_activos=True)
        self.libros_disponibles = [l for l in self.libro_service.listar_libros(solo_activos=True) if l.stock_disponible > 0]

        form = ttk.Frame(container)
        form.pack(fill=tk.BOTH, expand=True)

        # Lector combobox
        ttk.Label(form, text="Seleccionar Lector (Activo):", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W, pady=(5, 2))
        lectores_display = [f"{l.folio} - {l.nombre} ({l.tipo.capitalize()})" for l in self.lectores_activos]
        self.cmb_lector = ttk.Combobox(form, values=lectores_display, state='readonly', width=55)
        self.cmb_lector.pack(fill=tk.X, pady=(0, 15))
        if lectores_display:
            self.cmb_lector.set(lectores_display[0])

        # Libro combobox
        ttk.Label(form, text="Seleccionar Libro (Stock > 0):", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W, pady=(5, 2))
        libros_display = [f"{b.isbn} - {b.titulo} (Disp: {b.stock_disponible}/{b.stock_total})" for b in self.libros_disponibles]
        self.cmb_libro = ttk.Combobox(form, values=libros_display, state='readonly', width=55)
        self.cmb_libro.pack(fill=tk.X, pady=(0, 15))
        if libros_display:
            self.cmb_libro.set(libros_display[0])

        # Nota de vigencia
        info_frame = ttk.LabelFrame(container, text=" Información de Préstamo ", padding=10)
        info_frame.pack(fill=tk.X, pady=10)
        ttk.Label(info_frame, text="• El préstamo se emite con una vigencia de 7 días naturales.", font=('Segoe UI', 9)).pack(anchor=tk.W)
        ttk.Label(info_frame, text="• Se descontará 1 unidad automáticamente del stock disponible.", font=('Segoe UI', 9)).pack(anchor=tk.W)

        # Botones
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, pady=(15, 0))

        ttk.Button(btn_frame, text="Cancelar", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Confirmar Préstamo", style='Primary.TButton', command=self._guardar_prestamo).pack(side=tk.RIGHT, padx=5)

    def _guardar_prestamo(self):
        idx_lector = self.cmb_lector.current()
        idx_libro = self.cmb_libro.current()

        if idx_lector < 0 or not self.lectores_activos:
            messagebox.showerror("Error", "Debe seleccionar un lector válido de la lista.", parent=self.dialog)
            return
        if idx_libro < 0 or not self.libros_disponibles:
            messagebox.showerror("Error", "Debe seleccionar un libro válido con stock disponible.", parent=self.dialog)
            return

        lector_sel = self.lectores_activos[idx_lector]
        libro_sel = self.libros_disponibles[idx_libro]

        try:
            self.prestamo_service.registrar_prestamo(
                lector_id=lector_sel.id,
                libro_id=libro_sel.id,
                usuario_actual=self.usuario_actual.username
            )

            messagebox.showinfo("Éxito", f"Préstamo registrado exitosamente.\nLibro: {libro_sel.titulo}\nLector: {lector_sel.nombre}", parent=self.dialog)
            self.parent_view.cargar_datos()
            self.dialog.destroy()
        except ValueError as ex:
            messagebox.showerror("Regla de Negocio Violada", str(ex), parent=self.dialog)
