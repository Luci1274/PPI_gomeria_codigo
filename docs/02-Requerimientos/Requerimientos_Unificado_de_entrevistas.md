# Requerimientos unificados:
## Compras:
1. Registrar compra.
2. Filtrar compras.
3. Visualizar listado de compra.
4. Registrar ítem de compra.
5. Modificar ítem de compra.
6. Eliminar ítem de compra.
7. Visualizar ítem de compra.
8. Dar de baja compra.
9. Listado histórico de compras (incluye bajas/estado).

## Ventas:
1. Registrar ventas.
2. Filtrar ventas.
3. Registrar ítem de venta.
4. Modificar ítem de venta.
5. Eliminar ítem de venta.
6. Emitir facturas digital.
7. Filtrar ganancias.
8. Dar de baja/anular venta (registrar motivo).
9. Visualizar listado de ventas (incluye anuladas).

## Cliente con antigüedad
1. Registrar cliente.
2. Modificar cliente.
3. Eliminar cliente.
4. Visualizar listado de clientes antiguos.

## Proveedor
1. Registrar proveedor.
2. Modificar proveedor.
3. Eliminar proveedor.
4. Visualizar listado de proveedores.
5. Visualizar listado de productos de un proveedor.

## Productos
1. Registrar productos.
2. Modificar productos.
3. Eliminar productos.
4. Filtrar productos.
5. Control de stock semanal.
6. Filtrar gastos de productos.
7. Visualizar historial de movimientos de stock (compras/ventas/bajas).

## Sistema
1. Mostrar formas de pago disponibles.
2. Calcular ganancias.
3. Visualizar listado general de productos.
4. Modificar porcentaje de precio según el tipo de venta.
5. Descontar automáticamente stock al vender.
6. Aumentar automáticamente stock al comprar.
7. Mostrar alerta de producto en falta.
8. Registrar bajas (compras/ventas) y mantener historial.

## Requerimientos Funcionales

### Venta
1. El sistema debe permitir registrar, modificar y eliminar ventas.
2. El sistema debe visualizar el listado de ventas.
3. El cliente debe poder filtrar ventas por fecha, cliente y estado.
4. El sistema debe permitir registrar, modificar y eliminar el ítem de venta.
5. El sistema debe calcular automáticamente el total de cada venta. 
6. El sistema debe emitir una factura digital tras la venta.
7. El sistema debe permitir exportar la factura en formato PDF. 
8. El sistema debe visualizar el listado de ganancias.
9. El usuario debe poder filtrar el listado de ganancias por dia, semana o mes. 
10. El sistema debe generar reportes de ganancias. 
11. El sistema debe permitir anular o dar de baja una venta (registrar motivo y usuario) y conservar el registro histórico.
12. El listado de ventas debe mostrar ventas activas y anuladas, con filtros por estado, fecha y motivo.
 
### Compra
1. El sistema debe permitir registrar, modificar y eliminar compras.
2. El sistema debe visualizar el listado de compras.
3. El usuario debe poder filtrar compras por fecha, proovedor y estado.
4. El sistema debe permitir registrar, modificar y eliminar el ítem de compras.
5. El sistema debe actualizar automáticamente el stock al confirmar la compra.
6. El sistema debe permitir dar de baja una compra (registrar motivo y usuario) 
7. El sistema debe mantener un historial de compras, incluyendo bajas.
8. El listado debe permitir filtrar por motivo, estado, usuario y fecha.

### Productos e insumos
1. El sistema debe permitir registrar, modificar y eliminar productos e insumos.
2. El sistema debe visualizar y filtrar el listado de productos.
3. El sistema debe actualizar automáticamente el stock según la compra y venta.
4. El sistema debe enviar una notificación cuando un producto alcanze un stock mínimo.
5. El usuairo debe recibir alertas de productos en falta.
6. El sistema debe mantener un historial de movimientos de stock (compra/venta/baja).

## Requerimientos no funcionales:

### Seguridad:
1. El sistema debe proteger los datos de acceso no autorizado. 
2. El sistema debe utilizar un protocolo de cifrado seguro para la transmisión de datos. 
3. El sistema debe autenticar a los usuarios antes de permitir el acceso a recursos sensibles. 
4. Auditoría: registrar quién y cuándo realiza bajas/anulaciones.

### Escalabilidad:
1. La base de datos debe ser capaz de manejar un volumen creciente de datos sin comprometer la velocidad de respuesta. 

### Usabilidad:
1. El sistema debe ser fácil de usar y navegar para los usuarios. 
2. La interfaz de usuario debe ser intuitiva y amigable. 
3. El sistema debe proporcionar ayudas y documentación para los usuarios. 

### Disponibilidad:
1. El sistema debe estar disponible el 99.9% del tiempo. 
2. El sistema debe poder recuperarse de fallos sin interrumpir el servicio a los usuarios. 
3. El tiempo de inactividad planificado debe ser mínimo. 

### Fiabilidad:
1. El sistema debe ser confiable y cumplir con los requisitos del usuario. 
2. El sistema debe poder manejar errores sin comprometer la integridad de los datos. 
3. El sistema debe ser capaz de recuperarse de errores sin perder datos. 

### Mantenibilidad:
1. El código del sistema debe ser fácil de entender y modificar. 
2. El sistema debe estar bien documentado. 
3. El sistema debe ser fácil de probar y depurar. 

### Compatibilidad:
1. El sistema debe ser compatible con otros sistemas y tecnologías. 
2. El sistema debe ser compatible con diferentes sistemas operativos. 

### Conformidad:
1. El sistema debe cumplir con las leyes y regulaciones aplicables. 
2. El sistema debe cumplir con los estándares de la industria.
