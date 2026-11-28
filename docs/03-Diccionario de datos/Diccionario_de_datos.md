# Diccionario de datos

Este diccionario describe las entidades reales del modelo y los principales datos que se utilizan en el sistema. Es una síntesis del esquema SQL versionado y de las guías técnicas de los módulos. Ante diferencias con una base desplegada, prevalece el modelo ejecutado y debe actualizarse el SQL o este documento.

## Convenciones

- Los identificadores principales son enteros autoincrementales, salvo las tablas indicadas.
- `1` representa activo, disponible o verdadero y `0` representa inactivo o falso, salvo que el campo tenga una interpretación específica.
- Los nombres y valores mostrados por la interfaz deben considerarse datos persistidos en MySQL.
- Las claves foráneas, índices únicos y cardinalidades que se indican corresponden al SQL versionado.

## Entidades principales

| Entidad | Tabla | Descripción |
|---|---|---|
| Cliente | `cliente` | Persona o entidad que participa en ventas y, opcionalmente, pagos. |
| Empleado | `empleado` | Cuenta de acceso y usuario que registra operaciones. |
| Proveedor | `proveedor` | Empresa o persona que abastece productos mediante compras. |
| Tipo | `tipos` | Clasificación compartida por productos y servicios. |
| Producto | `producto` | Artículo comercializable con stock, precio y datos de catálogo. |
| Servicio | `servicio` | Servicio comercializable sin inventario propio. |
| Compra | `compra` | Cabecera de una orden de compra. |
| Ítem de compra | `item_compra` | Producto y cantidades pedida/entregada dentro de una compra. |
| Venta | `venta` | Cabecera de una operación de venta. |
| Ítem de venta | `item_venta` | Producto o servicio vendido dentro de una venta. |
| Método de pago | `metodos_pago` | Catálogo de formas de pago disponibles. |
| Pago de cliente | `historial_pago_cliente` | Registro asociado a una venta, importe y vencimiento. |

## Tablas y atributos

### Cliente

| Campo | Tipo SQL | Nulo | Uso |
|---|---|---:|---|
| `idcliente` | `int` | No | Identificador principal autoincremental. |
| `nombre` | `varchar(45)` | No | Nombre del cliente. |
| `apellido` | `varchar(45)` | Sí | Apellido. |
| `cuit` | `varchar(45)` | Sí | CUIT/DNI; definido como único. |
| `direccion` | `varchar(45)` | Sí | Dirección. |
| `numero_tel` / `telefono` | `varchar(45)` | Sí | Teléfono de contacto. |
| `mail` | `varchar(45)` | Sí | Correo electrónico. |
| `ciudad` | `varchar(45)` | Sí | Ciudad usada por filtros. |
| `activo` | `tinyint` | Sí | Baja lógica. |

### Empleado

| Campo | Tipo SQL | Nulo | Uso |
|---|---|---:|---|
| `idempleado` | `int` | No | Identificador principal autoincremental. |
| `nombre_usuario` | `varchar(45)` | No | Nombre único usado para iniciar sesión. |
| `mail` | `varchar(45)` | Sí | Correo asociado a la cuenta. |
| `contrasena` | `varchar(255)` | No | Hash de contraseña, no texto plano. |
| `tipo` | `varchar(45)` | No | Rol: `AD`, `DEV`, `EM`, `Empleado` u otro valor usado históricamente. |
| `activo` | `tinyint` | No | Estado de la cuenta. |
| `telefono` | `varchar(45)` | Sí | Canal opcional de recuperación. |
| `token_recuperacion` | `varchar(10)` | Sí | Código temporal de recuperación. |
| `token_expiracion` | `datetime` | Sí | Fecha y hora de vencimiento del código. |

### Proveedor

| Campo | Tipo SQL | Nulo | Uso |
|---|---|---:|---|
| `idproveedor` | `int` | No | Identificador principal autoincremental. |
| `nombre` | `varchar(45)` | No | Nombre o razón social. |
| `cuit` | `varchar(20)` | Sí | Identificación única. Se maneja como texto. |
| `direccion` | `varchar(45)` | Sí | Dirección. |
| `mail` | `varchar(45)` | Sí | Correo electrónico. |
| `ciudad` | `varchar(45)` | Sí | Ciudad usada por filtros. |
| `telefono` | `varchar(45)` | Sí | Teléfono. |
| `rubro` | `varchar(75)` | Sí | Rubro o categoría del proveedor. |
| `activo` | `tinyint` | Sí | Baja lógica. |

### Tipo, producto y servicio

