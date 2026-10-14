# Documentación del módulo de ventas

## Objetivo y alcance

El módulo permite crear ventas, descontar existencias, registrar el pago, consultar ventas por cliente y fecha, ver sus ítems y anular una venta. El flujo de creación es:

1. El usuario selecciona productos, cliente y método de pago.
2. El servidor valida la sesión, los artículos y sus precios vigentes, y verifica el stock de todo artículo que no sea un servicio; luego registra la venta, sus ítems y el pago en una transacción.
3. Se descuenta stock para todos los ítems cuyo tipo no sea `servicio`.

Una venta se anula de forma lógica: permanece en la base de datos, se marca inactiva y se reintegra al inventario la cantidad vendida de los ítems no-servicio.

## Archivos involucrados

| Archivo | Responsabilidad |
|---|---|
| `src/modulos/ventas_rutas.py` | Rutas Flask, validación y cálculo de totales. |
| `src/modulos/comandos_db/comandos_db_venta.py` | Consultas y operaciones transaccionales de la clase `Venta`. |
| `src/templates/ventas.html` | Vista de gestión de ventas; extiende `plantailla_gestion.html`. |
| `src/templates/orden_venta.html` | Catálogo y formulario de nueva venta; extiende `plantilla_orden.html`. |
| `src/static/js/ventas.js` | Listado, búsqueda, filtros, paginación, detalle y anulación. |
| `src/static/js/realizar_venta.js` | Catálogo, carrito, selección de cliente y método de pago y envío de la venta. |
| `src/static/css/gestion_ordenes.css` | Estilos específicos de la pantalla de gestión. |
| `src/static/css/ordenes.css` | Estilos generales de la pantalla de creación de órdenes. |

## Rutas

| Método y ruta | Función | Descripción |
|---|---|---|
| `GET /ventas` | `vista_gestion_ventas` | Renderiza la pantalla de gestión. |
| `GET /api/ventas` | `api_ventas` | Devuelve ventas activas, filtros, métricas y paginación. |
| `GET /venta/<id>/detalle` | `vista_detalle_venta` | Devuelve la cabecera de una venta y sus ítems. |
| `POST /api/ventas/anular/<id_venta>` | `api_anular_venta` | Anula una venta activa y reintegra existencias de ítems no-servicio. |
| `GET /ventas/realizar` | `vista_realizar_venta` | Renderiza el catálogo, clientes y métodos de pago activos. |
| `POST /api/ventas/realizar` | `api_procesar_venta` | Registra la venta enviada por el carrito. |

## Pantalla de gestión

La plantilla `ventas.html` presenta:

- botón **Nueva Venta**
- métricas de cantidad de ventas y unidades vendidas
- búsqueda por cliente
- filtros de período: hoy, últimos siete días, último mes, último año o todas las fechas
- tabla con número de venta, fecha, cliente, unidades, precio y acciones
- paginación
- modal de detalle
- confirmación antes de anular

La tabla se carga desde `GET /api/ventas`. El navegador solicita 20 filas por página (valor predeterminado de la ruta), espera 300 ms desde la última escritura antes de buscar y vuelve a la página 1 al cambiar la búsqueda o el período. Las métricas corresponden al conjunto que satisface los filtros, no solo a la página actual.

Las ventas anuladas no aparecen en el listado: la consulta incluye siempre `venta.activa = 1`. Por este motivo, la pantalla no ofrece un filtro para ver ventas anuladas.

### Parámetros de `GET /api/ventas`

| Parámetro | Tipo / valor predeterminado | Comportamiento |
|---|---|---|
| `busqueda` | Texto vacío | Divide la búsqueda por espacios; cada término debe coincidir en nombre o apellido del cliente. |
| `filtro_fecha` | `hoy` | Acepta `hoy`, `semana`, `mes`, `anio` o `todos`. |
| `fecha_inicio` | Opcional | Inicio del rango manual; requiere también `fecha_fin`. |
| `fecha_fin` | Opcional | Fin del rango manual; requiere también `fecha_inicio`. Incluye el día hasta las 23:59:59. |
| `pagina` | `1` | Página solicitada; el acceso a datos asegura un mínimo de 1. |
| `limite` | `20` | Cantidad por página; el acceso a datos asegura un mínimo de 1. |

