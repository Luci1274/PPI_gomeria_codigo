# Documentación técnica del inventario

## Descripción general

La pantalla de inventario administra productos e insumos y servicios desde una tabla común. Los productos tienen stock, marca, medidas y una imagen opcional; los servicios tienen nombre, tipo y precio, sin stock. Ambos usan registros de `tipos`.

Archivos principales:

- `src/modulos/inventario_rutas.py`: vistas y API.
- `src/modulos/comandos_db/comandos_db_productos.py`: consultas y operaciones sobre productos, servicios y tipos.
- `src/templates/inventario.html` y `src/static/js/inventario.js`: tabla, filtros y formularios.
- `src/templates/orden_venta.html` y `src/static/js/realizar_venta.js`: catálogo de ventas y retorno al inventario.
- `docs/estructura_y_datos_DB_27_11_2026.sql`: esquema de referencia de las tablas.

## Modelo y reglas de datos

- `producto` almacena nombre, tipo, marca, medidas, URL de imagen, estado, cantidad actual, cantidad mínima y precio.
- `servicio` almacena nombre, tipo, estado y precio. No mantiene existencias.
- `tipos` clasifica ambos. Al guardar un artículo, el sistema normaliza el nombre del tipo, reutiliza el registro existente o lo crea; si estaba inactivo, lo reactiva. No hay una pantalla para administrar tipos por separado.
- Los productos se consideran duplicados cuando coinciden nombre, tipo, marca y medidas; los servicios, cuando coincide el nombre. La base también impone restricciones de unicidad.
- Desactivar es una baja lógica (`activo = 0`); reactivar vuelve a establecer `activo = 1`. No se borran físicamente filas.

La consulta combina productos y servicios en una sola lista. El campo `tipo_item` (`producto` o `servicio`) distingue sus tablas porque los identificadores pueden coincidir. La API expone el identificador común como `idproducto_servicio`.

## Pantalla y filtros

La tabla muestra hasta 10 resultados por página, ordenados por nombre y luego por `tipo_item`. La métrica “Artículos encontrados” cuenta los resultados que cumplen los filtros, no un total global sin filtrar.

Filtros disponibles:

- Búsqueda parcial por nombre.
- Tipo, entre los tipos activos.
- Marca, entre las marcas no vacías registradas para productos (incluye marcas presentes solo en productos inactivos).
- Estado: activo, inactivo o todos. La pantalla inicia mostrando activos.
- Stock: todos o bajo. “Stock bajo” incluye únicamente productos activos o inactivos con `cantidad_actual < cantidad_minima`; no incluye servicios. Si la cantidad mínima es `NULL`, el artículo no coincide.

Al cambiar un filtro o buscar, la interfaz vuelve a la primera página. Los tipos y las marcas se actualizan con los datos del inventario, por lo que también aparecen las nuevas marcas al guardar artículos.

## Alta y modificación

Los formularios permiten elegir un tipo existente o escribir uno nuevo. Si se completan ambos, el texto escrito tiene prioridad.

- Producto: nombre y tipo obligatorios (máximo 45 caracteres); cantidad actual y precio deben ser valores válidos no negativos. La cantidad mínima es opcional al crear y no negativa cuando se informa; marca, medidas e imagen son opcionales.
- Servicio: nombre, tipo y precio obligatorios; nombre y tipo admiten hasta 45 caracteres y el precio debe ser finito y no negativo.
- La imagen de producto se envía a Cloudinary, donde se transforma a 600 × 600. Si se modifica el producto sin adjuntar una nueva imagen, se conserva la existente.
- La interfaz informa duplicados al crear. En productos y servicios inactivos se oculta la acción de edición y se ofrece reactivarlos.

## Rutas

Todas las rutas pertenecen a `inventario_bp`.

| Método y ruta | Función | Descripción |
|---|---|---|
| `GET /inventario` | `vista_gestion_inventario` | Renderiza la pantalla. `?volver=venta` muestra el botón para volver a la orden de venta. |
| `POST /api/inventario` | `api_inventario` | Lista y pagina resultados; recibe `pagina`, `buscar`, `tipo`, `marca`, `estado` y `stock` como parámetros de consulta. `stock` acepta `todos` o `bajo`. |
| `POST /api/inventario/crear` | `api_crear_producto` | Crea un producto, con imagen opcional. |
| `POST /api/inventario/servicios` | `api_crear_servicio` | Crea un servicio. |
| `GET /inventario/<id>/modificar` | `api_obtener_producto` | Obtiene producto o servicio según `tipo_item`. |
| `POST /api/inventario/<id>/modificar` | `api_modificar_producto` | Modifica el elemento según `tipo_item`. |
| `GET /api/inventario/<id>/desactivar` | `desactivar_producto` | Desactiva lógicamente el elemento según `tipo_item`. |
| `POST /api/inventario/<id>/activar` | `activar_producto` | Reactiva el elemento según `tipo_item`. |

En las rutas de obtener, modificar, desactivar y activar, `tipo_item` acepta `producto` o `servicio` y, si se omite, se asume `producto`. La ruta de listado usa POST aunque los filtros viajan en la query string.

Respuestas principales:

- Listado: `200`; filtro `stock` inválido: `400`; error de consulta: `500`.
- Altas: `201`; datos inválidos o error de carga de imagen: `400`; duplicado: `409`; falla de persistencia: `500`.
- Obtener: `200`; `tipo_item` inválido: `400`; artículo inexistente: `404`; falla de consulta: `500`.
- Modificar: `200` al guardar, `400` ante datos inválidos o error de carga de imagen, y `500` si falla la persistencia.
- Desactivar y reactivar: `200` si se actualiza el estado; `400` si no se pudo completar o el tipo es inválido.

## Acceso y relación con ventas

La protección global de `app.py` restringe la gestión del inventario a los roles `AD` y `DEV`. Los roles `EM` y `EMPLEADO` no tienen esos endpoints en su lista permitida. Sin sesión, las páginas redirigen al inicio de sesión y las APIs responden `401`; sin permiso, las APIs responden `403` y las páginas redirigen a `/`.

Al abrir Inventario desde una orden de venta con `?volver=venta`, la pantalla ofrece volver a la orden. El flujo de ventas conserva el carrito y el descuento en `localStorage` durante esa navegación. Los servicios vendidos no descuentan stock; las compras de mercadería siguen limitadas a productos.
