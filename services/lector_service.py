from typing import List, Optional
from repositories.lector_repository import LectorRepository
from repositories.prestamo_repository import PrestamoRepository
from repositories.bitacora_repository import BitacoraRepository
from models.lector import Lector

class LectorService:
    def __init__(self, lector_repo: LectorRepository, prestamo_repo: PrestamoRepository, bitacora_repo: BitacoraRepository):
        self.lector_repo = lector_repo
        self.prestamo_repo = prestamo_repo
        self.bitacora_repo = bitacora_repo

    def listar_lectores(self, filtro: str = "", solo_activos: bool = False) -> List[Lector]:
        if filtro.strip():
            return self.lector_repo.buscar_por_filtro(filtro.strip(), solo_activos)
        return self.lector_repo.listar_todos(solo_activos)

    def obtener_lector(self, lector_id: int) -> Optional[Lector]:
        return self.lector_repo.obtener_por_id(lector_id)

    def guardar_lector(self, lector_id: Optional[int], folio: str, nombre: str, correo: str,
                       telefono: str, tipo: str, activo: bool, usuario_actual: str) -> Lector:
        folio_clean = folio.strip()
        nombre_clean = nombre.strip()
        correo_clean = correo.strip().lower()
        telefono_clean = telefono.strip()
        tipo_clean = tipo.strip().lower()

        if not folio_clean:
            raise ValueError("El folio del lector es obligatorio.")
        if not nombre_clean:
            raise ValueError("El nombre del lector es obligatorio.")
        if not correo_clean or '@' not in correo_clean:
            raise ValueError("Ingrese un correo electrónico válido.")
        if not telefono_clean:
            raise ValueError("El teléfono es obligatorio.")
        if tipo_clean not in ('alumno', 'docente', 'externo'):
            raise ValueError("El tipo de lector debe ser 'alumno', 'docente' o 'externo'.")

        # Folio único
        existente_folio = self.lector_repo.obtener_por_folio(folio_clean)
        if existente_folio and (lector_id is None or existente_folio.id != lector_id):
            raise ValueError(f"Ya existe un lector registrado con el folio '{folio_clean}'.")

        # Correo único
        existente_correo = self.lector_repo.obtener_por_correo(correo_clean)
        if existente_correo and (lector_id is None or existente_correo.id != lector_id):
            raise ValueError(f"Ya existe un lector registrado con el correo '{correo_clean}'.")

        if lector_id is None:
            nuevo_lector = Lector(
                id=None, folio=folio_clean, nombre=nombre_clean, correo=correo_clean,
                telefono=telefono_clean, tipo=tipo_clean, activo=activo
            )
            guardado = self.lector_repo.crear(nuevo_lector)
            self.bitacora_repo.registrar(usuario_actual, f"Alta de lector: {guardado.nombre} (Folio: {guardado.folio})")
            return guardado
        else:
            lector_existente = self.lector_repo.obtener_por_id(lector_id)
            if not lector_existente:
                raise ValueError("El lector a actualizar no fue encontrado.")

            lector_existente.folio = folio_clean
            lector_existente.nombre = nombre_clean
            lector_existente.correo = correo_clean
            lector_existente.telefono = telefono_clean
            lector_existente.tipo = tipo_clean
            lector_existente.activo = activo

            self.lector_repo.actualizar(lector_existente)
            self.bitacora_repo.registrar(usuario_actual, f"Edición de lector ID {lector_id}: {lector_existente.nombre}")
            return lector_existente

    def desactivar_o_activar_lector(self, lector_id: int, activo: bool, usuario_actual: str) -> bool:
        """
        RF-10 / Reglas: No borrar lector con préstamos activos; desactivar.
        """
        lector = self.lector_repo.obtener_por_id(lector_id)
        if not lector:
            raise ValueError("El lector especificado no existe.")

        if not activo:
            activos_cnt = self.prestamo_repo.contar_prestamos_activos_por_lector(lector_id)
            if activos_cnt > 0:
                raise ValueError(f"No se puede desactivar al lector '{lector.nombre}' porque tiene {activos_cnt} préstamo(s) activo(s).")

        exito = self.lector_repo.cambiar_estado_activo(lector_id, activo)
        if exito:
            accion_str = "activado" if activo else "desactivado"
            self.bitacora_repo.registrar(usuario_actual, f"Lector {lector.nombre} (Folio {lector.folio}) {accion_str}")
        return exito
