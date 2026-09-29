import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from services.reporte_service import ReporteService
from models.usuario import Usuario

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class ReportesView(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, reporte_service: ReporteService, usuario_actual: Usuario):
        super().__init__(parent)
        self.reporte_service = reporte_service
        self.usuario_actual = usuario_actual

        self._build_ui()
        self.cargar_datos()

    def _build_ui(self):
        # Header / Barra Superior
        header_frame = ttk.Frame(self, padding=(15, 10))
        header_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(header_frame, text="Reporte Problemático: Préstamos Atrasados", style='Header.TLabel')
        title_lbl.pack(side=tk.LEFT)

        btn_csv = ttk.Button(header_frame, text="📥 Exportar Reporte a CSV", style='Primary.TButton', command=self._exportar_csv)
        btn_csv.pack(side=tk.RIGHT)

        # Contenedor Split: Tabla arriba / Gráfica abajo
        split_frame = ttk.PanedWindow(self, orient=tk.VERTICAL)
        split_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Frame Tabla Atrasados
        tbl_frame = ttk.LabelFrame(split_frame, text=" Préstamos Vencidos No Devueltos ", padding=10)
        split_frame.add(tbl_frame, weight=1)

        columns = ('id', 'folio', 'lector', 'isbn', 'libro', 'f_prestamo', 'f_venc', 'dias_atraso')
        self.tree = ttk.Treeview(tbl_frame, columns=columns, show='headings', selectmode='browse')

        self.tree.heading('id', text='ID')
        self.tree.heading('folio', text='Folio Lector')
        self.tree.heading('lector', text='Nombre Lector')
        self.tree.heading('isbn', text='ISBN Libro')
        self.tree.heading('libro', text='Título Libro')
        self.tree.heading('f_prestamo', text='Fecha Préstamo')
        self.tree.heading('f_venc', text='Fecha Vencimiento')
        self.tree.heading('dias_atraso', text='Días Atraso')

        self.tree.column('id', width=40, anchor=tk.CENTER)
        self.tree.column('folio', width=90)
        self.tree.column('lector', width=180)
        self.tree.column('isbn', width=110)
        self.tree.column('libro', width=220)
        self.tree.column('f_prestamo', width=100, anchor=tk.CENTER)
        self.tree.column('f_venc', width=100, anchor=tk.CENTER)
        self.tree.column('dias_atraso', width=80, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tbl_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame Gráfica Estadísticas
        chart_frame = ttk.LabelFrame(split_frame, text=" Indicadores Estadísticos Embebidos (Matplotlib) ", padding=10)
        split_frame.add(chart_frame, weight=1)

        self.chart_container = ttk.Frame(chart_frame)
        self.chart_container.pack(fill=tk.BOTH, expand=True)

    def cargar_datos(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        atrasados = self.reporte_service.obtener_prestamos_atrasados()
        hoy = datetime.now().date()

        for p in atrasados:
            venc_dt = datetime.strptime(p.fecha_vencimiento, "%Y-%m-%d").date()
            dias_atraso = (hoy - venc_dt).days

            self.tree.insert('', tk.END, iid=str(p.id), values=(
                p.id, p.lector_folio, p.lector_nombre, p.libro_isbn, p.libro_titulo,
                p.fecha_prestamo, p.fecha_vencimiento, f"{dias_atraso} días"
            ))

        self._renderizar_grafica()

    def _renderizar_grafica(self):
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        if not HAS_MATPLOTLIB:
            ttk.Label(
                self.chart_container,
                text="Matplotlib no se encuentra instalado en el entorno Python.\nInstale 'matplotlib' para visualizar gráficos.",
                font=('Segoe UI', 10, 'italic'),
                foreground='#64748b'
            ).pack(expand=True)
            return

        stats = self.reporte_service.obtener_estadisticas_generales()

        fig = Figure(figsize=(7, 2.8), dpi=95)
        fig.patch.set_alpha(0.0)

        # Subplot 1: Préstamos por Estado
        ax1 = fig.add_subplot(121)
        labels = ['Activos a tiempo', 'Atrasados', 'Devueltos']
        values = [
            stats['prestamos_activos'] - stats['prestamos_atrasados'],
            stats['prestamos_atrasados'],
            stats['prestamos_devueltos']
        ]
        colors = ['#3b82f6', '#ef4444', '#10b981']

        # Filtrar valores cero para gráfica pastel limpia
        pie_labels, pie_vals, pie_cols = [], [], []
        for l, v, c in zip(labels, values, colors):
            if v > 0:
                pie_labels.append(l)
                pie_vals.append(v)
                pie_cols.append(c)

        if pie_vals:
            ax1.pie(pie_vals, labels=pie_labels, autopct='%1.0f%%', colors=pie_cols, startangle=140, textprops={'fontsize': 8})
        else:
            ax1.text(0.5, 0.5, 'Sin préstamos registrados', ha='center', va='center', fontsize=8)

        ax1.set_title("Estatus de Préstamos", fontsize=9, fontweight='bold')

        # Subplot 2: Libros por Categoría
        ax2 = fig.add_subplot(122)
        cats = list(stats['categorias_conteo'].keys())
        counts = list(stats['categorias_conteo'].values())

        if cats:
            ax2.barh(cats, counts, color='#0d9488')
            ax2.set_xlabel("Nº de Libros", fontsize=8)
            ax2.tick_params(axis='both', labelsize=8)
        else:
            ax2.text(0.5, 0.5, 'Sin categorías', ha='center', va='center', fontsize=8)

        ax2.set_title("Acervo por Categoría", fontsize=9, fontweight='bold')
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _exportar_csv(self):
        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
            title="Guardar Reporte de Préstamos Atrasados"
        )
        if ruta:
            try:
                self.reporte_service.exportar_atrasados_a_csv(ruta)
                messagebox.showinfo("Exportación Exitosa", f"El reporte ha sido exportado correctamente en:\n{ruta}")
            except Exception as ex:
                messagebox.showerror("Error al exportar", str(ex))
