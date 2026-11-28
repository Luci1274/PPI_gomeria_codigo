# Documentación técnica del módulo de clientes

## Descripción general

El módulo permite consultar, buscar, crear, editar, desactivar y reactivar clientes. La vista se renderiza con Flask; `clientes.js` consume las rutas JSON y actualiza la tabla y los modales sin recargar la página. El acceso a MySQL se concentra en la clase `Cliente`.

Archivos principales:

- Plantilla: `src/templates/clientes.html`.
- Rutas Flask: `src/modulos/clientes_rutas.py`.
- Acceso a datos: `src/modulos/comandos_db/comandos_db_clientes.py`.
- Interacción del navegador: `src/static/js/clientes.js`.
- Estilos generales de la vista: `src/static/css/gestion.css` y `src/static/css/navbar.css`.

## Interfaz y comportamiento

- La tabla presenta nombre y apellido, CUIT/DNI, teléfono, correo, ciudad, dirección, deuda, estado y acciones.
- La búsqueda encuentra coincidencias parciales por nombre, apellido o CUIT. Espera 300 ms desde la última escritura antes de consultar.
- Los filtros de ciudad y estado se pueden combinar con la búsqueda. Las ciudades se cargan desde los valores distintos no vacíos de la tabla de clientes. El estado permite ver todos, solo activos o solo inactivos. La pantalla inicia con todas las ciudades y todos los estados.
- La tabla pagina los resultados de 10 en 10. El indicador y la métrica se actualizan con los resultados de los filtros actuales; la métrica no representa necesariamente el total sin filtrar.
- El alta y la edición se realizan desde modales. El acceso superior también ofrece un enlace para iniciar una venta.
- La baja es lógica: el cliente permanece en la base con `activo = 0`. Las filas inactivas se resaltan, muestran la acción para reactivar y no muestran las acciones de editar o desactivar.
- Las operaciones muestran notificaciones de resultado; la desactivación solicita confirmación. Los errores de carga también se registran en la consola del navegador y se informan en la interfaz.

El formulario acepta el nombre completo en un solo campo: el JavaScript envía la primera palabra como `nombre` y el resto como `apellido`. Los nombres de varias palabras pueden, por lo tanto, quedar divididos de manera distinta a la esperada.

El formulario de edición muestra un selector de estado, pero su valor no se envía al servidor. Para cambiar el estado se usan las acciones de desactivar y reactivar de la tabla.

## Rutas de Flask (`clientes_bp`)

| Método y ruta | Función | Resultado |
|---|---|---|
| `GET /clientes` | `vista_gestion_clientes` | Renderiza `clientes.html`. |
| `GET /api/clientes` | `api_clientes` | Devuelve clientes paginados, ciudades disponibles y totales. |
| `POST /api/clientes/crear` | `api_crear_cliente` | Crea un cliente desde un cuerpo JSON. |
| `GET /clientes/<id>/editar` | `api_obtener_cliente` | Devuelve los datos de un cliente activo para el formulario. |
| `POST /api/clientes/<id>/editar` | `api_modificar_cliente` | Actualiza los datos del cliente desde un cuerpo JSON. |
| `GET /clientes/<id>/desactivar` | `desactivar_cliente` | Desactiva lógicamente al cliente. |
| `POST /api/clientes/<id>/activar` | `activar_cliente` | Reactiva un cliente inactivo. |

### `GET /api/clientes`

Parámetros de consulta:

| Parámetro | Tipo / valor predeterminado | Uso |
|---|---|---|
| `pagina` | Entero, `1` | Página solicitada; se consultan 10 registros por página. |
| `buscar` | Texto, opcional | Busca coincidencias parciales en nombre, apellido o CUIT. |
| `cuit` | Texto, opcional | Filtro exacto por CUIT; la interfaz actual no lo expone como filtro separado. |
| `ciudad` | Texto, opcional | Filtro exacto por ciudad, utilizado por el selector de la pantalla. |
| `activo` | `1` | `1` para activos, `0` para inactivos o texto vacío para todos. La pantalla envía vacío inicialmente. |

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

