# Sistema de gestión para gomería

Aplicación web para administrar ventas, compras, inventario, clientes, proveedores y empleados. El backend está desarrollado con Flask y MySQL; la interfaz utiliza HTML, CSS y JavaScript.

## Tecnologías (resumen)

- **Python y Flask:** lógica del servidor y rutas web.
- **MySQL:** almacenamiento relacional de la información.
- **HTML, CSS y JavaScript:** estructura, estilos e interacción de las pantallas.
- **Cloudinary:** almacenamiento y procesamiento de imágenes de productos.
- **Twilio y Gmail:** envío de códigos para recuperar contraseñas.

La explicación y justificación de cada tecnología está en [Tecnologías](docs/Tecnologias.md).

## Códigos de error HTTP

Los endpoints pueden responder con estos códigos. El mensaje de la respuesta indica el motivo concreto:

| Código | Significado |
|---|---|
| `400 Bad Request` | La solicitud tiene datos inválidos o incompletos. |
| `401 Unauthorized` | Faltan credenciales válidas o la sesión no está iniciada. |
| `403 Forbidden` | La sesión está iniciada, pero el usuario no tiene permiso para esa operación. |
| `404 Not Found` | No existe la ruta o el registro solicitado. |
| `405 Method Not Allowed` | La ruta existe, pero no acepta el método HTTP usado, por ejemplo `GET` en lugar de `POST`. |
| `409 Conflict` | La operación entra en conflicto con el estado actual o con un registro existente, como un CUIT duplicado o un cambio concurrente de stock/precio. |
| `415 Unsupported Media Type` | La API esperaba un tipo de contenido, normalmente JSON, que la solicitud no envió. |
| `500 Internal Server Error` | Ocurrió una falla del servidor, como un error no controlado o un problema de base de datos. |

`200 OK` y `201 Created` indican operaciones exitosas; no son códigos de error.

## Funcionalidades

| Módulo | Descripción | Documentación |
|---|---|---|
| Inicio y seguridad | Dashboard, autenticación, sesiones y permisos por rol. | [Sistema y base de datos](docs/documentacion/sistema_y_base_de_datos.md) |
| Clientes | Alta, consulta, edición, estado y filtros de clientes. | [Clientes](docs/documentacion/clientes.md) |
| Compras | Órdenes de compra, recepción, consulta y anulación. | [Compras](docs/documentacion/compra.md) |
| Empleados | Inicio de sesión, registro, recuperación y gestión de empleados. | [Empleados](docs/documentacion/empleado.md) |
| Inventario | Productos, servicios, tipos, stock y alertas. | [Inventario](docs/documentacion/inventario.md) |
| Proveedores | Gestión, búsqueda, filtros y estado de proveedores. | [Proveedores](docs/documentacion/proveedores.md) |
| Ventas | Registro, consulta, detalle, filtros y anulación de ventas. | [Ventas](docs/documentacion/venta.md) |

## Requisitos

- Python 3 y pip.
- MySQL 8 o compatible con la intercalación `utf8mb4_0900_ai_ci` usada por el esquema.
- Git para clonar el repositorio.

Las dependencias Python están en [`requirements.txt`](requirements.txt). La interfaz también carga algunas bibliotecas JavaScript y CSS desde CDN.

## Instalación local en Windows

Ejecutá estos comandos desde la carpeta raíz del repositorio en PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si PowerShell no permite activar el entorno, podés usar su intérprete directamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\app.py
```

## Configuración

La aplicación lee el archivo `.env` ubicado en `src/.env`. Crealo localmente con los datos de conexión de MySQL:

| Variable | Uso |
|---|---|
| `DB_HOST` | Host del servidor MySQL. |
| `DB_USER` | Usuario de la base de datos. |
| `DB_PASSWORD` | Contraseña de MySQL. |
| `DB_NAME` | Base de datos que utilizará la aplicación. |
| `DB_PORT` | Puerto; si se omite, se usa `3306`. |
| `CLAVE_SECRETA` | Clave privada que Flask usa para firmar las sesiones. Configurala con un valor aleatorio y seguro. |

Cloudinary, Twilio y Gmail requieren variables adicionales si se usan sus funciones; están enumeradas en la [guía de configuración](docs/documentacion/sistema_y_base_de_datos.md). No compartas ni subas el `.env` al repositorio.

## Base de datos

Creá o seleccioná una base MySQL de desarrollo y cargá el esquema desde [`docs/estructura_y_datos_DB_27_11_2026.sql`](docs/estructura_y_datos_DB_27_11_2026.sql). El archivo incluye datos de ejemplo y sentencias `DROP TABLE IF EXISTS`: **revisa su contenido y usalo solo en una base descartable o con respaldo**, nunca lo ejecutes a ciegas sobre datos existentes.

El modelo relacional, sus restricciones y las limitaciones conocidas del esquema se explican en [Sistema y base de datos](docs/documentacion/sistema_y_base_de_datos.md).

## Ejecutar

Con el entorno virtual activado y `src/.env` configurado, desde la raíz del proyecto:

```powershell
python src\app.py
```

Abrí `http://127.0.0.1:5000` en el navegador. El servidor integrado de Flask inicia con modo debug; está destinado al desarrollo local, no a producción. `gunicorn` se instala únicamente en sistemas distintos de Windows y puede utilizarse como servidor WSGI en un entorno compatible.

El registro desde la pantalla de acceso crea cuentas con rol `Empleado`. Los permisos para `AD` y `DEV` se administran según las reglas descritas en la [documentación general](docs/documentacion/sistema_y_base_de_datos.md).

## Estructura del proyecto

```text
.
├── docs/
│   ├── documentacion/       # Guías técnicas por módulo y del sistema
│   └── estructura_y_datos_DB_27_11_2026.sql
├── requirements.txt         # Dependencias Python
└── src/
    ├── app.py               # Aplicación Flask y guardia de acceso
    ├── config.py            # Configuración, entorno y pool MySQL
    ├── modulos/             # Rutas, persistencia y servicios
    ├── static/              # CSS, JavaScript e imágenes
    └── templates/            # Plantillas HTML/Jinja
```
