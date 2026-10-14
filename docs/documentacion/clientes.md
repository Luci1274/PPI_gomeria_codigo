# Documentación técnica del módulo de clientes

## Descripción general

El módulo permite consultar, buscar, crear, editar y desactivar clientes. La interfaz se renderiza con Flask y utiliza JavaScript para consultar las rutas JSON y actualizar la tabla sin recargar la página. Los datos se leen y modifican en MySQL mediante la clase `Cliente`.

La plantilla principal es `src/templates/clientes.html`; utiliza `src/static/js/clientes.js` para la interacción y `src/static/css/clientes.css` y `navbar.css` para los estilos.

## Interfaz y comportamiento

- La tabla muestra nombre o razón social, CUIT/DNI, teléfono, correo, ciudad, dirección, deuda, estado y acciones.
- La búsqueda se aplica por nombre, apellido o CUIT y espera 300 ms desde la última escritura antes de consultar.
- El filtro de estado permite listar clientes activos, inactivos o ambos. Al abrir la pantalla se consultan los activos.
- La tabla pagina los resultados en grupos de 10.
- El alta y la edición se realizan desde formularios modales. La baja es lógica: el cliente permanece en la base de datos con `activo = 0`.
- Al cargar o guardar datos, el navegador muestra notificaciones. La pantalla utiliza una caja con mensajes emergentes para informar errores de validación o de la base de datos.

El formulario recibe el nombre completo en un solo campo y el JavaScript lo divide: la primera palabra se envía como `nombre` y las restantes como `apellido`. Por ello, nombres compuestos no se separan necesariamente como espera cada persona.

## Rutas de Flask (`clientes_bp`)

| Método y ruta | Función | Resultado |
|---|---|---|
| `GET /clientes` | `vista_gestion_clientes` | Renderiza `clientes.html`. |
| `GET /api/clientes` | `api_clientes` | Devuelve la lista paginada, las ciudades disponibles y los totales. |
| `POST /api/clientes/crear` | `api_crear_cliente` | Crea un cliente a partir de un cuerpo JSON. |
| `GET /clientes/<id>/editar` | `api_obtener_cliente` | Devuelve los datos de un cliente activo para cargar el formulario. |
| `POST /api/clientes/<id>/editar` | `api_modificar_cliente` | Actualiza los datos del cliente a partir de un cuerpo JSON. |
| `POST /clientes/<id>/desactivar` | `desactivar_cliente` | Desactiva lógicamente al cliente. |

### `GET /api/clientes`

Parámetros de consulta:

| Parámetro | Tipo / valor predeterminado | Uso |
|---|---|---|
| `pagina` | Entero, `1` | Página solicitada. |
| `buscar` | Texto, opcional | Busca coincidencias en nombre, apellido o CUIT. |
| `cuit` | Texto, opcional | Filtra por CUIT exacto. |
| `ciudad` | Texto, opcional | Filtra por ciudad exacta. |
| `activo` | `1` | Filtra por estado: `1` activos, `0` inactivos o vacío para todos. |

Respuesta exitosa (`200`):

```json
{
	"exito": true,
	"clientes": [],
	"ciudades": [],
	"pagina_actual": 1,
	"total_paginas": 0,
	"total_items": 0
}
```

Ante un error al consultar la base de datos responde `500` con `exito: false`, un mensaje y `redireccion: "/"`. La cantidad de páginas puede ser `0` cuando no hay resultados.

### `POST /api/clientes/crear`

Recibe un JSON con `nombre`, `apellido`, `cuit`, `numero_tel`, `mail`, `ciudad` y `direccion`. El CUIT/DNI es obligatorio en la API y debe ser numérico una vez quitados espacios, puntos y guiones. Se conserva en la base el formato original recibido.

Si se crea correctamente devuelve `201`:

```json
{
	"exito": true,
	"mensaje": "Cliente creado exitosamente",
	"id_cliente": 1
}
```

Si el CUIT/DNI ya pertenece a otro cliente, devuelve `409`; si falta o tiene caracteres no admitidos, devuelve `400`. La interfaz muestra el mensaje de la API. Si falla la operación en la base de datos devuelve `500`, `exito: false` y un mensaje de error.

### `GET /clientes/<id>/editar`

