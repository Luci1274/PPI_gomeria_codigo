# Documentación técnica del inventario

## Descripción general

La pantalla de inventario reúne productos y servicios en una tabla, aunque se almacenan en tablas distintas. Los productos administran stock, marca, medidas e imagen; los servicios tienen nombre, tipo y precio, sin stock. Ambos se clasifican mediante `tipos`.

Archivos principales:

- `src/modulos/inventario_rutas.py`: vistas y API de inventario.
- `src/modulos/comandos_db/comandos_db_productos.py`: consultas y operaciones de productos, servicios y tipos.
- `src/templates/inventario.html` y `src/static/js/inventario.js`: pantalla, formularios y filtros.
- `src/templates/orden_venta.html` y `src/static/js/realizar_venta.js`: catálogo y carrito de ventas.

## Tipos

Los tipos se crean al registrar un producto o servicio si todavía no existen. El formulario permite seleccionar un tipo existente o escribir uno nuevo. Si el tipo ya existe pero está inactivo, registrarlo nuevamente lo reactiva. La interfaz no incluye una pantalla para administrar o desactivar tipos.

## Inventario

La tabla combina los registros de `producto` y `servicio`; cada fila incluye `tipo_item` (`producto` o `servicio`) para distinguirlos, ya que los identificadores de ambas tablas pueden coincidir. Se pueden filtrar por nombre, tipo, marca y estado. Los servicios muestran que el stock no aplica.

Los productos se desactivan lógicamente en `producto`; los servicios, en `servicio`. La operación se selecciona usando `tipo_item`, evitando modificar un registro homónimo de la otra tabla.

## Rutas

Todas las rutas pertenecen a `inventario_bp`.

| Método y ruta | Función | Descripción |
|---|---|---|
| `GET /inventario` | `vista_gestion_inventario` | Renderiza la tabla y los formularios. El parámetro `volver=venta` activa el retorno a la orden. |
| `POST /api/inventario` | `api_inventario` | Devuelve la página solicitada, los tipos activos y las marcas de productos. Acepta `pagina`, `buscar`, `tipo`, `marca` y `estado` en la query string. |
| `POST /api/inventario/crear` | `api_crear_producto` | Valida y registra un producto; responde `201`, `400`, `409` ante duplicado o `500` si falla la persistencia. |
| `POST /api/inventario/servicios` | `api_crear_servicio` | Valida y registra un servicio; responde `201`, `400`, `409` ante duplicado o `500` si falla la persistencia. |
| `GET /inventario/<id>/modificar` | `api_obtener_producto` | Devuelve los datos del producto o servicio indicado por `tipo_item`. |
| `POST /api/inventario/<id>/modificar` | `api_modificar_producto` | Actualiza el elemento seleccionado por `tipo_item`. |
| `GET /api/inventario/<id>/desactivar` | `desactivar_producto` | Desactiva lógicamente el elemento indicado por `tipo_item`. |

En los endpoints de edición y desactivación, `tipo_item` admite `producto` o `servicio` y por defecto vale `producto`. La ruta de listado usa POST aunque sus filtros se envían como parámetros de consulta.

## Ventas y navegación al inventario

El catálogo de ventas reúne productos y servicios, usando el identificador y `tipo_item` de cada artículo. El carrito guarda ambos valores, por lo que dos registros con el mismo ID pero de distinta tabla no se confunden. Al navegar desde una orden a Inventario para registrar un servicio, la orden guarda el carrito y el descuento aplicado en `localStorage`; al volver, recarga el catálogo y restaura ambos.

Los empleados no ven el acceso directo a Inventario desde la orden de venta; la plantilla muestra ese botón solo a los roles `AD` y `DEV`. El acceso a las vistas de inventario también depende de la protección de rutas configurada en la aplicación.

Los servicios no afectan stock en las ventas. La compra de mercadería continúa limitada a productos.
