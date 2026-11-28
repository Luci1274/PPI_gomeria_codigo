# Documentación técnica del módulo de ventas

## Descripción general

El módulo permite crear ventas de productos y servicios, consultar el listado y el detalle, imprimir o descargar un comprobante y anular una operación. La cabecera, los ítems, el descuento de stock y el registro de pago se guardan en una transacción.

Archivos principales:

- `src/modulos/ventas_rutas.py`: vistas, API y validación de solicitudes.
- `src/modulos/comandos_db/comandos_db_venta.py`: consultas y transacciones de ventas.
- `src/templates/ventas.html` y `src/static/js/ventas.js`: listado, filtros, detalle, anulación e impresión/PDF.
- `src/templates/orden_venta.html`, `src/templates/plantilla_orden.html` y `src/static/js/realizar_venta.js`: catálogo, carrito y confirmación.
- `docs/estructura_y_datos_DB_27_11_2026.sql`: esquema de referencia.

## Rutas

Las rutas pertenecen a `ventas_bp`.

| Método y ruta | Función | Descripción |
|---|---|---|
| `GET /ventas` | `vista_gestion_ventas` | Renderiza el listado de ventas. |
| `GET /api/ventas` | `api_ventas` | Devuelve resultados paginados y métricas según los filtros. |
| `GET /venta/<id>/detalle` | `vista_detalle_venta` | Devuelve en JSON la cabecera y los ítems. |
| `POST /api/ventas/anular/<id_venta>` | `api_anular_venta` | Anula la venta y repone el stock de sus productos. |
| `GET /ventas/realizar` | `vista_realizar_venta` | Carga productos y servicios activos, tipos, clientes y métodos de pago activos. |
| `POST /api/ventas/realizar` | `api_procesar_venta` | Valida y registra el carrito. |

## Gestión y consulta

El listado permite buscar por nombre o apellido del cliente, filtrar por estado y fecha, definir un rango manual y navegar páginas. El filtro visual inicia con todas las ventas y la fecha de hoy. Para el rango manual se deben completar ambas fechas; si se completa, reemplaza el período predefinido. Las métricas se calculan sobre todos los registros que coinciden con los filtros, no solo sobre la página actual. “Unidades vendidas” incluye las cantidades de productos y servicios.

`GET /api/ventas` acepta:

| Parámetro | Uso |
|---|---|
| `busqueda` | Busca por los términos ingresados en nombre y apellido del cliente. |
| `filtro_fecha` | `hoy` (predeterminado), `semana`, `mes`, `anio` o `todos`. |
| `fecha_inicio`, `fecha_fin` | Intervalo opcional en formato `AAAA-MM-DD`; se requieren ambos. Si se indican, prevalecen sobre el filtro predefinido. |
| `estado` | `1`, `0` o `todos`. La API usa `1` por defecto; la interfaz inicia en `todos`. |
| `pagina` | Página solicitada; predeterminado `1`. |
| `limite` | Resultados por página; predeterminado `20`. |

Los períodos son de calendario: `hoy` cubre el día actual, `semana` los últimos siete días calendario incluyendo hoy, `mes` el mes actual y `anio` el año actual. Los valores de estado, fecha, página, límite e intervalo se validan; los inválidos responden `400`.

La respuesta exitosa contiene `ventas`, `paginacion`, `resumen` y `Exito: true`. `resumen` agrega ventas, unidades y monto para el conjunto filtrado. Una falla de consulta responde `500` con `exito: false`.

El detalle se obtiene al abrir “Ver resumen”. Incluye cliente, fecha, artículos, cantidades, precios unitarios, subtotal, descuento y total. El modal permite imprimir o generar un PDF del comprobante; se utilizan html2canvas y jsPDF cargados desde CDN. Una venta inexistente responde `404` y una falla de consulta, `500`.

## Crear una venta

La pantalla reúne productos y servicios activos en un catálogo común, que se puede buscar por nombre y filtrar por tipo. Cada selección agrega una unidad al carrito; se pueden quitar ítems y revisar el resumen, incluso desde el panel móvil.

Cada ítem se identifica con `tipo_item` (`producto` o `servicio`) e `idproducto_servicio`, ya que las tablas pueden tener IDs coincidentes. Los productos descuentan stock; los servicios no tienen stock. El cliente predeterminado es el registro de consumidor final (`idcliente = 1`) y la interfaz requiere elegir un método de pago.

El descuento es un importe fijo de dinero, no un porcentaje. La interfaz limita el valor al subtotal mostrado y enseña subtotal, descuento y total. Para confirmar, `POST /api/ventas/realizar` recibe JSON:

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

El precio que envía el navegador es una referencia para mostrar la orden, no la fuente del importe guardado. Dentro de la transacción, el servidor vuelve a cargar y bloquear los registros activos, compara sus precios vigentes con los mostrados, verifica el stock y calcula subtotal y total usando los precios de la base de datos. Si cambió un precio o el stock dejó de alcanzar, responde `409` y no registra la venta; hay que actualizar la orden. El descuento se valida contra el subtotal vigente y debe ser finito, no negativo ni superior a este.

El cliente y el método de pago deben seguir activos; también se validan el tipo e identificador de cada artículo, la cantidad y el precio. Datos inválidos, método ausente o carrito vacío responden `400`; precio o stock que cambió, `409`; un error de persistencia, `500`. Si se registra, responde `201` con `exito`, `mensaje`, `id_venta` y `redireccion`. El navegador elimina el carrito y el descuento guardados y vuelve a `/ventas`.

Al navegar a Clientes o al Inventario desde la orden, se guardan en `localStorage` los IDs, tipos, cantidades y descuento. Al regresar se reconstruye el carrito con el catálogo actual y sus precios vigentes; artículos que ya no están disponibles no se restauran. Al volver desde Inventario se usa `/inventario?volver=venta`.

## Persistencia y reglas de negocio

La clase `Venta` coordina las operaciones:

- `obtener_datos_inicio_venta()` carga el catálogo activo, los tipos activos, los clientes activos y los métodos de pago activos.
- `registrar(...)` valida cliente y método de pago activos, comprueba los artículos, bloquea productos para verificar existencias, y vuelve a comprobar los precios. Cabecera, ítems, descuento de stock y pago se confirman juntos o se revierten juntos.
- `venta` guarda cliente, empleado, fecha, descuento, `precio_total`, `iva`, estado y cantidad total de unidades.
- `item_venta` guarda cantidad y precio unitario vigente. Usa `idproducto` para productos o `idservicio` para servicios; el otro campo queda nulo.
- `historial_pago_cliente` guarda un pago por el total de la venta, el método elegido y el plazo (`0`).
- `anular(id_venta)` bloquea la cabecera de la venta para impedir anulaciones simultáneas, marca la venta inactiva y repone únicamente el stock de productos. No elimina los ítems ni el registro del pago.

La pantalla registra ventas completas (`estado = 1`). Aunque existe una columna `iva`, actualmente el valor guardado es `21` y no se suma al total. `numero_factura` se envía como el valor constante `1`; no se genera numeración correlativa. `cantidad_total_productos` suma unidades de productos y servicios, por eso la interfaz la presenta como unidades vendidas.

## Acceso

La protección global de `src/app.py` permite las rutas de venta a `AD`, `DEV` y a `EM`/`EMPLEADO` mediante la lista de endpoints autorizados. Sin sesión, las páginas redirigen al inicio de sesión y las APIs responden `401`; sin permiso, las APIs responden `403` y las páginas redirigen a `/`.
