# Documentación del módulo de compras

## Objetivo y alcance

El módulo administra órdenes de compra a proveedores y el ingreso de mercadería al inventario. Una orden pasa por dos momentos:

1. **Registro:** se guarda la orden y sus cantidades pedidas. Todavía no se modifica el stock.
2. **Completar / confirmar recepción:** se registran las cantidades efectivamente recibidas y se actualiza el stock. La operación solo puede completarse una vez.

Las órdenes también se pueden consultar, filtrar y anular. Si se anula una orden ya completada, se revierte del inventario la cantidad que había sido recibida. Si se anula antes de completarla, no se modifica el stock.

## Archivos involucrados

| Archivo | Responsabilidad |
|---|---|
| `src/modulos/compras_rutas.py` | Rutas Flask, validación de las solicitudes y respuestas HTTP. |
| `src/modulos/comandos_db/comandos_db_compra.py` | Consultas, transacciones y lógica de persistencia de la clase `Compra`. |
| `src/templates/compra.html` | Vista de gestión de órdenes; extiende `plantailla_gestion.html`. |
| `src/templates/orden_compra.html` | Catálogo y formulario de nueva orden; extiende `plantilla_orden.html`. |
| `src/static/js/compras.js` | Listado, filtros, paginación, detalle, recepción y anulación. |
| `src/static/js/realizar_compra.js` | Catálogo, carrito y envío de una nueva orden. |
| `src/static/css/gestion_ordenes.css` | Estilos específicos referenciados por la plantilla de gestión. |
| `src/static/css/ordenes.css` | Estilos generales de la plantilla de creación de órdenes. |

## Modelo de estados

La tabla `compra` maneja dos atributos de estado independientes:

- `activo`: `1` indica que la orden está activa; `0`, que fue anulada.
- `completo`: `0` indica que aún no se confirmó la recepción; `1`, que se completó.

El estado de recepción no significa que se haya recibido necesariamente la cantidad pedida en todos los ítems. Al confirmar, el usuario informa las cantidades reales, que pueden ser cero, menores o mayores que lo solicitado.

| `activo` | `completo` | Significado | Efecto en stock |
|---:|---:|---|---|
| 1 | 0 | Orden activa pendiente de recepción | Ninguno hasta confirmar. |
| 1 | 1 | Orden activa con recepción confirmada | Ya se ingresaron las cantidades recibidas, excepto servicios. |
| 0 | 0 | Orden pendiente anulada | No se revierte stock porque no se había ingresado. |
| 0 | 1 | Orden completada y luego anulada | Se revierte la cantidad recibida, excepto servicios. |

No hay un flujo implementado para reactivar una orden anulada o para completar parcialmente una orden en varias etapas.

## Rutas

| Método y ruta | Función | Descripción |
|---|---|---|
| `GET /compras` | `vista_gestion_compras` | Renderiza la pantalla de gestión. |
| `GET /api/compras` | `api_compras` | Devuelve el listado, las métricas y los datos de paginación con filtros. |
| `GET /api/compras/<id>/detalle` | `vista_detalle_compra` | Devuelve la cabecera y los ítems de una orden. |
| `GET /compra/<id>/detalle` | `vista_detalle_compra` | Alias alternativo de la ruta de detalle. |
| `POST /api/compras/realizar` | `api_realizar_compra` | Registra una orden pendiente. |
| `POST /compras/completar` | `completar_compra` | Registra las cantidades recibidas y completa la orden. |
| `POST /api/compras/anular/<id_compra>` | `api_anular_compra` | Anula una orden y, si ya estaba completada, revierte el stock recibido. |
| `GET /compras/realizar` | `vista_realizar_compra` | Renderiza el catálogo para crear una orden. |

## Pantalla de gestión

La pantalla `compra.html` muestra:

- acceso a **Nueva Orden de Compra**
- métricas de total de compras y total de productos
- búsqueda de orden por número o proveedor
- filtro por fecha: hoy, últimos siete días, último mes, último año o todas las fechas
- filtro de estado activo/anulado/todos
- filtro de recepción completa/incompleta/todas
- tabla con número, fecha, proveedor, tipos de producto, cantidad total, estado de recepción y acciones
- modal para consultar el detalle o completar una orden pendiente
- confirmación antes de anular una orden
- paginación de resultados

