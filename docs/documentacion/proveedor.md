# Documentación del módulo de proveedores

## Objetivo y alcance

El módulo permite consultar proveedores, buscarlos y filtrarlos, crear y modificar sus datos y desactivarlos lógicamente. También ofrece un acceso directo a la pantalla para registrar una compra.

Los proveedores se guardan en la tabla `proveedor`. Las compras se relacionan con ellos mediante `idproveedor`; desactivar un proveedor no elimina su historial de compras ni borra el registro.

## Archivos involucrados

| Archivo | Responsabilidad |
|---|---|
| `src/modulos/proveedores_rutas.py` | Rutas Flask para la pantalla, el listado y las operaciones de proveedores. |
| `src/modulos/comandos_db/comandos_db_proveedores.py` | Consultas y operaciones de persistencia de la clase `Proveedor`. |
| `src/templates/proveedor.html` | Pantalla, filtros, tabla y formularios modales. Extiende `plantailla_gestion.html`. |
| `src/static/js/proveedores.js` | Carga y renderizado del listado, filtros, paginación y acciones de formularios. |

## Pantalla de gestión

La pantalla presenta:

- **Nuevo Proveedor**, que abre el formulario de alta.
- **Nueva Compra**, que dirige a `/compras/realizar`.
- Una métrica con el total de proveedores que coinciden con los filtros.
- Búsqueda por nombre o CUIT.
- Filtros por rubro, estado (activos, inactivos o todos) y ciudad.
- Tabla con código, nombre/razón social y rubro, CUIT, ciudad y dirección, teléfono, correo, estado y acciones.
- Paginación, con 10 registros por página.
- Formularios modales para crear y modificar.
- Confirmación antes de desactivar.

La búsqueda espera 300 ms desde la última pulsación. Al cambiar la búsqueda o cualquiera de los filtros, el listado vuelve a la página 1. Los registros inactivos también muestran las acciones de modificar y eliminar; el backend permite consultar y modificar un proveedor por ID sin filtrar por estado.

## Rutas

| Método y ruta | Función | Descripción |
|---|---|---|
| `GET /proveedores` | `vista_gestion_proveedores` | Renderiza `proveedor.html`. |
| `GET /api/proveedores` | `api_proveedores` | Devuelve los proveedores paginados y las opciones de rubro y ciudad. |
| `POST /api/proveedores/crear` | `api_crear_proveedor` | Crea un proveedor a partir de un cuerpo JSON. |
| `GET /proveedores/<id>/editar` | `api_obtener_proveedor` | Devuelve los datos de un proveedor para editarlo. |
| `POST /api/proveedores/<id>/editar` | `api_modificar_proveedor` | Actualiza los datos indicados en el cuerpo JSON. |
| `POST /proveedores/<id>/desactivar` | `desactivar_proveedor` | Realiza una desactivación lógica. |

## Listado: `GET /api/proveedores`

### Parámetros de consulta

| Parámetro | Predeterminado | Comportamiento |
|---|---|---|
| `pagina` | `1` | Página solicitada; se usan 10 registros por página. |
| `buscar` | Vacío | Búsqueda parcial (`LIKE`) sobre nombre o CUIT. |
| `rubro` | Vacío | Coincidencia exacta de rubro. |
| `activo` | Vacío en la API | `1` activos, `0` inactivos; vacío no filtra por estado. La pantalla selecciona activos inicialmente. |
| `ciudad` | Vacío | Coincidencia exacta de ciudad. |

Respuesta exitosa (`200`):

```json
{
  "exito": true,
  "proveedores": [],
  "rubros": [],
  "ciudades": [],
  "pagina_actual": 1,
  "total_paginas": 1,
  "total_items": 0
}
```

Los elementos de `proveedores` incluyen `idproveedor`, `nombre`, `cuit`, `direccion`, `mail`, `ciudad`, `telefono`, `rubro` y `activo`. Las opciones de `rubros` y `ciudades` se obtienen como valores distintos no nulos ni vacíos de toda la tabla, sin filtrar por estado. Ante un error de MySQL, la ruta responde `500` con `exito: false`, un mensaje y `redireccion: "/"`.

## Crear un proveedor

El formulario solicita nombre/razón social, CUIT y rubro como campos obligatorios en el navegador. Teléfono, correo, ciudad y dirección son opcionales en la interfaz. El correo usa validación HTML de tipo email. El JavaScript envía estos valores como JSON a `POST /api/proveedores/crear`; si el rubro no está presente en el cuerpo, la ruta usa `"General"` como valor predeterminado.

La operación `Proveedor.crear_proveedor(...)` normaliza ciudad y rubro quitando espacios exteriores y convirtiéndolos a formato título. El CUIT es obligatorio y debe contener números; se ignoran espacios, puntos y guiones al compararlo para detectar duplicados. El valor ingresado se conserva en la fila. La comprobación incluye proveedores activos e inactivos. Nombre, dirección, correo y teléfono se guardan tal como llegan. La fila se crea con `activo = 1`.

Respuesta exitosa (`201`):

```json
{
  "exito": true,
  "mensaje": "Proveedor creado exitosamente"
}
```

