# Documentación general del sistema y la base de datos

## Alcance y archivos principales

La aplicación es un sistema web Flask para gestionar ventas, compras, inventario, clientes, proveedores y empleados. La aplicación principal registra las rutas, aplica el control global de sesiones y sirve el inicio y el dashboard.

| Componente | Archivo | Responsabilidad |
|---|---|---|
| Aplicación y autorización | [`src/app.py`](../../src/app.py) | Inicializa Flask, protege rutas y registra las páginas y blueprints. |
| Configuración | [`src/config.py`](../../src/config.py) | Carga variables de entorno, configura la clave de sesión y el pool de base de datos. |
| Inicio y dashboard | [`src/templates/pantalla_principal.html`](../../src/templates/pantalla_principal.html), [`src/static/js/pantalla_principal.js`](../../src/static/js/pantalla_principal.js) | Presenta métricas, actividad reciente y alertas de stock. |
| Consultas del dashboard | [`src/modulos/comandos_db/comandos_db_pantalla_inicial.py`](../../src/modulos/comandos_db/comandos_db_pantalla_inicial.py) | Ejecuta las consultas que alimentan el dashboard. |
| Acceso y registro | [`src/modulos/empleados_rutas.py`](../../src/modulos/empleados_rutas.py), [`src/templates/iniciar_sesion.html`](../../src/templates/iniciar_sesion.html), [`src/static/js/login.js`](../../src/static/js/login.js) | Presenta el acceso, registro y recuperación de contraseña. |
| Esquema de referencia | [`docs/estructura_y_datos_DB_27_11_2026.sql`](../estructura_y_datos_DB_27_11_2026.sql) | Contiene el DDL y datos de ejemplo del modelo relacional. |

Cada módulo de negocio tiene su propia guía en esta carpeta; ver [empleados](./empleado.md), [ventas](./venta.md), [compras](./compra.md), [inventario](./inventario.md), [clientes](./clientes.md) y [proveedores](./proveedores.md).

## Aplicación Flask y control de acceso

`app.py` crea la instancia Flask, carga la clase `Config`, instala `proteger_rutas` como `before_request` y registra los blueprints de ventas, empleados, proveedores, inventario, clientes y compras.

### Regla general de autorización

Antes de ejecutar una ruta, `proteger_rutas`:

1. Deja continuar archivos estáticos y solicitudes sin endpoint resuelto.
2. Permite los endpoints o las rutas incluidas en `RUTAS_PUBLICAS`.
3. Si no existe `id_usuario` en la sesión, redirige las páginas a `/iniciar_sesion` y responde `401` JSON a las solicitudes reconocidas como API.
4. Con sesión, permite todas las rutas a los tipos `AD` y `DEV`.
5. Permite a `EM` y `EMPLEADO` solo los endpoints enumerados en `ENDPOINTS_EMPLEADO`: inicio y dashboard, las rutas habilitadas de ventas y cierre de sesión.
6. Para una sesión válida sin permiso, responde `403` JSON a una API y redirige una página a `/`.

El acceso a `/` y `/api/datos-dashboard` está permitido a cualquier sesión válida, antes de comprobar el rol. La gestión de empleados, clientes, proveedores, inventario y compras no está habilitada para empleados por la lista actual. Los archivos estáticos se sirven sin pasar por esta comprobación.

`ENDPOINTS_JSON` identifica además rutas de detalle que devuelven JSON aunque su URL no comience con `/api/`. La detección general de API también reconoce URLs `/api/...` y endpoints cuyo nombre comienza con `api_`.

Los nombres de rol que realmente autoriza `app.py` están codificados en la regla anterior. Aunque `Config` carga una variable `ROLES`, `app.py` no la consulta para decidir permisos; modificarla no cambia por sí solo esta política.

La aplicación ejecuta `app.run(debug=True)` cuando se inicia directamente como programa. Ese modo es de desarrollo; no debe exponerse como servidor de producción.

## Inicio y dashboard

