from typing import List
from datetime import datetime, timedelta
from repositories.prestamo_repository import PrestamoRepository
from repositories.libro_repository import LibroRepository
from repositories.lector_repository import LectorRepository
from repositories.bitacora_repository import BitacoraRepository
from models.prestamo import Prestamo

class PrestamoService:
    def __init__(self, prestamo_repo: PrestamoRepository, libro_repo: LibroRepository,
                 lector_repo: LectorRepository, bitacora_repo: BitacoraRepository):
        self.prestamo_repo = prestamo_repo
        self.libro_repo = libro_repo
        self.lector_repo = lector_repo
        self.bitacora_repo = bitacora_repo

    def listar_prestamos_join(self, filtro: str = "", estado: str = "todos") -> List[Prestamo]:
        """Devuelve préstamos con JOIN relacionando lector y libro."""
        return self.prestamo_repo.listar_con_join(filtro, estado)

    def registrar_prestamo(self, lector_id: int, libro_id: int, usuario_actual: str) -> Prestamo:
        """
        Reglas de Negocio Opción 1:
        1. Lector debe existir y estar activo.
        2. Libro debe existir, estar activo y tener stock_disponible > 0.
        3. El lector no debe tener ya un préstamo activo del mismo libro.
        4. Fecha de vencimiento a 7 días de la fecha de préstamo.
        5. Actualización atómica de stock en BD.
        """
        # 1. Validar lector
        lector = self.lector_repo.obtener_por_id(lector_id)
        if not lector:
            raise ValueError("El lector seleccionado no existe.")
        if not lector.activo:
            raise ValueError(f"No se puede realizar el préstamo: El lector '{lector.nombre}' está inactivo.")

        # 2. Validar libro
        libro = self.libro_repo.obtener_por_id(libro_id)
        if not libro:
            raise ValueError("El libro seleccionado no existe.")
        if not libro.activo:
            raise ValueError(f"No se puede realizar el préstamo: El libro '{libro.titulo}' está inactivo.")
        if libro.stock_disponible <= 0:
            raise ValueError(f"No hay stock disponible para el libro '{libro.titulo}' (Disponible: 0).")

        # 3. Validar préstamos activos duplicados del mismo libro para este lector
        mismo_libro_activos = self.prestamo_repo.contar_prestamos_activos_por_lector_y_libro(lector_id, libro_id)
        if mismo_libro_activos > 0:
            raise ValueError(f"El lector '{lector.nombre}' ya tiene un préstamo activo de este mismo libro.")

        # 4. Fechas (7 días de vigencia)
        hoy_dt = datetime.now().date()
        fecha_prestamo = hoy_dt.isoformat()
        fecha_vencimiento = (hoy_dt + timedelta(days=7)).isoformat()

        nuevo_prestamo = Prestamo(
            id=None,
            lector_id=lector_id,
            libro_id=libro_id,
            fecha_prestamo=fecha_prestamo,
            fecha_vencimiento=fecha_vencimiento,
            fecha_devolucion=None,
            estado='activo'
        )

        # 5. Registro transaccional
        creado = self.prestamo_repo.registrar_prestamo_transaccional(nuevo_prestamo)
        self.bitacora_repo.registrar(
            usuario_actual,
            f"Préstamo registrado: Libro '{libro.titulo}' a Lector '{lector.nombre}' (Vence: {fecha_vencimiento})"
        )
        return creado

    def registrar_devolucion(self, prestamo_id: int, usuario_actual: str) -> bool:
        """
        Cierre del proceso de negocio:
        Marca el préstamo como devuelto e incrementa el stock disponible del libro.
        """
        prestamo = self.prestamo_repo.obtener_por_id(prestamo_id)
        if not prestamo:
            raise ValueError("El préstamo especificado no existe.")
        if prestamo.estado == 'devuelto':
            raise ValueError("Este préstamo ya fue devuelto con anterioridad.")

        hoy_iso = datetime.now().date().isoformat()
        exito = self.prestamo_repo.registrar_devolucion_transaccional(prestamo_id, hoy_iso)

        if exito:
            self.bitacora_repo.registrar(
                usuario_actual,
                f"Devolución registrada: Préstamo #{prestamo_id} (Libro: {prestamo.libro_titulo})"
            )
        return exito