Devuelve `200` con `exito: true` y el objeto `cliente`, incluidos sus datos y la deuda calculada. La consulta solo encuentra clientes activos. Si no se obtiene el cliente, la ruta devuelve `500` con un mensaje de error y `redireccion: "/clientes"`.

### `POST /api/clientes/<id>/editar`

Recibe los mismos campos de datos que la creación, excepto que el identificador se toma de la URL. Comprueba que el CUIT/DNI normalizado no pertenezca a otro cliente; permite conservar el CUIT/DNI propio al editar. La comprobación incluye clientes inactivos. Responde `409` si ya está asignado a otro cliente, `400` si falta o no es válido, `200` si se actualiza correctamente y `500` ante un error de base de datos.

### `POST /clientes/<id>/desactivar`

Actualiza el estado del cliente a inactivo. Responde `200` con `exito: true` cuando la operación informa éxito; en caso contrario, responde `400` con `exito: false`.

## Clase `Cliente` (acceso a datos)

### `Cliente.crear_cliente(...)`

Inserta un cliente con `activo = 1`. Normaliza nombre, apellido, ciudad y dirección convirtiéndolos a formato título. Antes del `INSERT`, compara el CUIT/DNI sin espacios, puntos ni guiones contra todos los clientes, activos o inactivos. Lanza `ClienteCuitDuplicadoError` si ya está registrado y `ClienteCuitInvalidoError` si falta o no es numérico; devuelve el identificador generado (`lastrowid`) o `None` ante un error de MySQL.

### `Cliente.leer_clientes(pagina=1, por_pagina=10, buscar=None, cuit=None, ciudad=None, activo=1)`

Aplica los filtros solicitados y devuelve una tupla con `(total_items, clientes, ciudades, exito)`. La búsqueda parcial se aplica sobre nombre, apellido y CUIT; los filtros `cuit` y `ciudad` son exactos. La deuda se calcula como la suma de `historial_pago_cliente.monto` asociada a ventas activas e incompletas (`venta.activa = 1` y `venta.estado = 0`).

La consulta de ciudades devuelve los valores distintos no nulos ni vacíos de la tabla `cliente`.

### `Cliente.leer_cliente(id)`

Busca un cliente activo por `idcliente` y calcula su deuda con el mismo criterio que el listado. Devuelve `(cliente, True)` si la consulta se ejecuta, incluso si no encuentra filas; ante un error de MySQL devuelve `(None, False)`.

### `Cliente.modificar_cliente(id, ...)`

Actualiza nombre, apellido, CUIT, teléfono, correo, ciudad y dirección. Normaliza nombre y apellido; ciudad y dirección vacías se guardan como `NULL`. No modifica el campo `activo`. Bloquea la fila del cliente y comprueba que el CUIT/DNI no pertenezca a otro registro. Lanza `ClienteCuitDuplicadoError` o `ClienteCuitInvalidoError` en caso de duplicado o dato inválido; devuelve `True` ante una actualización válida y `False` si no existe el registro o falla la consulta.

### `Cliente.eliminar_cliente(id)`

Realiza la baja lógica mediante `UPDATE cliente SET activo = 0`. Devuelve `True` si la operación termina correctamente y `False` si falla.

## Consideraciones de implementación

- La API acepta el filtro `ciudad` y devuelve ciudades, pero `clientes.html` no contiene actualmente un selector con el identificador `select-ciudad-filtro`; por eso el filtro de ciudad del JavaScript no se muestra ni se utiliza desde esta pantalla.
- El formulario de edición incluye un selector de estado, pero `clientes.js` no envía ese valor y `Cliente.modificar_cliente` tampoco actualiza `activo`. El selector no cambia el estado del cliente.
- La desactivación lógica se solicita con `POST`; el método de acceso a datos cambia `activo` a `0`.
- Las rutas mostradas no realizan validaciones de campos ni comprueban una sesión antes de ejecutar las operaciones. La base de datos o validaciones adicionales deberían proteger los datos requeridos.
- La aplicación previene duplicados de CUIT/DNI normalizando espacios, puntos y guiones, y considerando también clientes inactivos. La base de datos no declara una restricción única para el dato; la comprobación previa no garantiza evitar una carrera entre solicitudes concurrentes. Para una garantía también a nivel de base hace falta limpiar duplicados existentes y agregar un índice único sobre un valor canónico.