Si el CUIT ya está registrado, responde `409` con un mensaje que la interfaz muestra al usuario. Si el CUIT falta o no es válido, responde `400`; si falla la inserción en MySQL, responde `500`. La ruta no devuelve el ID creado. La interfaz vuelve a cargar el listado tras un alta exitosa.

## Modificar un proveedor

Al elegir **Modificar**, el navegador consulta `GET /proveedores/<id>/editar` y carga nombre, CUIT, teléfono, correo, ciudad, dirección y rubro en el modal. La ruta responde `200` con `exito: true` y el objeto `proveedor`; si no encuentra un registro o falla la consulta, responde `500`.

El formulario envía esos campos como JSON a `POST /api/proveedores/<id>/editar`. La operación actualiza los siete campos del proveedor y normaliza ciudad y rubro a formato título. Antes de modificar, bloquea y verifica la existencia del registro y comprueba que el CUIT no pertenezca a otro proveedor (incluidos los inactivos). No modifica `activo`.

La respuesta es `200` si existe el proveedor y la modificación se ejecutó correctamente, incluso si los valores enviados eran iguales a los actuales. Responde `409` si el CUIT pertenece a otro proveedor, `400` si el CUIT falta o no es válido, `404` si el ID no existe y `500` ante un error de base de datos. La verificación de existencia evita confundir un `UPDATE` sin cambios con un ID inexistente.

## Desactivar un proveedor

La acción **Eliminar** pide confirmación y envía `POST /proveedores/<id>/desactivar`. `Proveedor.eliminar_proveedor(id)` bloquea y verifica el registro y solo entonces cambia `activo` de `1` a `0`; no elimina físicamente la fila. Responde `200` si la operación se realizó, `404` si el ID no existe, `409` si ya estaba inactivo y `500` ante un error de base de datos.

La actualización de estado exige que el `UPDATE` afecte exactamente una fila. Si no ocurre, la transacción se revierte en lugar de informar éxito.

## Acceso a datos: métodos de `Proveedor`

### `Proveedor.crear_proveedor(...)`

Inserta un proveedor activo, pero antes busca un CUIT equivalente en toda la tabla, sin excluir inactivos. La comparación ignora espacios, puntos y guiones. Lanza `ProveedorCuitDuplicadoError` ante un duplicado o `ProveedorCuitInvalidoError` si falta el CUIT o contiene caracteres no numéricos; devuelve `True` si confirma la transacción o `None` ante un error de MySQL.

### `Proveedor.leer_proveedores(pagina=1, por_pagina=10, buscar=None, rubro=None, activo=None, ciudad=None)`

Devuelve `(total_items, proveedores, rubros, ciudades, exito)`. Aplica los filtros indicados, ordena los proveedores por `idproveedor` ascendente y pagina el resultado. Si la consulta falla, devuelve `(0, [], [], [], False)`.

### `Proveedor.leer_proveedor(id)`

Busca por `idproveedor` sin filtrar por `activo`. Devuelve `(proveedor, True)` si la consulta se ejecuta, incluso si no hay coincidencia; ante una excepción devuelve `(None, False)`.

### `Proveedor.modificar_proveedor(id, ...)`

Actualiza nombre, CUIT, dirección, correo, ciudad, teléfono y rubro; normaliza ciudad y rubro. Bloquea y verifica el registro con `SELECT ... FOR UPDATE`, excluye su propio ID al revisar la unicidad del CUIT y devuelve `True` si la operación termina correctamente. Lanza `ProveedorNoEncontradoError`, `ProveedorCuitDuplicadoError` o `ProveedorCuitInvalidoError` para esos casos.

### `Proveedor.eliminar_proveedor(id)`

Desactiva lógicamente mediante `activo = 0`. Bloquea y verifica la fila, exige que el `UPDATE` afecte una fila y diferencia proveedor inexistente de proveedor ya inactivo mediante `ProveedorNoEncontradoError` y `ProveedorYaInactivoError`.

## Relación con compras

Las órdenes de compra guardan `idproveedor` en la cabecera y consultan el nombre del proveedor para el listado y el detalle. La pantalla de nueva compra obtiene únicamente proveedores activos. La gestión de proveedores no crea ni modifica órdenes de compra.

## Consideraciones y limitaciones

- La aplicación previene duplicados por CUIT al crear y modificar, comparando CUIT con formato equivalente (espacios, puntos y guiones ignorados) e incluyendo proveedores inactivos. No se detectó una restricción única en la base de datos; ante dos altas concurrentes, la comprobación previa no ofrece una garantía absoluta. Para una garantía a nivel de base hace falta una migración con limpieza de duplicados previos y un índice único sobre un CUIT canónico.
- No hay validación explícita de los datos en las rutas ni comprobación de sesión antes de crear, modificar o desactivar.
- Ciudad y rubro opcionales se convierten a cadena vacía si faltan o llegan como `null`.
- La consulta del listado devuelve listas de rubros y ciudades que incluyen valores de proveedores inactivos.
- La consulta individual permite cargar y modificar proveedores inactivos.
- La búsqueda parcial abarca solo nombre y CUIT; rubro y ciudad se filtran por coincidencia exacta.
- La página solicitada no se limita a un mínimo antes de calcular el `OFFSET`.
- La desactivación no comprueba si el proveedor tiene compras asociadas. El registro se conserva, por lo que las referencias históricas no se borran.