`GET /` renderiza `pantalla_principal.html` y pasa a la plantilla el nombre de usuario guardado en sesión. La navegación lateral y los accesos rápidos cambian según el tipo de usuario:

- `AD` y `DEV` ven ventas, compras, inventario, clientes, proveedores y empleados, además de accesos rápidos para las operaciones principales.
- `EM` y `EMPLEADO` ven el inicio, ventas y cierre de sesión; el acceso rápido se limita a crear una venta.

La página muestra la fecha local del navegador, tres métricas, las últimas ventas y productos con stock bajo. `pantalla_principal.js` solicita los datos inicialmente y vuelve a consultar cada 10 segundos.

### `GET /api/datos-dashboard`

La ruta usa las consultas de `comandos_db_pantalla_inicial.py` y devuelve:

| Campo | Contenido |
|---|---|
| `total_productos` | Cantidad de filas de productos activos; no es la suma de unidades en inventario. |
| `total_clientes` | Cantidad de clientes activos. |
| `ventas_dia` | Cantidad de ventas activas emitidas hoy; no es el importe vendido. |
| `ultimas_ventas` | Hasta cinco ventas activas de hoy, ordenadas de más reciente a más antigua, con cliente, total, forma de pago y estado de pago. |
| `productos_bajos` | Productos activos cuya `cantidad_actual` es menor que `cantidad_minima`. |

La API responde `200` con `exito: true` y esos campos cuando las consultas terminan correctamente. Ante un error de base de datos responde `500` con `exito: false` y un mensaje; el JavaScript muestra el aviso de error. Una falla de red también produce un aviso. Sin resultados, el dashboard muestra mensajes de tabla vacía.

El acceso a reponer stock desde las alertas solo se presenta a `AD` y `DEV`. La consulta de ventas del día incluye ventas activas con independencia del valor de `venta.estado`; ese campo representa si la venta está pagada, no si fue anulada.

## Inicio de sesión, registro y cierre

La pantalla de `GET /iniciar_sesion` y su alias `GET /registrarse` es la misma plantilla; JavaScript cambia entre las pestañas de acceso y registro. El formulario envía las operaciones a las API, no a la ruta declarada en el atributo `action` del formulario.

| Método y ruta | Función |
|---|---|
| `GET /iniciar_sesion` | Muestra la pantalla de acceso, registro y recuperación. |
| `GET /registrarse` | Alias de la pantalla anterior. |
| `POST /api/iniciar_sesion` | Comprueba las credenciales de una cuenta activa. |
| `POST /api/registrarse` | Crea una cuenta nueva con rol `Empleado`. |
| `POST /api/recuperar/solicitar` | Solicita un código temporal de recuperación. |
| `POST /api/recuperar/validar_token` | Comprueba el código. |
| `POST /api/recuperar/restablecer` | Guarda el nuevo hash de contraseña. |
| `GET /cerrar_sesion` | Limpia la sesión y redirige a la pantalla de acceso. |

El inicio de sesión acepta JSON o formulario. Recibe `txt_input_nombre`, `password_input` y `checkbox_recordar`. `Usuario.verificar_credenciales` busca el nombre de usuario activo y verifica la contraseña mediante Werkzeug. Si coincide, la ruta guarda `id_usuario`, `nombre_usuario` y `tipo` en la sesión y devuelve `200` con redirección a `/`; credenciales incorrectas devuelven `401` y un error de base de datos devuelve `500`.

La sesión de Flask se firma con `SECRET_KEY`. La opción «Recordar» activa `session.permanent`; no se define una duración propia de sesión permanente en `Config`, por lo que queda a cargo del valor predeterminado de Flask.

El registro es público y crea una cuenta de tipo `Empleado`; exige nombre de usuario y contraseña no vacíos. El nombre se comprueba antes de insertar, y la tabla también lo impone como único. El navegador compara la confirmación de contraseña y usa `intl-tel-input` para enviar el teléfono con código internacional cuando está disponible. Las cuentas nuevas no reciben permisos administrativos.

