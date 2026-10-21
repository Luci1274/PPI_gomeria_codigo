# Documentación técnica del módulo de ventas

## Descripción general

El módulo permite crear órdenes de venta de productos y servicios, consultar las ventas registradas, ver el detalle y anular una operación. La venta se persiste en una transacción que incluye la cabecera, los ítems, el ajuste de stock de productos y el historial del pago.

Archivos principales:

- `src/modulos/ventas_rutas.py`: vistas, API y cálculo del total.
- `src/modulos/comandos_db/comandos_db_venta.py`: acceso a datos y transacciones de venta.
- `src/templates/ventas.html` y `src/static/js/ventas.js`: gestión, filtros, detalle y anulación.
- `src/templates/orden_venta.html` y `src/static/js/realizar_venta.js`: catálogo, carrito y confirmación de la venta.
- `src/templates/plantilla_orden.html`: estructura compartida de la pantalla de orden.

## Rutas

Las rutas pertenecen a `ventas_bp`.

| Método y ruta | Función | Descripción |
|---|---|---|
| `GET /ventas` | `vista_gestion_ventas` | Renderiza la gestión de ventas. |
| `GET /api/ventas` | `api_ventas` | Devuelve las ventas activas paginadas y las métricas del filtro. |
| `GET /venta/<id>/detalle` | `vista_detalle_venta` | Devuelve la cabecera y los ítems de una venta. |
| `POST /api/ventas/anular/<id_venta>` | `api_anular_venta` | Anula una venta y repone el stock de sus productos. |
| `GET /ventas/realizar` | `vista_realizar_venta` | Carga el catálogo, tipos activos, clientes y métodos de pago. |
| `POST /api/ventas/realizar` | `api_procesar_venta` | Valida y registra el carrito como una venta. |

El acceso a las rutas se controla mediante la protección de sesión y roles configurada en `src/app.py`.

## Gestión de ventas

La pantalla principal muestra el total de ventas, el total de unidades y una tabla con fecha, cliente, cantidad, precio final y acciones. Permite buscar por cliente, filtrar por fecha y paginar los resultados.

`GET /api/ventas` acepta:

| Parámetro | Uso |
|---|---|
| `busqueda` | Busca por nombre o apellido del cliente. |
| `filtro_fecha` | `hoy` (predeterminado), `semana`, `mes`, `anio` o `todos`. |
| `fecha_inicio`, `fecha_fin` | Si ambos están presentes, filtran un intervalo manual de fechas. |
| `pagina` | Página solicitada; comienza en `1`. |
| `limite` | Cantidad por página; el acceso a datos usa `20` por defecto. |

La respuesta contiene `ventas`, `paginacion`, `resumen` y `Exito`. Los errores de acceso a datos se devuelven con `Exito: false`; la ruta responde `500`.

El detalle se carga desde el botón de resumen. Incluye cliente, fecha, ítems, subtotal, descuento y total pagado. Al anular, la interfaz solicita confirmación y envía POST; si la operación tiene éxito vuelve a cargar el listado.

## Crear una venta

La orden reúne productos y servicios activos en un mismo catálogo. Cada ítem conserva `tipo_item` (`producto` o `servicio`) además del ID porque sus tablas pueden tener identificadores coincidentes. Los productos descuentan stock; los servicios no tienen stock.

El usuario elige cliente y método de pago, agrega ítems al carrito y puede ingresar un **descuento como importe fijo en dinero**, no como porcentaje. El resumen muestra:

- subtotal de los ítems;
- descuento aplicado;
- total a pagar (`subtotal - descuento`).

El descuento no puede ser negativo ni superar el subtotal. La interfaz limita el valor al subtotal vigente y el endpoint vuelve a validar estos límites. La orden confirma los mismos importes antes de enviarla. Al navegar a Inventario para agregar un servicio, se conservan el carrito y el descuento en `localStorage`.

El endpoint `POST /api/ventas/realizar` recibe JSON con:

```json
{
  "id_cliente": 1,
  "id_metodo_pago": 1,
  "descuento": 250.00,
  "carrito": [
    {
      "idproducto_servicio": 12,
      "tipo_item": "producto",
      "precio_unitario": 145000.00,
      "cantidad": 1
    }
  ]
}
```

`descuento` es una cantidad monetaria y usa `0` cuando no se aplica. El servidor valida que sea numérico, finito, no negativo y menor o igual al subtotal del carrito; los valores inválidos responden `400`. El endpoint también exige un carrito y una sesión válida.

Si la venta se registra, responde `201` con `exito`, `mensaje`, `id_venta` y `redireccion`. Los errores de registro responden `500`. Tras el éxito, el navegador elimina el carrito y el descuento guardados y redirige a `/ventas`.

## Acceso a datos y persistencia

La clase `Venta`, en `comandos_db_venta.py`, realiza las operaciones principales:

- `obtener_datos_inicio_venta()` carga productos, servicios, tipos, clientes activos y métodos de pago activos.
- `registrar(...)` valida la estructura del carrito, comprueba que los productos y servicios sigan activos, bloquea y verifica el stock de productos, y abre una transacción.
- La cabecera se guarda en `venta`, incluidos `descuento`, `cantidad_total_productos` y `precio_total`.
- Cada ítem se guarda en `item_venta` con `idproducto` o `idservicio`, dejando el otro identificador nulo.
- Solo se descuenta stock de la tabla `producto`.
- El importe final se guarda como monto en `historial_pago_cliente`, junto al método de pago y la venta.
- `obtener_ventas_paginadas(...)` lista ventas activas, agrega métricas y aplica los filtros solicitados.
- `obtener_por_id(id_venta)` carga cabecera e ítems; incluye el descuento para mostrarlo en el detalle.
- `anular(id_venta)` marca la venta inactiva y repone el stock únicamente de los productos asociados.

Los datos corresponden a las tablas `venta`, `item_venta`, `producto`, `servicio`, `cliente`, `empleado`, `metodos_pago` e `historial_pago_cliente`, según el esquema actual de `docs/comandos_creacion_db.sql`.

## Consideraciones para continuar

- `precio_total` se calcula restando el descuento al subtotal recibido en el carrito. Aunque la tabla tiene un campo `iva`, el cálculo actual no agrega IVA al total.
- Los precios unitarios se reciben desde el navegador y se utilizan para calcular y persistir la venta. Para evitar manipulación del importe desde una petición modificada, convendría obtener el precio vigente desde la base de datos al registrar y usar el precio enviado solo como referencia de interfaz.
- `numero_factura` se envía actualmente con el valor constante `1`; no se genera un número correlativo.
- `cantidad_total_productos` suma las unidades de todos los ítems del carrito, también los servicios, pese al nombre de la columna.
- La anulación repone existencias de productos y marca la venta inactiva; no elimina físicamente la venta ni sus ítems.