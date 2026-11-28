# Documentación técnica del módulo de compras

## Descripción general

El módulo permite crear órdenes de compra, registrar la recepción de sus productos, consultar y filtrar órdenes, ver su detalle, descargar un resumen en PDF y anular órdenes. La compra se crea como incompleta; el inventario se actualiza al confirmar las cantidades recibidas.

Archivos principales:

- Rutas Flask: `src/modulos/compras_rutas.py`.
- Acceso a datos: `src/modulos/comandos_db/comandos_db_compra.py`.
- Listado y detalle: `src/templates/compra.html` y `src/static/js/compras.js`.
- Alta de órdenes: `src/templates/orden_compra.html` y `src/static/js/realizar_compra.js`.
- Plantillas base: `src/templates/plantilla_orden.html` y `src/templates/plantailla_gestion.html`.

## Rutas

| Método y ruta | Función | Resultado |
|---|---|---|
| `GET /compras` | `vista_gestion_compras` | Renderiza el listado de compras. |
| `GET /api/compras` | `api_compras` | Devuelve resultados filtrados y paginados. |
| `GET /api/compras/<id>/detalle` | `vista_detalle_compra` | Devuelve cabecera e ítems de una orden. |
| `GET /compra/<id>/detalle` | `vista_detalle_compra` | Alias de la ruta de detalle. |
| `POST /api/compras/anular/<id_compra>` | `api_anular_compra` | Anula la orden y revierte el stock recibido, si corresponde. |
| `GET /compras/realizar` | `vista_realizar_compra` | Renderiza el catálogo para crear una orden. |
| `POST /api/compras/realizar` | `api_realizar_compra` | Registra una orden incompleta. |
| `POST /compras/completar` | `completar_compra` | Registra cantidades recibidas y actualiza el stock. |

## Pantalla de gestión de compras

`GET /compras` renderiza `compra.html`. La pantalla incluye métricas, filtros, tabla paginada, modal de detalle y acciones para completar o anular órdenes.

### Filtros y métricas

| Filtro | Parámetro de API | Valores / comportamiento |
|---|---|---|
| Texto | `busqueda` | Coincidencia parcial por número de orden o nombre del proveedor. |
| Fecha | `filtro_fecha` | `hoy`, `semana`, `mes`, `anio` o `todos`. La pantalla inicia en `hoy`. |
| Estado | `estado` | `1` activa, `0` anulada o `todos`. La pantalla inicia en `todos`. |
| Recepción | `completo` | `1` completa, `0` incompleta o `todos`. La pantalla inicia en `0` (incompletas). |

La API también acepta `fecha_inicio` y `fecha_fin` para un rango manual, pero la pantalla no presenta controles para esos parámetros. El rango manual se aplica cuando se envían ambas fechas. La búsqueda no incluye la fecha.

Si no se especifican, la API usa `filtro_fecha=hoy`, `estado=1`, `completo` sin filtro, `pagina=1` y `limite=20`. La pantalla envía sus propias opciones iniciales: `hoy`, `todos` los estados, órdenes `incompletas`, página 1 y el límite predeterminado.

Los rangos `mes` y `anio` corresponden al mes calendario actual y al año calendario actual. `semana` usa como inicio la fecha de hoy menos siete días.

Las métricas de total de compras y unidades se calculan sobre el conjunto que coincide con los filtros actuales, no solo sobre la página visible. Las unidades corresponden a `compra.cantidad_total` (cantidad pedida), incluso para órdenes todavía incompletas.

La tabla muestra número, fecha, proveedor, tipos de producto, cantidad total pedida, estado de anulación, estado de recepción y acciones. Los tipos que se muestran son los nombres distintos asociados a los productos de la orden. La paginación usa 20 elementos por página de forma predeterminada; la API acepta `limite` y normaliza página y límite a valores válidos.

Las órdenes anuladas se resaltan y no ofrecen acciones para anular o completar. Las órdenes activas incompletas ofrecen `Completar`; las activas completas permiten ver el resumen y anular.

### `GET /api/compras`

Devuelve JSON con esta estructura:

```json
{
  "compras": [
    {
      "idcompra": 42,
      "fecha": "04/10/2026",
      "horas": "15:30:00",
      "proveedor": "Gomería Central",
      "tipo": "Neumáticos, Bandas",
      "total_productos": 12,
      "estado": 1,
      "completo": 0
    }
  ],
  "paginacion": {
    "pagina_actual": 1,
    "limite": 20,
    "total_registros": 42,
    "total_paginas": 3
  },
  "resumen": {
    "total_compras": 42,
    "total_productos": 321
  },
  "Exito": true
}
```

`tipo` es una lista de nombres de tipos separados por coma; puede ser `null` si no hay tipos asociados. `estado` refleja `compra.activo`. `Exito` se escribe con mayúscula inicial. Cuando no hay compras, la consulta devuelve una página; si falla la base de datos, la API responde `500` con `exito: false`, un mensaje y una redirección a `/`.

## Detalle de una compra

La misma respuesta se obtiene por cualquiera de estas rutas:

- `GET /api/compras/<id>/detalle`
- `GET /compra/<id>/detalle`

La respuesta exitosa contiene `compra` e `items`. La cabecera incluye `idcompra`, `fecha`, `horas`, `proveedor`, `total_productos`, `activo` y `completo`. Cada ítem incluye `iditem_compra`, `producto_nombre`, `tipo`, `cantidad_pedida` y `cantidad_entregada`.

El detalle responde `404` si no existe la orden y `500` si ocurre un error de acceso a datos. La respuesta exitosa incluye `Cache-Control: no-store`.

El modal permite consultar el resumen y descargarlo como PDF con las bibliotecas `html2canvas` y `jsPDF`, cargadas desde CDN en `compra.html`.

## Crear una orden

`GET /compras/realizar` carga `orden_compra.html` con productos activos, tipos activos y proveedores activos. Si falla la consulta inicial, renderiza la vista sin esos datos, marca `error_db` y responde `500`.

La pantalla permite:

- buscar productos por nombre y filtrar por tipo;
- agregar productos al carrito haciendo clic; cada clic agrega una unidad;
- quitar productos y consultar el total de unidades pedidas;
- elegir un proveedor antes de revisar y registrar la orden;
- abrir el resumen del carrito en una vista lateral, adaptada a pantallas pequeñas.

El catálogo muestra el stock actual y la cantidad mínima como referencia. El carrito se guarda en `localStorage` con la clave `ordenCompraCarrito` al abrir la pantalla de proveedores. Al regresar, restaura solo productos que sigan presentes en el catálogo y cantidades enteras positivas; los elementos inválidos se descartan. El proveedor seleccionado no se guarda en ese carrito. Tras registrar la orden, se elimina el carrito guardado.

### `POST /api/compras/realizar`

Recibe JSON con un proveedor y una lista de productos y cantidades:

```json
{
  "id_proveedor": 3,
  "carrito": [
    {
      "idproducto_servicio": 12,
      "cantidad": 5
    },
    {
      "idproducto_servicio": 18,
      "cantidad": 2
    }
  ]
}
```

La ruta convierte el identificador de proveedor, los identificadores de producto y las cantidades con `int()`, y exige valores positivos y un carrito no vacío. Devuelve `400` ante datos inválidos y `500` si falla el registro. Si tiene éxito, responde `200`:

```json
{
  "exito": true,
  "mensaje": "Compra registrada exitosamente con ID 43.",
  "id_compra": 43,
  "redireccion": "/compras"
}
```

La interfaz muestra el resultado y redirige a `/compras`.

## Completar una orden y actualizar stock

Al completar una orden se registra la cantidad recibida de cada ítem. Desde la tabla, `Completar` abre el detalle en modo edición; el usuario puede ingresar cantidades enteras desde cero. El formulario envía `id_compra`, `iditem_compra` y `cantidad_recibida` mediante `POST /compras/completar`.

La ruta valida que el identificador de compra y los identificadores de ítem sean positivos, que haya ítems, que ambas listas tengan el mismo tamaño, que las cantidades sean enteras no negativas y que no se repita un identificador de ítem. La capa de datos comprueba que la orden exista, esté activa e incompleta, y que se hayan recibido exactamente todos sus ítems.

