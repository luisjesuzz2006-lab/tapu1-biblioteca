# 📚 Biblioteca Central TAP - Sistema de Gestión de Préstamos

**Materia**: Tópicos Avanzados de Programación  
**Unidad**: Unidad 1 — Proyecto Final  
**Opción Seleccionada**: **Opción 1. Sistema de biblioteca**  
**Stack Tecnológico**: Python 3.10+, Tkinter / ttk, SQLite 3 (`sqlite3`), Matplotlib, Pillow  

---

## 📝 Descripción del Proyecto

**Biblioteca Central TAP** es una aplicación de escritorio diseñada para administrar de forma eficiente el acervo bibliográfico, el padrón de lectores y el registro de préstamos y devoluciones de una biblioteca académica o escolar.

El sistema resuelve la problemática del control de inventario de libros en tiempo real, vencimiento de préstamos, seguimiento de usuarios morosos y prevención de pérdida de libros, ofreciendo una interfaz gráfica moderna (con soporte para tema claro y oscuro), reportes exportables a CSV y gráficas estadísticas embebidas.

---

## 🚀 Requisitos e Instalación

### Requisitos Previos
- **Python 3.10** o superior instalado en el sistema.
- Entorno de ejecución con soporte para Tkinter.

### Instrucciones de Instalación y Ejecución

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/TU_USUARIO/tap-u1-biblioteca.git
   cd tap-u1-biblioteca
   ```

2. **Crear y activar un entorno virtual (opcional pero recomendado)**:
   ```bash
   # En Windows
   python -m venv .venv
   .venv\Scripts\activate

   # En Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**:
   ```bash
   python main.py
   ```

> **Nota**: La primera vez que se ejecuta la aplicación, el módulo `db/database.py` creará automáticamente el archivo de base de datos `biblioteca.db`, sus tablas con restricciones de llaves foráneas (`PRAGMA foreign_keys = ON;`) y sembrará los usuarios y datos de prueba requeridos.

---

## 🔑 Usuarios de Prueba Preconfigurados

| Usuario | Contraseña | Rol | Permisos y Alcance |
| :--- | :--- | :--- | :--- |
| `admin` | `admin123` | **Administrador** | Acceso total al sistema: CRUD de Libros, Lectores, Préstamos, Devoluciones, Reportes, Bitácora y **Administración de Cuentas de Personal**. |
| `operador` | `operador123` | **Operador** | Acceso a operaciones del catálogo y préstamos. **No puede gestionar ni ver la pestaña de cuentas del personal**. |

---

## 🗄️ Modelo de Datos (SQLite)

El sistema implementa 5 tablas relacionales con restricciones `FOREIGN KEY`, `CHECK` y `UNIQUE`:

```
+-------------------+       +-------------------+       +-------------------+
|  usuarios_sistema |       |     lectores      |       |      libros       |
+-------------------+       +-------------------+       +-------------------+
| id (PK)           |       | id (PK)           |       | id (PK)           |
| username (UNIQUE) |       | folio (UNIQUE)    |       | isbn (UNIQUE)     |
| password_hash     |       | nombre            |       | titulo            |
| rol               |       | correo (UNIQUE)   |       | autor             |
| activo            |       | telefono, tipo    |       | categoria, anio   |
+-------------------+       | activo            |       | stock_total       |
                            +---------+---------+       | stock_disponible  |
                                      |                 | activo            |
                                      | (1:N)           +---------+---------+
                                      |                           |
                                      v                           v (1:N)
                            +-------------------------------------+
                            |              prestamos              |
                            +-------------------------------------+
                            | id (PK)                             |
                            | lector_id (FK -> lectores.id)       |
                            | libro_id (FK -> libros.id)          |
                            | fecha_prestamo (ISO YYYY-MM-DD)     |
                            | fecha_vencimiento (ISO YYYY-MM-DD)  |
                            | fecha_devolucion (ISO / NULL)       |
                            | estado ('activo' | 'devuelto')      |
                            +-------------------------------------+
```

### Descripción de Tablas:
1. `usuarios_sistema`: Cuentas de acceso al sistema con hashing SHA-256.
2. `libros`: Acervo bibliográfico con ISBN único, stock total y disponible.
3. `lectores`: Padrón de usuarios de la biblioteca (alumnos, docentes, externos).
4. `prestamos`: Registro del movimiento de negocio relacionando lector y libro con vigencia de 7 días.
5. `bitacora`: Registro de auditoría de todas las acciones del sistema.

---

## 🛠️ Arquitectura del Proyecto (4 Capas)

El proyecto sigue un patrón de diseño desacoplado **N-Capas**:

```
tap-u1-biblioteca/
├── main.py                     # Punto de entrada de la aplicación
├── README.md                   # Documentación detallada del proyecto
├── requirements.txt            # Dependencias externas (matplotlib, pillow)
├── .gitignore                  # Filtro de Git
├── db/                         # Persistencia y Conexión SQLite
│   ├── __init__.py
│   └── database.py             # Inicializador, tablas, FK y sembrado de datos
├── models/                     # Entidades del Dominio (Objetos puros sin GUI)
│   ├── __init__.py
│   ├── usuario.py
│   ├── libro.py
│   ├── lector.py
│   ├── prestamo.py
│   └── bitacora.py
├── repositories/               # Capa de Acceso a Datos (Consultas SQL y JOINs)
│   ├── __init__.py
│   ├── usuario_repository.py
│   ├── libro_repository.py
│   ├── lector_repository.py
│   ├── prestamo_repository.py  # Consulta JOIN obligatoria
│   └── bitacora_repository.py
├── services/                   # Capa de Reglas de Negocio
│   ├── __init__.py
│   ├── usuario_service.py      # Autenticación y hash SHA-256
│   ├── libro_service.py        # Validación stock y reglas de borrado
│   ├── lector_service.py       # Validaciones folio/correo único
│   ├── prestamo_service.py     # Transacción atómica de préstamos y devolución
│   └── reporte_service.py      # Estadísticas y exportación CSV
└── ui/                         # Capa de Interfaz de Usuario (Tkinter / ttk)
    ├── __init__.py
    ├── styles.py               # Tema Claro / Oscuro con TTK Styles
    ├── login_window.py         # Ventana de autenticación modal
    ├── main_window.py          # Ventana principal con menú y pestañas
    ├── libros_view.py          # CRUD Libros con Treeview y búsqueda
    ├── lectores_view.py        # CRUD Lectores con Treeview y búsqueda
    ├── prestamos_view.py       # Pestaña de Movimientos (Préstamos/Devoluciones)
    ├── reportes_view.py        # Reporte Atrasados + Gráfica Matplotlib + CSV
    ├── usuarios_view.py        # Pestaña exclusiva de Administrador
    └── bitacora_view.py        # Pestaña de Auditoría del Sistema
```

---

## 📋 Reglas de Negocio Implementadas

1. **RF-1 / BD**: Generación automática de `biblioteca.db` y tablas en la primera ejecución.
2. **RF-2 / Roles**: Autenticación con roles `administrador` y `operador`. Los operadores no pueden acceder al módulo de gestión de usuarios.
3. **RF-3 / Hashing**: Las contraseñas se almacenan mediante el algoritmo de hash SHA-256 (`hashlib`). Nunca en texto plano.
4. **RF-4 / CRUD**: Gestión completa de Libros y Lectores con altas, modificaciones y desactivación lógica.
5. **RF-5 & RF-7 / Proceso de Negocio + JOIN**: Préstamo a 7 días y Devolución con actualización atómica de stock. Pantallas con consultas `SQL JOIN` que vinculan `prestamos`, `lectores` y `libros`.
6. **RF-6 / Filtros**: Búsqueda en tiempo real en widgets `Treeview` por ISBN, Título, Folio, Nombre, etc.
7. **RF-8 / Reportes**: Vista dedicada del caso problemático ("Préstamos Atrasados") con exportación a archivo CSV y gráfica con `matplotlib` embebido.
8. **RF-9 / Confirmaciones**: Diálogos `messagebox.askyesno` previa a desactivaciones o acciones irreversibles.
9. **RF-10 / Integridad Referencial**: Impide desactivar un libro o lector si cuenta con préstamos activos pendientes de devolución. Captura de `sqlite3.IntegrityError` y excepciones sin caídas de la aplicación (RNF-4).

---

## 🎨 Extras Implementados (Rubro Máximo)

- [x] **Bitácora de Acciones / Auditoría**: Registro persistente de cada inicio de sesión, alta, modificación y devolución realizada.
- [x] **Exportación a CSV**: Generación de reportes tabulares en formato CSV descargable.
- [x] **Gráfica Matplotlib Embebida**: Gráfico estadístico interactivo embebido directamente en la pestaña de reportes.
- [x] **Tema Claro / Oscuro**: Alternador de apariencia visual en tiempo real para la interfaz.

---

## 📂 Capturas de Pantalla

Las capturas de pantalla de la interfaz se encuentran ubicadas en la carpeta [`docs/capturas/`](./docs/capturas/):
- `01_login.png`: Pantalla de Login con roles.
- `02_libros_crud.png`: Padrón de Libros con buscador y modal `Toplevel`.
- `03_prestamos_join.png`: Movimiento de negocio con consultas JOIN.
- `04_reporte_grafica.png`: Pantalla de reportes atrasados con Matplotlib y exportación a CSV.

---

## 📤 Instrucciones para la Entrega en GitHub

1. Inicializar el repositorio Git local:
   ```bash
   git init
   git add .
   git commit -m "Inicialización del proyecto Sistema de Biblioteca TAP Unidad 1"
   ```
2. Crear un repositorio en GitHub llamado `tap-u1-biblioteca`.
3. Vincular el remoto y subir los cambios:
   ```bash
   git remote add origin https://github.com/TU_USUARIO/tap-u1-biblioteca.git
   git branch -M main
   git push -u origin main
   ```
4. Compartir el enlace del repositorio GitHub en la tarea asignada al profesor.
