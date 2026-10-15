# Sistema de gestión para gomería

Aplicación web para administrar ventas a clientes, compras a proveedores, inventario, clientes, proveedores y usuarios. La interfaz se sirve con Flask, usa JavaScript para las operaciones dinámicas y persiste los datos en MySQL.

## Tecnologías

| Tecnología | Uso en el proyecto |
|---|---|
| HTML5, CSS3 y JavaScript | Estructura, estilos e interacción de las pantallas. |
| Python y Flask | Aplicación web, vistas, API JSON y control de sesiones y roles. |
| MySQL | Persistencia de usuarios, catálogo, ventas, compras y entidades relacionadas. |
| MySQL Workbench | Cliente gráfico opcional para consultar y administrar la base de datos. |
| PyMySQL | Conexión de Python con MySQL. |
| DBUtils | Pool de conexiones MySQL. |
| Cloudinary | Almacenamiento de imágenes del inventario cuando se adjunta una imagen. |
| python-dotenv | Carga de configuración local desde `src/.env`. |
| Gunicorn | Servidor WSGI para despliegues compatibles; no es necesario para la ejecución local en Windows. |
| Git y GitHub | Control de versiones y alojamiento del repositorio. |
| Visual Studio Code | Editor recomendado para desarrollo. |

## Requisitos e instalación

- Python instalado.
- Una base de datos MySQL con el esquema del proyecto.
- Credenciales de Cloudinary si se van a cargar imágenes de productos.

Los paquetes Python instalados por el proyecto —fuente de verdad: `requirements.txt`— son:

```text
Flask
PyMySQL
python-dotenv
gunicorn
cloudinary
DBUtils
```

Desde la raíz del repositorio, en PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crea `src/.env` con la configuración del entorno. No subas este archivo ni sus secretos al repositorio:

```dotenv
DB_HOST=
DB_USER=
DB_PASSWORD=
DB_NAME=
DB_PORT=3306
CLAVE_SECRETA=
TU_CLOUD_NAME=
TU_API_KEY=
TU_API_SECRET=
```

Para iniciar la aplicación localmente:

```powershell
Set-Location src
python app.py
```

La aplicación se inicia en modo debug mediante `app.run(debug=True)`; esto es para desarrollo local, no para producción. `requirements.txt` también incluye Gunicorn para despliegues en entornos compatibles.

## Módulos principales

- **Autenticación:** inicio de sesión para cuentas activas y registro público de usuarios con rol predeterminado `Empleado`. Las contraseñas se guardan con hash.
- **Pantalla principal:** resumen de productos y clientes activos, ventas del día, últimas ventas y alertas de stock bajo; consulta el dashboard periódicamente.
- **Ventas a clientes:** registra venta, ítems y pago en una transacción, calcula importes con los precios vigentes del catálogo y descuenta stock para artículos que no sean servicios. Permite consultar, detallar y anular ventas; al anular se revierten las existencias.
- **Compras a proveedores:** registra órdenes pendientes sin modificar stock. Al confirmar la recepción se cargan las cantidades efectivamente recibidas; anular una orden completada revierte esas cantidades.
- **Inventario:** administra productos y servicios, existencias, cantidades mínimas, precios e imágenes opcionales en Cloudinary.
- **Clientes y proveedores:** permite buscar, crear, modificar y desactivar registros. El CUIT/DNI se valida y se controla contra duplicados normalizando espacios, puntos y guiones.
- **Empleados:** permite consultar, modificar y desactivar cuentas existentes. El registro de usuario es el flujo implementado para crear cuentas; el botón de alta desde la gestión no está implementado.

### Acceso por rol

La autorización se aplica en el servidor desde la protección central de `src/app.py`; ocultar enlaces en la interfaz no es el único control.

| Rol | Acceso |
|---|---|
| `AD` | Acceso total a las rutas protegidas. |
| `DEV` | Acceso total a las rutas protegidas. |
| `Empleado` / `EM` | Pantalla principal y ventas: listado, detalle, anulación y registro. También puede cerrar sesión. |
| Otros roles | Se redirigen a la pantalla principal (`/`); pueden acceder a ella, pero no a las demás rutas protegidas. |

El inicio de sesión y el registro son públicos. Las páginas protegidas redirigen a iniciar sesión cuando no hay sesión; las API sin sesión responden `401`. Si una sesión autenticada intenta acceder a una ruta no permitida por su rol, se la redirige a `/`.

## Códigos de respuesta HTTP

| Código | Significado | Contexto de uso |
|---|---|---|
| `200 OK` | Solicitud procesada correctamente. | Consultas exitosas y operaciones que responden sin crear un recurso. |
| `201 Created` | Recurso creado correctamente. | Alta de clientes o registro de una venta, según el endpoint. |
| `302 Found` | Redirección temporal. | Usuario sin sesión que intenta abrir una página protegida; se redirige al login. También se redirige a `/` a una sesión autenticada sin permiso para la ruta solicitada. |
| `400 Bad Request` | Solicitud o datos inválidos. | Campos o cantidades no válidos, carrito vacío o transición de estado no permitida. |
| `401 Unauthorized` | Falta una sesión válida o falla la autenticación. | API protegida sin sesión o credenciales de inicio de sesión incorrectas. |
| `404 Not Found` | Recurso o ruta inexistente. | Registro no encontrado o ruta que no existe. |
| `409 Conflict` | Conflicto con un registro existente. | CUIT/DNI ya asignado a otro cliente o proveedor. |
| `500 Internal Server Error` | Error del servidor o de persistencia. | Fallo de base de datos u otra excepción no controlada. |

Los códigos disponibles dependen del endpoint; esta tabla resume los utilizados por la aplicación y no significa que cada ruta devuelva todos ellos.

## Documentación técnica

Los detalles de rutas, parámetros, respuestas, operaciones de base de datos y limitaciones de cada pantalla están en [`docs/documentacion/`](docs/documentacion/):

- [Inicio de sesión y registro](docs/documentacion/inicio_sesion_registro.md)
- [Pantalla principal](docs/documentacion/pantalla_principal.md)
- [Ventas](docs/documentacion/venta.md)
- [Compras](docs/documentacion/compra.md)
- [Inventario](docs/documentacion/inventario.md)
- [Clientes](docs/documentacion/clientes.md)
- [Proveedores](docs/documentacion/proveedor.md)
- [Empleados](docs/documentacion/empleados.md)

La estructura MySQL exportada está en [`docs/comandos_creacion_db.sql`](docs/comandos_creacion_db.sql).