En una transacción, `Compra.completar_compra(...)` guarda cada cantidad recibida, suma esas cantidades al stock de `producto.cantidad_actual` y marca la orden `completo = 1`. El stock no se modifica al crear la orden.

La cantidad recibida no se compara con la cantidad pedida: se puede finalizar la orden con una cantidad menor, igual, mayor o incluso cero. El flag `completo` indica que se cerró el proceso de recepción, no que se recibió exactamente lo solicitado.

La ruta responde `400` ante datos inválidos, `500` si la operación no se pudo completar y `200` si finaliza correctamente. En caso de éxito, la interfaz cierra el modal, notifica el resultado y vuelve a cargar el listado.

## Anular una orden

`POST /api/compras/anular/<id_compra>` anula una orden activa. La anulación es lógica: cambia `compra.activo` a `0`.

- Si la orden ya estaba completa, descuenta del stock las cantidades realmente recibidas (`item_compra.cantidad_entregada`).
- Si estaba incompleta, no modifica el stock, porque todavía no se había actualizado.

La interfaz pide confirmación antes de enviar la solicitud. Una anulación exitosa responde `200`; si la orden no existe o ya estaba anulada, la ruta responde `400`. Los errores inesperados responden `500`. No existe una operación para reactivar órdenes anuladas.

## Clase `Compra` y persistencia

### `Compra.registrar(id_proveedor, listado_items, total_productos, fecha=None)`

Inserta la cabecera con fecha, hora, cantidad total pedida, proveedor, `activo = 1` y `completo = 0`; después inserta las líneas en `item_compra` con `cantidad_pedida`. Las operaciones se confirman en una transacción. No actualiza el stock ni registra precios de compra.

Devuelve `(id_compra, True)` si se registra correctamente o `(None, False)` ante un error de MySQL.

### `Compra.obtener_compras_paginadas(...)`

Combina filtros de estado, texto, recepción y fecha. Calcula totales sobre todos los resultados filtrados y obtiene la página solicitada. El listado devuelve `compras`, `paginacion`, `resumen` y `Exito`.

### `Compra.obtener_por_id(id_compra)`

Consulta la cabecera y las líneas de la compra, incluyendo cantidades pedidas y recibidas. Devuelve `(compra, items, True)` cuando encuentra la orden, `(None, [], True)` si la consulta se ejecuta pero no hay una orden con ese ID, y `([], [], False)` ante un error.

### `Compra.completar_compra(id_compra, cantidad_entregada_por_item)`

Bloquea la orden y sus ítems durante la transacción, valida que siga activa e incompleta y que el mapa contenga exactamente todos los ítems. Guarda las cantidades recibidas, actualiza el inventario y marca la orden completa. Devuelve `False` si no cumple las condiciones o si falla MySQL.

### `Compra.anular(id_compra)`

Marca la orden como inactiva. Si estaba completa, revierte únicamente las cantidades registradas como recibidas. Devuelve `False` si no existe, ya está anulada o falla MySQL.

### `Compra.obtener_datos_inicio_compra()`

Devuelve `(productos, tipos, proveedores, estado)`, usando productos, tipos y proveedores activos. Los productos se ordenan por stock actual ascendente.

## Tablas y campos utilizados

- `compra`: `idcompra`, `fecha`, `horas`, `cantidad_total`, `idproveedor`, `activo`, `completo`.
- `item_compra`: `iditem_compra`, `idproducto`, `idcompra`, `cantidad_pedida`, `cantidad_entregada`.
- `producto`: `idproducto`, `nombre`, `idtipo`, `cantidad_actual`, `cantidad_minima`, además de los datos de catálogo que presenta la pantalla.
- `tipos`: proporciona el nombre del tipo asociado al producto.
- `proveedor`: identifica el proveedor de la orden.

## Consideraciones

- El listado tiene paginación y filtros asíncronos; los cambios de filtros restablecen la página a la primera.
- El carrito se persiste solo al navegar al listado de proveedores, no en cada cambio ni junto con el proveedor seleccionado.
- El flujo de compra no captura un precio de costo por ítem.
- La validación en servidor cubre el formato y los valores básicos del pedido y de la recepción; las rutas de este módulo no implementan una comprobación de sesión propia.