La interfaz no expone controles de fechas manuales, pero la API acepta ambos parámetros. Si se envía solo uno, no se aplica el rango manual y se continúa con el filtro predefinido. `todos` omite la condición de fecha.

### Respuesta de ejemplo

```json
{
  "ventas": [
    {
      "idventa": 75,
      "numero_factura": 1,
      "fecha": "14/10/2026 17:45",
      "cliente": "María Pérez",
      "cantidad_total_productos": 3,
      "precio_total": 32500.5
    }
  ],
  "paginacion": {
    "pagina_actual": 1,
    "limite": 20,
    "total_registros": 1,
    "total_paginas": 1
  },
  "resumen": {
    "total_ventas": 1,
    "total_productos": 3,
    "total_monto": 32500.5
  },
  "Exito": true
}
```

`fecha` se formatea como `DD/MM/YYYY HH:MM`; `precio_total` se convierte a número decimal para serializarlo como JSON. El resumen suma la cantidad total de productos y los importes de las ventas activas que coinciden con los filtros. Ante un error MySQL, el acceso a datos retorna `Exito: false` y la ruta responde `500` con un mensaje y una redirección.

## Consultar el detalle

La ruta `GET /venta/<id>/detalle` responde con la cabecera y la lista de ítems asociados.

Cabecera consultada:

- `idventa`
- `numero_factura`
- fecha de emisión (solo fecha)
- `descuento`
- cantidad total de productos
- `precio_total`
- nombre completo, teléfono y correo del cliente

Cada ítem contiene su ID, cantidad, precio unitario, nombre de producto e imagen.

Ejemplo:

```json
{
  "exito": true,
  "venta": {
    "idventa": 75,
    "numero_factura": 1,
    "fecha": "2026-10-14",
    "descuento": 0,
    "cantidad_total_productos": 3,
    "precio_total": 32500.5,
    "nombre_cliente": "María Pérez",
    "numero_tel": "1122334455",
    "mail": "maria@example.com"
  },
  "items": [
    {
      "id_item_venta": 32,
      "cantidad": 3,
      "precio_unitario": 10833.5,
      "producto_nombre": "Producto de ejemplo",
      "imagen_producto": "/static/image/producto.png"
    }
  ]
}
```

La pantalla muestra fecha, cliente, total y por cada ítem nombre, cantidad y precio unitario. No muestra el subtotal por ítem. Los botones **Descargar PDF** e **Imprimir** existen en el HTML del modal, pero `ventas.js` no les asigna acciones; actualmente no realizan esas operaciones.

Si el acceso a datos no obtiene la cabecera, devuelve `([], [], False)`, tanto si el ID no existe como si ocurre una excepción. La ruta comprueba primero ese estado y devuelve `500`; por ello, su rama `404` para venta inexistente no se alcanza en ese caso.

## Crear una venta

### Carga inicial y catálogo

`GET /ventas/realizar` carga:

- productos activos con ID, nombre, medidas, tipo, precio, imagen y stock actual
- tipos distintos de productos activos
- clientes activos
- métodos de pago activos

Si falla la carga de datos, renderiza la plantilla con listas vacías, activa `error_db` y responde `500`.

La pantalla permite buscar por nombre y filtrar por tipo. Al agregar repetidamente una tarjeta al carrito, las unidades se acumulan bajo el mismo `idproducto_servicio`. El resumen muestra subtotales y total a partir del precio unitario cargado desde el catálogo.

El cliente predeterminado de la interfaz es el ID `1` (cliente ocasional/general). El método de pago debe seleccionarse explícitamente antes de confirmar.

### Persistencia del carrito

El carrito en memoria contiene, por artículo:

- `idproducto_servicio`
- `nombre`
- `precio_unitario`
- `cantidad`

Al navegar al módulo de clientes, el JavaScript guarda en `localStorage` solo el ID y la cantidad, usando la clave `ordenVentaCarrito`. Al regresar, restaura los productos que sigan presentes en el catálogo activo y tengan cantidad entera positiva; nombre y precio se vuelven a leer de las tarjetas actuales. Un elemento inválido se descarta y se muestra un aviso.

