# Reglas de negocio

Las reglas siguientes fueron contrastadas con la implementación actual. Las reglas marcadas como “pendientes” existen en el modelo o en documentación inicial, pero no están completamente automatizadas por el código.

## Hechos implementados

1. Los usuarios deben iniciar sesión para utilizar las funciones protegidas.
2. Los roles `AD` y `DEV` tienen acceso administrativo completo.
3. Los roles `EM` y `Empleado` tienen acceso limitado al inicio y a las rutas de ventas habilitadas.
4. Los registros principales pueden desactivarse sin eliminarse físicamente.
5. Los productos tienen stock actual y stock mínimo.
6. Los servicios no tienen stock ni movimientos de inventario.
7. Las compras se registran inicialmente como incompletas y no afectan el stock hasta completar la recepción.
8. Las ventas descuentan stock de productos y conservan el precio vigente al confirmarse.
9. Las ventas pueden registrar un cliente; si no se selecciona uno, la interfaz usa el consumidor final.
10. La anulación de operaciones se realiza mediante baja lógica.

## Restricciones

1. El nombre de usuario de empleado debe ser único.
2. El CUIT de cliente y proveedor debe ser único en la base de datos.
3. Un producto no puede duplicarse por la combinación nombre, tipo, marca y medidas.
4. Un servicio no puede duplicarse por nombre.
5. Una venta no puede confirmar un carrito vacío, una cantidad inválida o un método de pago inactivo.
6. Antes de confirmar una venta, el servidor vuelve a verificar los precios vigentes y el stock disponible.
7. Una compra no puede completarse si la orden está anulada, ya está completa o no incluye exactamente todos sus ítems.
8. Las cantidades recibidas de una compra pueden ser menores, iguales, mayores o iguales a cero que las pedidas; el sistema permite cerrar la recepción con cualquiera de esos valores.
9. La baja de una compra completa revierte únicamente las cantidades registradas como entregadas.
10. Una venta anulada no elimina ítems ni pagos; repone únicamente el stock de sus productos.

## Acciones disparadoras

1. Al confirmar una venta, se crea la cabecera, los ítems, el registro de pago y los movimientos de stock.
2. Al confirmar una venta, se descuenta el stock de cada producto confirmado.
3. Al completar una compra, se suman las cantidades recibidas al stock de los productos.
4. Al anular una compra completa, se descuentan del stock las cantidades entregadas.
5. Al anular una venta, se devuelve al stock la cantidad registrada en sus ítems de producto.
6. Cuando `cantidad_actual < cantidad_minima`, el producto aparece como alerta de stock bajo.
7. Al guardar tipos nuevos o reactivados, se reutiliza el catálogo compartido de productos y servicios.

## Cálculos

1. El subtotal de una venta se calcula como suma de `precio_unitario * cantidad` de sus ítems.
2. El descuento de venta es un importe fijo en moneda, no un porcentaje.
3. El total de venta se calcula como `subtotal - descuento`.
4. El IVA no se suma al total confirmado: el campo `iva` se persiste como `21`, pero el importe guardado usa los precios vigentes sin recálculo tributario.
5. Las unidades vendidas corresponden a la suma de cantidades de productos y servicios.
6. El total de una compra corresponde a la suma de cantidades pedidas al crearla.
7. La deuda mostrada para clientes no es una cuenta corriente administrada por el sistema: se calcula como suma de montos de pagos asociados a ventas activas no pagadas.

## Estados

| Campo | Entidad | Significado |
|---|---|---|
| `activo` | Cliente, proveedor, empleado, producto, servicio y tipo | Indica si el registro está disponible; no representa el estado de pago o recepción. |
| `activo` | Compra | Indica si la compra está activa o anulada. |
| `completo` | Compra | Indica si se cerró la recepción. |
| `activa` | Venta | Indica si la venta está activa o anulada. |
| `estado` | Venta | Indica si la venta está pagada (`1`) o pendiente (`0`). |

## Diferencias respecto de supuestos iniciales

1. No existe margen automático del 30 % sobre el precio del proveedor. El precio se guarda y modifica desde el catálogo de productos.
2. Sí existen descuentos en ventas; son importes fijos validados contra el subtotal.
3. No se implementó una forma de pago propia en la cabecera de compra. El proveedor seleccionado es obligatorio, pero el registro de compra no guarda una forma de pago.
4. No existe eliminación física de proveedores, clientes, productos o ventas. Los módulos usan baja lógica.
5. No existe alta automática de una cuenta corriente con plazo máximo de cuatro meses; el esquema permite registros de pago e historial asociado a ventas, pero no contiene esa regla automatizada.
6. No se genera una factura correlativa ni numeración de comprobantes; el flujo actual utiliza identificadores internos y valores constantes o datos existentes.
7. No existe una clase o tabla específica de “historial de precios” en el esquema actual.