La búsqueda se consulta luego de 300 ms sin nuevas pulsaciones. Al cambiar un filtro se vuelve a la primera página. El listado carga la primera página al abrir la vista y solicita hasta 20 órdenes por página.

Las acciones disponibles dependen de los estados:

- **Ver resumen** está disponible en las filas listadas.
- **Completar** se muestra solo para órdenes activas incompletas.
- **Anular** se muestra solo para órdenes activas.

La columna `Estado` de la tabla representa si la recepción está completa o incompleta. El filtro `estado` de la API, en cambio, corresponde a `activo` (vigente/anulada). Las órdenes anuladas se representan visualmente con una clase de fila y no ofrecen la acción de volver a anular.

### Filtros de `GET /api/compras`

| Parámetro | Tipo / valor predeterminado | Valores y comportamiento |
|---|---|---|
| `busqueda` | Texto vacío | Coincidencia parcial en el ID de compra o el nombre del proveedor. |
| `filtro_fecha` | `hoy` | `hoy`, `semana`, `mes`, `anio` o `todos`. |
| `fecha_inicio` | Opcional | Inicio de rango manual; se aplica solo si también se envía `fecha_fin`. |
| `fecha_fin` | Opcional | Fin de rango manual; se aplica solo si también se envía `fecha_inicio`. |
| `estado` | `1` | `1` activas, `0` anuladas, `todos` para no filtrar por `activo`. |
| `completo` | Sin filtro en la ruta | `1` completas, `0` incompletas, `todos` para no filtrar por recepción. |
| `pagina` | `1` | Página solicitada; se limita al intervalo disponible. |
| `limite` | `20` | Tamaño de página; la consulta asegura un mínimo de 1. |

El filtro de fecha del formulario manual no está presente en la interfaz actual, aunque la API admite `fecha_inicio` y `fecha_fin`. El rango predefinido se aplica como fecha mayor o igual al límite calculado por MySQL; `todos` no agrega condición de fecha.

### Respuesta del listado

Una respuesta exitosa tiene la estructura siguiente:

```json
{
  "compras": [
    {
      "idcompra": 42,
      "fecha": "04/10/2026",
      "horas": "15:30:00",
      "proveedor": "Gomería Central",
      "tipo": "insumo, herramienta",
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

`total_productos` y la métrica homónima se calculan sumando `compra.cantidad_total`, es decir, las cantidades **pedidas**, no las recibidas. Las métricas respetan los filtros aplicados y se calculan sobre todas las coincidencias, no solo sobre la página visible. Cuando no hay coincidencias, el método de datos calcula una página y cero registros.

La API devuelve `500` si falla la consulta a la base de datos, con `Exito: false`, un mensaje y una redirección.

> **Desajuste actual de nombres:** la consulta devuelve los tipos agrupados en `tipo`, pero `compras.js` intenta mostrar `tipos_producto`. Como resultado, la columna de tipos puede aparecer como `0 tipos` aunque la orden tenga productos. El resto de la respuesta conserva la clave `tipo`.

## Consultar el detalle

Al pedir el resumen, el navegador consulta `GET /api/compras/<id>/detalle`. La respuesta incluye:

- `compra`: `idcompra`, `fecha`, `horas`, `proveedor`, `total_productos`, `activo` y `completo`
- `items`: `iditem_compra`, `producto_nombre`, `cantidad_pedida`, `cantidad_entregada` y `tipo`

Ejemplo:

```json
{
  "exito": true,
  "compra": {
    "idcompra": 42,
    "fecha": "04/10/2026",
    "horas": "15:30:00",
    "proveedor": "Gomería Central",
    "total_productos": 12,
    "activo": 1,
    "completo": 0
  },
  "items": [
    {
      "iditem_compra": 15,
      "producto_nombre": "Kit de reparación",
      "cantidad_pedida": 12,
      "cantidad_entregada": 0,
      "tipo": "insumo"
    }
  ]
}
```

Las fechas se serializan como `DD/MM/YYYY` y las horas como texto. La respuesta exitosa incluye el encabezado `Cache-Control: no-store`.

En la implementación actual, `Compra.obtener_por_id` devuelve un estado falso tanto si no encuentra la compra como ante un error de consulta. Por eso, la ruta responde `500` en ambos casos; aunque existe una rama preparada para `404`, la ausencia de la compra no llega a esa rama.

## Crear una orden

### Carga del catálogo

`GET /compras/realizar` obtiene de la base de datos:

- productos activos, ordenados por cantidad actual ascendente
- tipos distintos de productos activos para el filtro
- proveedores activos

La pantalla muestra el nombre, tipo, medidas, cantidad actual y mínima del producto. La búsqueda filtra por nombre y el selector filtra por tipo. En dispositivos pequeños se puede abrir/cerrar el panel del carrito.

### Carrito

`realizar_compra.js` mantiene el carrito en memoria y lo guarda en `localStorage` bajo la clave `ordenCompraCarrito` al abrir la sección de proveedores. Al volver a la pantalla, restaura únicamente los ítems cuyo ID sigue presente en el catálogo activo y cuya cantidad sea un entero positivo.

Al agregar varias veces el mismo producto, el carrito acumula la cantidad para ese mismo `idproducto_servicio`. El resumen muestra las unidades totales; el modal de confirmación requiere al menos un producto y un proveedor.

### Solicitud de registro

Al confirmar se envía `POST /api/compras/realizar` con JSON:

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

La ruta valida que el cuerpo sea un objeto JSON, que el ID de proveedor y los IDs de producto sean enteros positivos, que el carrito no esté vacío y que todas las cantidades sean enteros positivos. Calcula `total_productos` como la suma de cantidades y llama a `Compra.registrar`.

Respuesta exitosa (`200`):

```json
{
  "exito": true,
  "mensaje": "Compra registrada exitosamente con ID 43.",
  "id_compra": 43,
  "redireccion": "/compras"
}
```

Un cuerpo o carrito inválido devuelve `400`; un error al registrar en la base de datos devuelve `500`. Tras el éxito, el JavaScript elimina el carrito guardado y redirige a `/compras`.

### Persistencia inicial

`Compra.registrar(id_proveedor, listado_items, total_productos, fecha=None)` crea en una transacción:

1. Una fila en `compra` con fecha, hora, proveedor, cantidad total, `activo = 1` y `completo = 0`.
2. Una fila en `item_compra` por cada producto, guardando `idproducto_servicio`, `idcompra` y `cantidad_pedida`.

**No modifica `producto_servicio.cantidad_actual` en este paso.** Si falla una consulta MySQL, la transacción se revierte y el método devuelve `(None, False)`; si termina correctamente, devuelve `(id_compra, True)`.

## Completar / confirmar la recepción

La acción **Completar** abre el detalle en modo de recepción. El usuario ingresa la `cantidad_entregada` de cada ítem; se permiten enteros desde cero. El formulario envía a `POST /compras/completar`:

- `id_compra`
- una lista de `iditem_compra`
- una lista alineada de `cantidad_recibida`

Ejemplo de campos de formulario:

```text
id_compra=42
iditem_compra=15
cantidad_recibida=10
iditem_compra=16
cantidad_recibida=0
```

La ruta valida que el ID de compra sea positivo, que haya ítems, que las dos listas tengan igual longitud, que los IDs no se repitan y que las cantidades recibidas sean enteros no negativos. Si la validación falla, responde `400`.

`Compra.completar_compra(id_compra, cantidad_entregada_por_item)` realiza lo siguiente dentro de una transacción:

1. Bloquea la fila de la orden con `SELECT ... FOR UPDATE`.
2. Rechaza órdenes inexistentes, anuladas o ya completas.
3. Bloquea los ítems y comprueba que se haya enviado exactamente el conjunto de IDs de la orden (sin omisiones ni IDs ajenos).
4. Actualiza `cantidad_entregada` para cada ítem.
5. Suma al inventario la cantidad recibida de los tipos distintos de `servicio`.
6. Marca la compra como `completo = 1` y confirma la transacción.

El stock se actualiza una sola vez por orden: una solicitud repetida ya no pasa la validación de orden pendiente. Para los servicios se guarda la cantidad recibida, pero no se actualiza `cantidad_actual`.

Respuesta exitosa (`200`):

```json
{
  "exito": true,
  "mensaje": "Compra completada exitosamente.",
  "redireccion": "/compras"
}
```

La ruta devuelve `500` si el método no puede completar la operación. El navegador informa el resultado y vuelve a cargar el listado.

## Anular una orden

La interfaz pide confirmación y luego llama a `POST /api/compras/anular/<id_compra>`.

`Compra.anular(id_compra)`:

1. Comprueba que la compra exista y que siga activa.
2. Si está completa, obtiene `cantidad_entregada` de sus ítems y resta esas cantidades del stock para todos los tipos distintos de `servicio`.
3. Si está incompleta, no cambia el stock.
4. Marca `compra.activo = 0` y confirma la transacción.

La anulación es lógica: la fila de la compra y sus ítems se conservan. No se puede volver a anular una compra ya anulada. La operación no comprueba que el stock actual alcance para restar lo recibido, por lo que la anulación de una orden completada puede dejar una cantidad negativa si ese stock ya fue consumido o ajustado por otros movimientos.

Respuesta exitosa (`200`):

```json
{
  "exito": true,
  "mensaje": "La compra #42 fue anulada y el stock ajustado.",
  "redireccion": "/compras"
}
```

Si el método no puede anularla, la ruta responde `400`; ante una excepción no controlada, responde `500`.

## Acceso a datos: resumen de métodos

### `Compra.obtener_compras_paginadas(...)`

Aplica los filtros de estado activo, texto, estado de recepción y fecha. Obtiene métricas, limita la página y ordena las órdenes por fecha, hora e ID descendentes. Devuelve un diccionario con `compras`, `paginacion`, `resumen` y `Exito`.

### `Compra.obtener_por_id(id_compra)`

Consulta la cabecera de una orden, el nombre del proveedor y los ítems vinculados a `producto_servicio`. Devuelve `(compra, items, estado)`.

### `Compra.obtener_datos_inicio_compra()`

Consulta el catálogo, los tipos y los proveedores activos para renderizar la pantalla de creación. Devuelve `(productos, tipos, proveedores, estado)`.

### `Compra.completar_compra(id_compra, cantidad_entregada_por_item)`

Registra las cantidades recibidas y actualiza el stock una vez. La actualización de stock excluye `tipo = 'servicio'`.

### `Compra.anular(id_compra)`

Marca la orden inactiva. Si estaba completa, revierte las unidades realmente recibidas, excluyendo servicios.

## Tablas y campos utilizados

| Tabla | Uso en el módulo |
|---|---|
| `compra` | Cabecera: fecha, hora, cantidad total pedida, proveedor, estado activo y estado completo. |
| `item_compra` | Detalle: producto, cantidad pedida y cantidad entregada. |
| `producto_servicio` | Catálogo y stock actual; se actualiza al completar o anular una orden completa, excepto para servicios. |
| `proveedor` | Proveedor asociado a la orden y listado de proveedores activos. |

Campos de compra consultados o escritos:

- `compra`: `idcompra`, `fecha`, `horas`, `cantidad_total`, `idproveedor`, `activo`, `completo`
- `item_compra`: `iditem_compra`, `idproducto_servicio`, `idcompra`, `cantidad_pedida`, `cantidad_entregada`
- `producto_servicio`: `idproducto_servicio`, `nombre`, `tipo`, `medidas`, `imagen_producto`, `cantidad_actual`, `cantidad_minima`, `activo`
- `proveedor`: `idproveedor`, `nombre`, `telefono`, `mail`, `activo`

## Interfaz y funcionalidades aún no conectadas

La plantilla de gestión incluye botones **Descargar PDF** e **Imprimir** en el modal de detalle. `compras.js` los oculta en el modo de completar, pero no registra manejadores para esos botones; actualmente no ejecutan una acción.

El módulo no envía un costo unitario ni un importe total de compra en el payload y las consultas de detalle no obtienen precios. El resumen de la orden contabiliza unidades, no valores monetarios.

## Resumen del flujo de stock

| Operación | Orden completa | Efecto en stock para productos no `servicio` |
|---|---:|---|
| Registrar orden | No | Ninguno. |
| Completar recepción | Pasa a completa | Suma `cantidad_entregada` por ítem. |
| Anular orden incompleta | No | Ninguno. |
| Anular orden completa | Sí | Resta `cantidad_entregada` por ítem. |

Las cantidades pedidas se conservan como parte del detalle, pero el inventario sigue las cantidades efectivamente recibidas.

## Revisión de duplicados

El alta de una compra inserta una cabecera y sus ítems, que referencian artículos existentes por `idproducto_servicio`; no inserta productos en el catálogo. La operación es transaccional, pero no recibe una clave de idempotencia ni comprueba si la solicitud ya fue procesada. Si se reenvía una solicitud de compra, puede crearse otra orden y volver a impactar el stock al confirmar su recepción. La protección actual contra productos de catálogo repetidos corresponde al alta desde inventario y no a las compras.