La pantalla de recuperación tiene tres pasos —solicitud, validación y cambio—. Sus detalles, códigos HTTP y comportamiento de correo/SMS se describen en [la documentación de empleados](./empleado.md).

## Configuración y variables de entorno

`config.py` carga el archivo `.env` ubicado junto a ese módulo (en esta estructura, `src/.env`) con `python-dotenv`. La documentación enumera nombres y propósitos, no valores secretos; no se deben versionar credenciales reales.

| Variable | Uso | Comportamiento |
|---|---|---|
| `DB_HOST` | Host de MySQL. | Sin valor predeterminado en el código. |
| `DB_USER` | Usuario de MySQL. | Sin valor predeterminado en el código. |
| `DB_PASSWORD` | Contraseña de MySQL. | Sin valor predeterminado en el código. |
| `DB_NAME` | Nombre de la base de datos. | Sin valor predeterminado en el código. |
| `DB_PORT` | Puerto de MySQL. | Predeterminado `3306`; se convierte a entero al importar `config.py`. |
| `CLAVE_SECRETA` | Clave de firma de sesión de Flask. | Tiene un fallback de desarrollo débil; se debe configurar una clave aleatoria y privada en cada entorno desplegado. |
| `RUTAS_PUBLICAS` | Lista separada por comas de rutas/endpoints públicos. | Si se define, reemplaza la lista predeterminada completa; debe incluir las rutas públicas necesarias. |
| `ROLES` | Lista separada por comas de roles. | Se carga con un valor predeterminado, pero no es utilizada por la guardia de permisos actual. |
| `TU_CLOUD_NAME`, `TU_API_KEY`, `TU_API_SECRET` | Credenciales para configurar Cloudinary. | Se leen cuando se invoca `Config.conectar_cloudinary()`. |
| `TWILIO_SID`, `TWILIO_TOKEN`, `TWILIO_WHATSAPP_NUMBER` | Credenciales y número remitente para Twilio. | Se leen al solicitar las credenciales de Twilio. |
| `GMAIL_USER`, `GMAIL_PASS` | Cuenta y contraseña de Gmail para notificaciones por correo. | Se leen al solicitar las credenciales de Gmail. |

El pool se crea al importar `config.py` con `PooledDB`: `mincached=2`, `maxconnections=10` y `blocking=True`. Las conexiones usan PyMySQL y cursores `DictCursor`, por lo que los resultados se consumen como diccionarios. `Config.conectar_db()` entrega una conexión del pool. Las funciones de integración con Cloudinary, Twilio y Gmail obtienen sus credenciales desde el entorno.

No se deben imprimir ni agregar al repositorio valores de `.env`. Para desplegar, configurar como mínimo la conexión MySQL y una `CLAVE_SECRETA` segura; también configurar los servicios externos que se utilicen.

## Modelo de datos

El archivo [`estructura_y_datos_DB_27_11_2026.sql`](../estructura_y_datos_DB_27_11_2026.sql) define las tablas y contiene inserciones de ejemplo. Las tablas usan InnoDB y `utf8mb4`. Es un volcado de esquema y datos, no un archivo seguro para ejecutar indiscriminadamente: contiene `DROP TABLE IF EXISTS` antes de recrear tablas. Antes de usarlo, comprobar el entorno y contar con respaldo.

### Entidades

