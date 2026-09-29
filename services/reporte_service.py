import csv
from typing import List, Dict, Any
from datetime import datetime
from repositories.prestamo_repository import PrestamoRepository
from repositories.libro_repository import LibroRepository
from repositories.lector_repository import LectorRepository
from models.prestamo import Prestamo

class ReporteService:
    def __init__(self, prestamo_repo: PrestamoRepository, libro_repo: LibroRepository, lector_repo: LectorRepository):
        self.prestamo_repo = prestamo_repo
        self.libro_repo = libro_repo
        self.lector_repo = lector_repo

    def obtener_prestamos_atrasados(() -> List[Prestamo]:
        """Obtiene la lista del caso problemático: Préstamos activos vencidos."""
        return self.prestamo_repo.listar_prestamos_atrasados()

    def exportar_atrasados_a_csv(self, ruta_archivo: str) -> str:
        """Exporta los préstamos atrasados a un archivo CSV estructurado."""
        atrasados = self.obtener_prestamos_atrasados()
        with open(ruta_archivo, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Encabezados
            writer.writerow(['ID Préstamo', 'Folio Lector', 'Nombre Lector', 'ISBN', 'Título Libro', 'Fecha Préstamo', 'Fecha Vencimiento', 'Días de Atraso'])
            
            hoy = datetime.now().date()
            for p in atrasados:
                venc_dt = datetime.strptime(p.fecha_vencimiento, "%Y-%m-%d").date()
                dias_atraso = (hoy - venc_dt).days
                writer.writerow([
                    p.id,
                    p.lector_folio or '',
                    p.lector_nombre or '',
                    p.libro_isbn or '',
                    p.libro_titulo or '',
                    p.fecha_prestamo,
                    p.fecha_vencimiento,
                    dias_atraso
                ])
        return ruta_archivo

    def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """Calcula métricas clave para visualizaciones y resúmenes del sistema."""
        prestamos_todos = self.prestamo_repo.listar_con_join()
        atrasados = self.obtener_prestamos_atrasados()
        libros = self.libro_repo.listar_todos()
        lectores = self.lector_repo.listar_todos()

        activos_cnt = sum(1 for p in prestamos_todos if p.estado == 'activo')
        devueltos_cnt = sum(1 for p in prestamos_todos if p.estado == 'devuelto')
        atrasados_cnt = len(atrasados)

        # Distribución de libros por categoría
        categorias: Dict[str, int] = {}
        for lib in libros:
            if lib.activo:
                cat = lib.categoria
                categorias[cat] = categorias.get(cat, 0) + 1

        return {
            'total_libros': len(libros),
            'total_lectores': len(lectores),
            'total_prestamos': len(prestamos_todos),
            'prestamos_activos': activos_cnt,
            'prestamos_devueltos': devueltos_cnt,
            'prestamos_atrasados': atrasados_cnt,
            'categorias_conteo': categorias
        }