La navegación de cancelación o el cierre del modal vuelve a cargar `/ventas/realizar`; el carrito que no se haya guardado al ir a clientes no se conserva al recargar.

### Solicitud de registro

Al confirmar, `realizar_venta.js` envía `POST /api/ventas/realizar` con JSON:

```json
{
  "id_cliente": 8,
  "id_metodo_pago": 2,
  "descuento": 0,
  "carrito": [
    {
      "idproducto_servicio": 12,
      "precio_unitario": 10833.5,
      "cantidad": 3
    }
  ]
}
```

El navegador deshabilita el botón mientras espera la respuesta. Al éxito elimina el carrito guardado y redirige a `/ventas`.

La ruta:

1. Lee el JSON y rechaza un carrito vacío, artículos mal formados o cantidades/IDs no enteros positivos.
2. Comprueba que exista `session["id_usuario"]`; si falta, responde `401` con una redirección a `/registrarse`.
3. Obtiene el cliente (por defecto ID `1`) y el método de pago (por defecto ID `1` si no se envía).
4. Valida los identificadores de cliente y método de pago, y que el descuento sea numérico, finito y no negativo.
5. Llama a `Venta.registrar(...)` con el ID del empleado de la sesión. La cantidad total y el precio se calculan dentro de la transacción usando los artículos consultados en la base.

En el JavaScript actual el descuento enviado es siempre `0.0`. La ruta también pasa `numero_factura=1` en todas las solicitudes y no ofrece un campo para configurarlo. Esto es intencional mientras no se integre la conexión con un servicio de facturación/legalización; el número actual no se presenta como numeración fiscal legalizada. El método almacena `iva=21.0` por defecto, pero el total se calcula como subtotal menos descuento y no suma el IVA.

El backend valida que el carrito tenga IDs y cantidades enteras positivas. No confía en los precios enviados por el navegador: vuelve a consultar los artículos activos y utiliza sus precios actuales de base de datos para guardar los ítems, el total y el pago. También comprueba stock para todo tipo distinto de `servicio`, bloqueando las filas del inventario durante la transacción; los servicios no descuentan existencias. Un descuento inválido o mayor al subtotal se rechaza.

Respuesta exitosa (`201`):

```json
{
  "exito": true,
  "mensaje": "Venta #75 realizada con éxito.",
  "id_venta": 75,
  "redireccion": "/ventas"
}
```

Un carrito vacío o un dato inválido devuelve `400`; una sesión ausente, `401`; si el registro falla, devuelve `500`. Las demás excepciones de la ruta también se devuelven como `500` con el texto de la excepción en `error`.

### Transacción `Venta.registrar(...)`

El método `Venta.registrar` valida cantidades positivas, agrupa artículos repetidos y lee los precios actuales desde la base como valores decimales. Luego, en una misma transacción:

1. Consulta y bloquea los productos solicitados para validar su existencia, estado activo, precio y stock. El precio recibido del cliente no se utiliza para calcular el total.
2. Inserta la cabecera en `venta` con fecha actual, descuento, IVA, total de unidades, total monetario, cliente, empleado, `activa = 1` y el estado recibido (por defecto `1`).
3. Inserta una fila en `item_venta` por cada artículo con precio unitario y cantidad.
4. Descuenta stock de `producto_servicio` para todo tipo distinto de `servicio`, después de comprobar que hay unidades suficientes.
5. Inserta el pago en `historial_pago_cliente`, asociado al ID de venta, con fecha/hora actual, importe total, método de pago y plazo.
6. Confirma la transacción.

Si una entrada o el stock no son válidos, revierte la transacción y la ruta responde `400` con el motivo. Otros errores de base de datos revierten la transacción, el método devuelve `None` y la ruta responde `500`. La venta, sus ítems, el pago y el movimiento de stock quedan dentro de la misma transacción.

## Anular una venta

La tabla muestra la acción **Eliminar**, que solicita confirmación y llama a `POST /api/ventas/anular/<id_venta>`.

`Venta.anular(id_venta)`:

1. Comprueba que exista la venta y que `activa` sea `1`.
2. Consulta todos sus ítems.
3. Suma al stock la cantidad vendida de cada artículo cuyo tipo no sea `servicio`.
4. Actualiza la venta a `activa = 0`.
5. Confirma la transacción.

La fila y sus ítems permanecen en la base de datos; se trata de una anulación lógica. Una venta inexistente o ya inactiva no se procesa. No hay verificación de stock máximo ni de que el movimiento original se haya aplicado correctamente.

Respuesta exitosa (`200`):

```json
{
  "exito": true,
  "mensaje": "La venta #75 fue anulada y el stock restituido.",
  "redireccion": "/ventas"
}
```

Si `Venta.anular` devuelve falso, la ruta responde `400`; ante una excepción no controlada, responde `500`. Después de una anulación exitosa, el navegador vuelve a cargar el listado, que ya excluye esa venta.

## Acceso a datos: métodos de `Venta`

### `Venta.registrar(...)`

Registra cabecera, ítems, movimiento de stock e historial de pago en una transacción. Retorna el ID de venta en caso de éxito o `None` ante un error.

### `Venta.obtener_ventas_paginadas(...)`

Lista únicamente ventas activas. Admite búsqueda por términos del nombre/apellido del cliente, rango de fechas, paginación y métricas agregadas. Ordena por fecha de emisión e ID descendentes. Devuelve `ventas`, `paginacion`, `resumen` y `Exito`.

### `Venta.obtener_por_id(id_venta)`

Consulta cabecera, cliente e ítems de la venta. Devuelve `(venta, items, estado)`.

### `Venta.anular(id_venta)`

Anula lógicamente una venta y reintegra al stock las cantidades de sus ítems no-servicio.

### `Venta.obtener_datos_inicio_venta()`

Carga productos, tipos, clientes y métodos de pago activos para la pantalla de creación.

## Tablas involucradas

| Tabla | Uso |
|---|---|
| `venta` | Cabecera de la operación, fecha, totales, cliente, empleado y estado activo. |
| `item_venta` | Productos, precios unitarios y cantidades vendidas. |
| `producto_servicio` | Catálogo y existencias; se descuenta al vender y se reintegra al anular, excepto servicios. |
| `cliente` | Cliente asociado y datos que se muestran en listado y detalle. |
| `empleado` | Empleado asociado mediante el ID guardado en la sesión. |
| `metodos_pago` | Métodos activos presentados en el formulario. |
| `historial_pago_cliente` | Registro de pago asociado a la venta. |

Campos principales usados:

- `venta`: `idventa`, `numero_factura`, `fecha_emision_factura`, `descuento`, `iva`, `cantidad_total_productos`, `precio_total`, `idcliente`, `idempleado`, `activa`, `estado`
- `item_venta`: `id_item_venta`, `idventa`, `idproducto_servicio`, `precio_unitario`, `cantidad`
- `producto_servicio`: `idproducto_servicio`, `nombre`, `tipo`, `precio`, `imagen_producto`, `cantidad_actual`, `activo`
- `historial_pago_cliente`: `fecha`, `hora`, `monto`, `idmetodos_pago`, `plazo_pago`, `idventa`

## Resumen del efecto sobre el stock

| Operación | Efecto para tipo `servicio` | Efecto para otros tipos |
|---|---|---|
| Registrar venta | No modifica existencias. | Resta la cantidad vendida; la comprobación de stock suficiente actualmente solo cubre el tipo exacto `producto`. |
| Anular venta activa | No modifica existencias. | Suma nuevamente la cantidad registrada en los ítems. |

La clave de producto que se usa en los ítems es `idproducto_servicio`; las ventas no crean nuevos productos de inventario, sino que enlazan productos existentes.

## Revisión de duplicados

El alta de una venta registra cabecera, ítems, movimientos de stock e historial de pago dentro de una transacción; no inserta productos en el catálogo. No recibe una clave de idempotencia ni comprueba si la solicitud ya fue procesada. Si se reenvía una solicitud de venta, puede registrarse otra venta y descontarse el stock nuevamente. La protección actual contra productos de catálogo repetidos corresponde al alta desde inventario y no a las ventas.