| Tabla | Propósito y campos representativos |
|---|---|
| `cliente` | Personas o entidades que compran: `idcliente`, nombre, apellido, CUIT, teléfono, correo, ciudad, dirección y `activo`. El CUIT es único. |
| `empleado` | Cuentas de acceso: `idempleado`, `nombre_usuario` único, correo, hash de `contrasena`, `tipo`, `activo`, teléfono y campos de recuperación `token_recuperacion`/`token_expiracion`. |
| `proveedor` | Proveedores: `idproveedor`, nombre, CUIT único, datos de contacto, rubro y `activo`. |
| `tipos` | Catálogo de tipos/clasificaciones con nombre único y estado. |
| `producto` | Artículos con tipo, marca, medidas, imagen, stock actual, mínimo, precio y estado. Tiene una restricción única compuesta por nombre, tipo, marca y medidas. |
| `servicio` | Servicios con nombre, tipo, precio y estado. El nombre tiene una restricción única. |
| `compra` | Orden de compra con fecha, hora, cantidad total, proveedor, `activo` y `completo`. `activo` indica si está anulada; `completo` indica si fue recibida. |
| `item_compra` | Detalle de compra: producto, compra, cantidad pedida y cantidad entregada. |
| `venta` | Cabecera de venta: fecha de emisión, descuento, IVA, cantidad total, precio total, cliente opcional, empleado, `activa` y `estado`. `activa` representa baja lógica; `estado` representa pago completo o pendiente. |
| `item_venta` | Detalle de venta con producto o servicio, precio unitario, cantidad y referencia lógica a la venta. |
| `metodos_pago` | Catálogo de métodos de pago con identificador, nombre y estado. |
| `historial_pago_cliente` | Datos de pago asociados a una venta y un método: fecha, hora, monto, comprobantes, vencimiento y plazo. |

### Relaciones

| Relación | Cardinalidad y claves |
|---|---|
| `proveedor` → `compra` | Un proveedor puede tener muchas compras. `compra.idproveedor` tiene clave foránea. |
| `tipos` → `producto` | Un tipo puede clasificar muchos productos; `producto.idtipo` tiene clave foránea. |
| `tipos` → `servicio` | Un tipo puede clasificar muchos servicios; `servicio.idtipo` tiene clave foránea. |
| `cliente` → `venta` | Un cliente puede tener muchas ventas; `venta.idcliente` es nullable y tiene clave foránea. |
| `empleado` → `venta` | Un empleado puede registrar muchas ventas; `venta.idempleado` tiene clave foránea y es obligatorio. |
| `venta` → `historial_pago_cliente` | Una venta puede tener registros de pago; `historial_pago_cliente.idventa` tiene clave foránea. |
| `metodos_pago` → `historial_pago_cliente` | Un método puede aparecer en muchos registros; `historial_pago_cliente.idmetodos_pago` tiene clave foránea. |
| `producto` → `item_compra` | Un producto puede aparecer en muchos detalles; `item_compra.idproducto` tiene clave foránea. |
| `producto` / `servicio` → `item_venta` | Los detalles pueden referenciar productos o servicios mediante sus claves foráneas respectivas. Las dos columnas permiten `NULL`. |
| `compra` → `item_compra` | Relación lógica mediante `item_compra.idcompra`; el esquema define un índice, pero no una clave foránea. |
| `venta` → `item_venta` | Relación lógica mediante `item_venta.idventa`; el esquema define un índice, pero no una clave foránea. |

Las relaciones de compra-producto y venta-producto/servicio se representan mediante tablas de detalle. En el esquema actual no hay una restricción `CHECK` que exija exactamente una de las columnas `idproducto` o `idservicio` en `item_venta`.

### Restricciones y observaciones del esquema

- Las claves primarias identifican cada entidad; salvo `metodos_pago`, los identificadores principales son autoincrementales.
- Además de las restricciones únicas mencionadas, `historial_pago_cliente.fecha_vencimiento` tiene un índice `UNIQUE`; por tanto, el esquema no permite repetir una fecha de vencimiento no nula en esa tabla.
- Las tablas de detalle tienen índices para sus identificadores relacionados. Los índices por sí solos no garantizan la existencia de la fila padre; en particular, `item_compra.idcompra` y `item_venta.idventa` no tienen clave foránea declarada en este dump.
- Los campos de estado (`activo`, `activa`, `completo`, `estado`) representan conceptos distintos según la tabla; no deben interpretarse como una única bandera global.
- La baja lógica conserva filas e historial. El esquema no declara reglas `ON DELETE CASCADE` para las relaciones listadas.
- Este SQL es la referencia versionada del proyecto; cualquier diferencia con una base ya desplegada debe comprobarse contra esa base antes de ejecutar cambios.
