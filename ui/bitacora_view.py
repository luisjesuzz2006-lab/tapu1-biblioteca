import tkinter as tk
from tkinter import ttk
from repositories.bitacora_repository import BitacoraRepository

class BitacoraView(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, bitacora_repo: BitacoraRepository):
        super().__init__(parent)
        self.bitacora_repo = bitacora_repo

        self._build_ui()
        self.cargar_datos()

    def _build_ui(self):
        header_frame = ttk.Frame(self, padding=(15, 10))
        header_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(header_frame, text="Bitácora de Acciones (Historial de Auditoría)", style='Header.TLabel')
        title_lbl.pack(side=tk.LEFT)

        btn_refresh = ttk.Button(header_frame, text="🔄 Actualizar Log", command=self.cargar_datos)
        btn_refresh.pack(side=tk.RIGHT)

        tree_frame = ttk.Frame(self, padding=15)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('id', 'fecha', 'usuario', 'accion')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')

        self.tree.heading('id', text='ID')
        self.tree.heading('fecha', text='Fecha y Hora')
        self.tree.heading('usuario', text='Usuario en Sesión')
        self.tree.heading('accion', text='Acción Registrada')

        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('fecha', width=140, anchor=tk.CENTER)
        self.tree.column('usuario', width=130)
        self.tree.column('accion', width=450)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def cargar_datos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        entries = self.bitacora_repo.listar_recientes(150)
        for e in entries:
            self.tree.insert('', tk.END, iid=str(e.id), values=(
                e.id, e.fecha_hora, e.usuario, e.accion
            ))