| Campo | Entidad | Tipo SQL | Uso |
|---|---|---|---|
| `idtipo` | Tipo | `int` | Identificador principal. |
| `tipo` / `nombre` | Tipo | `varchar(45)` | Nombre único del tipo. |
| `activo` | Tipo | `tinyint` | Estado del catálogo. |
| `idproducto` | Producto | `int` | Identificador principal. |
| `nombre` | Producto | `varchar(45)` | Nombre del producto. |
| `idtipo` | Producto | `int` | Tipo clasificador; clave foránea. |
| `marca` | Producto | `varchar(45)` | Marca opcional. |
| `medidas` | Producto | `varchar(45)` | Medida opcional. |
| `unidad_medida` | Producto | `varchar(45)` | Unidad presentada por la interfaz. |
| `imagen_url` | Producto | `text` | URL entregada por Cloudinary. |
| `precio` | Producto | `decimal(10,2)` | Precio actual de venta. |
| `cantidad_actual` | Producto | `int` | Stock disponible. |
| `cantidad_minima` | Producto | `int` | Umbral de alerta. |
| `activo` | Producto | `tinyint` | Baja lógica. |
| `idservicio` | Servicio | `int` | Identificador principal. |
| `nombre` | Servicio | `varchar(45)` | Nombre único del servicio. |
| `idtipo` | Servicio | `int` | Tipo clasificador; clave foránea. |
| `precio` | Servicio | `decimal(10,2)` | Precio actual. |
| `activo` | Servicio | `tinyint` | Baja lógica. |

### Compra e ítem de compra

| Campo | Tabla | Tipo / uso |
|---|---|---|
| `idcompra` | `compra` | Identificador principal autoincremental. |
| `fecha` | `compra` | Fecha de registro. |
| `horas` | `compra` | Hora de registro. |
| `cantidad_total` | `compra` | Suma de cantidades pedidas. |
| `idproveedor` | `compra` | Proveedor relacionado; clave foránea. |
| `activo` | `compra` | `1` activa, `0` anulada. |
| `completo` | `compra` | `1` recepción cerrada, `0` recepción pendiente. |
| `iditem_compra` | `item_compra` | Identificador principal del ítem. |
| `idcompra` | `item_compra` | Compra asociada. Índice definido, pero sin clave foránea declarada en el SQL. |
| `idproducto` | `item_compra` | Producto relacionado; clave foránea. |
| `cantidad_pedida` | `item_compra` | Cantidad solicitada al proveedor. |
| `cantidad_entregada` | `item_compra` | Cantidad recibida al completar. |

### Venta e ítem de venta

| Campo | Tabla | Tipo / uso |
|---|---|---|
| `idventa` | `venta` | Identificador principal autoincremental. |
| `fecha` | `venta` | Fecha/hora de emisión según el SQL. |
| `descuento` | `venta` | Importe fijo restado al subtotal. |
| `iva` | `venta` | Campo persistido con valor `21` por el flujo actual, sin sumarlo al total. |
| `cantidad_total_productos` | `venta` | Cantidad total de unidades de productos y servicios. |
| `precio_total` | `venta` | Total vigente calculado por el servidor. |
| `idcliente` | `venta` | Cliente nullable y clave foránea. |
| `idempleado` | `venta` | Empleado obligatorio y clave foránea. |
| `activa` | `venta` | Baja lógica de la venta. |
| `estado` | `venta` | Estado de pago: `1` pagada y `0` pendiente. |
| `iditem_venta` | `item_venta` | Identificador principal del detalle. |
| `idventa` | `item_venta` | Venta asociada. Índice definido, sin clave foránea declarada en el SQL. |
| `idproducto` | `item_venta` | Producto vendido; nullable. |
| `idservicio` | `item_venta` | Servicio vendido; nullable. |
| `cantidad` | `item_venta` | Cantidades vendidas. |
| `precio_unitario` | `item_venta` | Precio vigente al confirmar la venta. |

### Método de pago y pago

| Campo | Tabla | Tipo / uso |
|---|---|---|
| `idmetodos_pago` | `metodos_pago` | Identificador principal. |
| `nombre` | `metodos_pago` | Nombre del método. |
| `activo` | `metodos_pago` | Método disponible si está activo. |
| `idhistorial_pago_cliente` | `historial_pago_cliente` | Identificador principal autoincremental. |
| `idventa` | `historial_pago_cliente` | Venta relacionada; clave foránea. |
| `idmetodos_pago` | `historial_pago_cliente` | Método relacionado; clave foránea. |
| `monto` | `historial_pago_cliente` | Importe registrado. |
| `fecha`, `hora` | `historial_pago_cliente` | Momento del pago o vencimiento. |
| `fecha_vencimiento` | `historial_pago_cliente` | Fecha del comprobante de cuenta corriente; tiene índice único en el esquema. |
| `plazo_dias` | `historial_pago_cliente` | Plazo usado por el registro; las ventas actuales usan `0`. |

## Relaciones y restricciones

- Un proveedor puede abastecer muchas compras; una compra pertenece a un proveedor.
- Un tipo clasifica muchos productos y servicios.
- Una compra contiene muchos `item_compra`; cada línea corresponde a un producto.
- Una venta puede pertenecer a un cliente opcional y siempre pertenece a un empleado.
- Una venta contiene muchos `item_venta`; cada línea apunta a un producto o a un servicio.
- Una venta puede tener registros en `historial_pago_cliente`; un método de pago puede utilizarse en muchos registros.
- `item_compra.idcompra` e `item_venta.idventa` son relaciones lógicas indexadas, pero no tienen clave foránea declarada en el dump actual.
- `historial_pago_cliente.fecha_vencimiento` tiene restricción única. El sistema no permite repetir una fecha no nula en esa tabla.
- Las restricciones únicas evitan nombres/tipos repetidos y combinaciones duplicadas de productos o servicios según el módulo.
- Las bajas son lógicas en los catálogos y operaciones principales; no deben confundirse con eliminación física.