`total_items` corresponde a los resultados que cumplen los filtros. Cada elemento de `ciudades` contiene el campo `ciudad`. Si no hay resultados, la API puede devolver `total_paginas: 0`; la interfaz muestra la paginación como una página. Ante un error de base de datos, responde `500` con `exito: false`, un mensaje y `redireccion: "/"`.

### `POST /api/clientes/crear`

Recibe un JSON con `nombre`, `apellido`, `cuit`, `numero_tel`, `mail`, `ciudad` y `direccion`. Si se crea correctamente devuelve `201`:

```json
{
  "exito": true,
  "mensaje": "Cliente creado exitosamente",
  "id_cliente": 1
}
```

Ante un error de MySQL devuelve `500`, `exito: false` y un mensaje.

### `GET /clientes/<id>/editar`

Devuelve `200` con `exito: true` y el objeto `cliente`, incluidos sus datos y la deuda calculada. La consulta solo encuentra clientes activos. Si ocurre un error de MySQL o no se encuentra un cliente activo, la ruta responde `500` con un mensaje y `redireccion: "/clientes"`.

### `POST /api/clientes/<id>/editar`

Recibe los mismos campos de datos que la creación, excepto que el identificador se toma de la URL. Devuelve `200` si la consulta de actualización se ejecuta o `500` si falla. La ruta no procesa el campo `activo`.

### `GET /clientes/<id>/desactivar`

Actualiza el estado del cliente a inactivo. Responde `200` con `exito: true` si se modificó un cliente activo; en caso contrario, responde `400` con `exito: false`. La operación se expone actualmente con el método `GET`.

### `POST /api/clientes/<id>/activar`

Cambia `activo` de `0` a `1`. Devuelve `200` si se reactivó un cliente inactivo y `400` si no se modificó ninguna fila o falla la operación.

## Clase `Cliente` (acceso a datos)

### `Cliente.crear_cliente(...)`

Inserta el cliente con `activo = 1`. Normaliza nombre, apellido, ciudad y dirección con formato título. Devuelve el identificador generado (`lastrowid`) o `None` ante un error de MySQL.

### `Cliente.leer_clientes(pagina=1, por_pagina=10, buscar=None, cuit=None, ciudad=None, activo=1)`

Aplica los filtros y devuelve `(total_items, clientes, ciudades, exito)`. La búsqueda parcial se aplica sobre nombre, apellido y CUIT; `cuit` y `ciudad` son filtros exactos. Calcula `deuda` como la suma de `historial_pago_cliente.monto` asociada a ventas activas e incompletas (`venta.activa = 1` y `venta.estado = 0`).

La lista de ciudades incluye valores distintos no nulos ni vacíos de toda la tabla `cliente`, sin depender de los filtros aplicados al listado.

### `Cliente.leer_cliente(id)`

Busca un cliente activo por `idcliente` y calcula la deuda con el mismo criterio que el listado. Devuelve `(cliente, True)` si la consulta se ejecuta, incluso si no encuentra filas; ante un error de MySQL devuelve `(None, False)`.

### `Cliente.modificar_cliente(id, ...)`

Actualiza nombre, apellido, CUIT, teléfono, correo, ciudad y dirección. Normaliza nombre y apellido; ciudad y dirección vacías se guardan como `NULL`. No modifica `activo`. Devuelve `True` si la consulta termina correctamente y `False` si falla; no comprueba si el identificador coincidió con una fila.

### `Cliente.eliminar_cliente(id)` y `Cliente.activar_cliente(id)`

Realizan la baja lógica (`activo = 0`) y la reactivación (`activo = 1`), respectivamente. Cada método devuelve `True` si modificó una fila y `False` si el cliente no estaba en el estado esperado o si falla la operación.

## Consideraciones

- El selector de ciudad ya está conectado con el filtro `ciudad` de la API y conserva las opciones devueltas por el listado.
- El selector de estado del modal de edición es solo visual: no modifica el estado. Utilizar las acciones de la tabla para desactivar o reactivar.
- La desactivación está implementada como `GET`; sería preferible migrarla a un método HTTP de escritura (`POST` o `PATCH`) si se actualiza el contrato de la API y su cliente.
- Las rutas de este módulo no implementan validaciones de campos ni una comprobación de sesión propia.
