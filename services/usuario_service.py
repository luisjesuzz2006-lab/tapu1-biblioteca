from typing import List, Optional
from repositories.usuario_repository import UsuarioRepository
from repositories.bitacora_repository import BitacoraRepository
from models.usuario import Usuario
from db.database import hash_password

class UsuarioService:
    def __init__(self, usuario_repo: UsuarioRepository, bitacora_repo: BitacoraRepository):
        self.usuario_repo = usuario_repo
        self.bitacora_repo = bitacora_repo

    def autenticar(self, username: str, password_plano: str) -> Usuario:
        """
        Valida las credenciales del usuario.
        Lanza ValueError si falla la autenticación o si el usuario está inactivo (RF-2, RF-3, Login).
        """
        if not username or not username.strip():
            raise ValueError("El nombre de usuario no puede estar vacío.")
        if not password_plano:
            raise ValueError("La contraseña no puede estar vacía.")

        user = self.usuario_repo.obtener_por_username(username.strip())
        if not user:
            raise ValueError("Usuario o contraseña incorrectos.")

        if not user.activo:
            raise ValueError("La cuenta de usuario se encuentra inactiva. Contacte al administrador.")

        pwd_hash = hash_password(password_plano)
        if user.password_hash != pwd_hash:
            raise ValueError("Usuario o contraseña incorrectos.")

        self.bitacora_repo.registrar(user.username, "Inicio de sesión exitoso")
        return user

    def listar_usuarios(self) -> List[Usuario]:
        return self.usuario_repo.listar_todos()

    def crear_usuario(self, username: str, password_plano: str, rol: str, usuario_actual: str) -> Usuario:
        if not username or not username.strip():
            raise ValueError("El nombre de usuario es obligatorio.")
        if not password_plano or len(password_plano.strip()) < 6:
            raise ValueError("La contraseña debe contener al menos 6 caracteres.")
        if rol.lower() not in ('administrador', 'operador'):
            raise ValueError("El rol asignado no es válido.")

        existente = self.usuario_repo.obtener_por_username(username.strip())
        if existente:
            raise ValueError(f"El nombre de usuario '{username}' ya se encuentra registrado.")

        pwd_hash = hash_password(password_plano)
        nuevo_usuario = Usuario(
            id=None,
            username=username.strip(),
            password_hash=pwd_hash,
            rol=rol.lower(),
            activo=True
        )
        creado = self.usuario_repo.crear(nuevo_usuario)
        self.bitacora_repo.registrar(usuario_actual, f"Creación de usuario del sistema: {creado.username} ({creado.rol})")
        return creado

    def cambiar_estado_activo(self, usuario_id: int, activo: bool, usuario_actual: str) -> bool:
        user = self.usuario_repo.obtener_por_id(usuario_id)
        if not user:
            raise ValueError("El usuario no existe.")
        if user.username == usuario_actual:
            raise ValueError("No puede desactivar su propia cuenta de usuario en sesión.")

        user.activo = activo
        exito = self.usuario_repo.actualizar(user)
        if exito:
            estado_str = "activado" if activo else "desactivado"
            self.bitacora_repo.registrar(usuario_actual, f"Usuario {user.username} {estado_str}")
        return exito
