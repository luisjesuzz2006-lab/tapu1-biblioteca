from typing import List, Optional
from repositories.libro_repository import LibroRepository
from repositories.prestamo_repository import PrestamoRepository
from repositories.bitacora_repository import BitacoraRepository
from models.libro import Libro

class LibroService:
    def __init__(self, libro_repo: LibroRepository, prestamo_repo: PrestamoRepository, bitacora_repo: BitacoraRepository):
        self.libro_repo = libro_repo
        self.prestamo_repo = prestamo_repo
        self.bitacora_repo = bitacora_repo

    def listar_libros(self, filtro: str = "", solo_activos: bool = False) -> List[Libro]:
        if filtro.strip():
            return self.libro_repo.buscar_por_filtro(filtro.strip(), solo_activos)
        return self.libro_repo.listar_todos(solo_activos)

    def obtener_libro(self, libro_id: int) -> Optional[Libro]:
        return self.libro_repo.obtener_por_id(libro_id)

    def guardar_libro(self, libro_id: Optional[int], isbn: str, titulo: str, autor: str,
                      categoria: str, anio: int, stock_total: int, stock_disponible: int,
                      activo: bool, usuario_actual: str) -> Libro:
        # Validaciones de campos
        isbn_clean = isbn.strip()
        titulo_clean = titulo.strip()
        autor_clean = autor.strip()
        categoria_clean = categoria.strip()

        if not isbn_clean:
            raise ValueError("El ISBN del libro es obligatorio.")
        if not titulo_clean:
            raise ValueError("El título del libro es obligatorio.")
        if not autor_clean:
            raise ValueError("El autor del libro es obligatorio.")
        if not categoria_clean:
            raise ValueError("La categoría del libro es obligatoria.")
        if anio <= 0 or anio > 2100:
            raise ValueError("El año de publicación no es válido.")
        if stock_total < 0:
            raise ValueError("El stock total no puede ser negativo.")
        if stock_disponible < 0 or stock_disponible > stock_total:
            raise ValueError("El stock disponible debe ser mayor o igual a 0 y no superar el stock total.")

        # Verificar ISBN único
        existente = self.libro_repo.obtener_por_isbn(isbn_clean)
        if existente and (libro_id is None or existente.id != libro_id):
            raise ValueError(f"Ya existe un libro registrado con el ISBN '{isbn_clean}'.")

        if libro_id is None:
            nuevo_libro = Libro(
                id=None, isbn=isbn_clean, titulo=titulo_clean, autor=autor_clean,
                categoria=categoria_clean, anio=anio, stock_total=stock_total,
                stock_disponible=stock_disponible, activo=activo
            )
            guardado = self.libro_repo.crear(nuevo_libro)
            self.bitacora_repo.registrar(usuario_actual, f"Alta de libro: {guardado.titulo} (ISBN: {guardado.isbn})")
            return guardado
        else:
            libro_existente = self.libro_repo.obtener_por_id(libro_id)
            if not libro_existente:
                raise ValueError("El libro a actualizar no fue encontrado.")

            libro_existente.isbn = isbn_clean
            libro_existente.titulo = titulo_clean
            libro_existente.autor = autor_clean
            libro_existente.categoria = categoria_clean
            libro_existente.anio = anio
            libro_existente.stock_total = stock_total
            libro_existente.stock_disponible = stock_disponible
            libro_existente.activo = activo

            self.libro_repo.actualizar(libro_existente)
            self.bitacora_repo.registrar(usuario_actual, f"Edición de libro ID {libro_id}: {libro_existente.titulo}")
            return libro_existente

    def desactivar_o_activar_libro(self, libro_id: int, activo: bool, usuario_actual: str) -> bool:
        """
        RF-10 / Reglas: No borrar libro con préstamo activo; desactivar.
        Si se intenta desactivar un libro con préstamos activos, se rechaza la acción con ValueError.
        """
        libro = self.libro_repo.obtener_por_id(libro_id)
        if not libro:
            raise ValueError("El libro especificado no existe.")

        if not activo:
            activos_cnt = self.prestamo_repo.contar_prestamos_activos_por_libro(libro_id)
            if activos_cnt > 0:
                raise ValueError(f"No se puede desactivar el libro '{libro.titulo}' porque tiene {activos_cnt} préstamo(s) activo(s).")

        exito = self.libro_repo.cambiar_estado_activo(libro_id, activo)
        if exito:
            accion_str = "activado" if activo else "desactivado"
            self.bitacora_repo.registrar(usuario_actual, f"Libro {libro.titulo} (ID {libro_id}) {accion_str}")
        return exito
