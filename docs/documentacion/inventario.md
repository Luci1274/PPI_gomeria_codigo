# Documentación del módulo de inventario

## Objetivo y alcance

El módulo permite consultar el catálogo de productos y servicios, buscar y filtrar registros, crear artículos, modificar sus datos y desactivarlos. También muestra precio de venta y stock actual.

Cada artículo tiene un ID propio (`idproducto_servicio`). Las ventas y compras se refieren a ese ID para registrar ítems y ajustar stock; crear una venta o compra no crea filas nuevas en el catálogo.

## Archivos involucrados

| Archivo | Responsabilidad |
|---|---|
| `src/modulos/inventario_rutas.py` | Rutas Flask y recepción de formularios. |
| `src/modulos/comandos_db/comandos_db_productos.py` | Consultas y operaciones de la clase `Producto`. |
| `src/templates/inventario.html` | Vista de listado y modales de alta y modificación; extiende `plantailla_gestion.html`. |
| `src/static/js/inventario.js` | Carga y renderizado, filtros, paginación y acciones de formulario. |
| `src/modulos/api_claudinary.py` | Subida de imágenes a Cloudinary, utilizada si se adjunta una imagen. |
| `src/static/css/gestion.css` | Estilos generales heredados de la plantilla de gestión. |

## Pantalla de inventario

La pantalla presenta:

- botón **Nuevo Producto**
- métrica **Total Productos**, correspondiente a los resultados del filtro actual
- búsqueda por nombre
- filtros por tipo, marca y estado (activo, inactivo o todos)
- tabla con código, nombre/medidas, tipo, marca, precio de venta, stock, estado y acciones
- navegación paginada
- modales para crear y modificar
- confirmación antes de desactivar

El listado utiliza 10 registros por página. La búsqueda espera 300 ms desde la última escritura; al cambiar un filtro o búsqueda se vuelve a la primera página.

La interfaz usa una API `POST` para consultar el listado, aunque los parámetros de búsqueda se envían en la URL. El formulario de alta y el de edición también usan `POST` con `multipart/form-data`, porque pueden incluir una imagen.

## Rutas

| Método y ruta | Función | Descripción |
|---|---|---|
| `GET /inventario` | `vista_gestion_inventario` | Renderiza `inventario.html`. |
| `POST /api/inventario` | `api_inventario` | Devuelve productos paginados y opciones de filtro. |
| `POST /api/inventario/crear` | `api_crear_producto` | Crea un producto o servicio; admite imagen opcional. |
| `GET /inventario/<id>/modificar` | `api_obtener_producto` | Obtiene un artículo por ID para completar el formulario de edición. |
| `POST /api/inventario/<id>/modificar` | `api_modificar_producto` | Actualiza los datos y, opcionalmente, la imagen. |
| `POST /api/inventario/<id>/desactivar` | `desactivar_producto` | Desactiva lógicamente el registro. |

## Listado: `POST /api/inventario`

### Parámetros de consulta

| Parámetro | Valor predeterminado en la ruta | Uso |
|---|---|---|
| `pagina` | `1` | Página solicitada. |
| `buscar` | `None` | Coincidencia parcial en el nombre. |
| `tipo` | `None` | Se aplica con `LIKE`; la interfaz envía el tipo seleccionado. |
| `marca` | `None` | Se aplica con `LIKE`; la interfaz envía la marca seleccionada. |
| `estado` | `None` | Filtra por `activo`: `1` activos, `0` inactivos, vacío para todos. |

La ruta fija el tamaño de página en 10. El método `Producto.leer_productos(...)` devuelve el total, los productos de la página, listas de tipos y marcas y el indicador de éxito.

### Respuesta de ejemplo

```json
{
  "exito": true,
  "productos": [
    {
      "idproducto_servicio": 12,
      "nombre": "Kit de reparación",
      "medidas": null,
      "tipo": "insumo",
      "precio": "8500.00",
      "cantidad_actual": 14
    }
  ],
  "tipos": [
    {"tipo": "insumo"}
  ],
  "marcas": [
    {"marca": "Genérica"}
  ],
  "pagina_actual": 1,
  "total_paginas": 2,
  "total_items": 15
}
```

La ruta calcula `total_paginas` con el total dividido por 10; con cero resultados devuelve cero páginas. Ante error de base de datos responde `500`, `exito: false`, el campo `Mensaje` y una redirección.

### Comportamiento observado del listado

- La búsqueda de texto solo consulta `nombre`, no marca, tipo ni medidas.
- La lista de valores distintos para tipo y marca no filtra por `activo`; puede ofrecer opciones que solo pertenecen a artículos inactivos.
- La consulta paginada selecciona `idproducto_servicio`, `nombre`, `medidas`, `tipo`, `precio` y `cantidad_actual`, pero no selecciona `marca` ni `activo`.
- A pesar de lo anterior, el JavaScript muestra marca y estado a partir de `prod.marca` y `prod.activo`. Como no están en la respuesta del listado, las marcas pueden mostrarse como `-` y los registros se interpretan como activos, incluidos los inactivos. El filtrado por estado sí se aplica en SQL, pero el indicador visual no puede distinguirlo con los datos actuales.
- El contador se calcula con `COUNT(idproducto_servicio)` y cuenta filas, no productos únicos por nombre o descripción.

## Crear un artículo

El modal permite cargar:

- nombre (obligatorio)
- tipo (obligatorio; texto libre)
- marca (opcional)
- medidas/especificaciones (opcional)
- cantidad actual (obligatoria en el navegador, mínimo 0)
- cantidad mínima (opcional en el navegador)
- precio de venta (obligatorio en el navegador, admite centavos)
- imagen (opcional; solo archivos de imagen en el control HTML)

El JavaScript envía los campos como `FormData` a `POST /api/inventario/crear`. Las cantidades se convierten a entero y el precio a decimal en el cliente; la ruta los lee con `request.form`. El tipo no se elige de una lista fija, por lo que el usuario puede escribir, por ejemplo, neumático, insumo, herramienta, repuesto o servicio.

### Imagen

Si se adjunta un archivo, la ruta llama a `subir_imagen(...)` y guarda la URL devuelta. Si Cloudinary no devuelve una URL, la API responde `400` y no intenta crear el artículo. Sin archivo, la URL se guarda como `NULL`.

### Control de duplicados

Antes del `INSERT`, `Producto.crear_producto(...)` busca otro registro con igual nombre, tipo, marca y medidas:

- compara nombre y tipo ignorando mayúsculas/minúsculas y espacios de los extremos
- convierte marca y medidas nulas a cadena vacía para comparar
- no filtra por `activo`; un producto inactivo con los mismos campos también impide crear otro igual

Si encuentra coincidencia, lanza `ProductoDuplicadoError`; la ruta responde `409` y un mensaje. La búsqueda previa no está respaldada por una restricción única de base de datos, por lo que no constituye una garantía ante dos altas simultáneas.

Respuesta exitosa (`201`):

```json
{
  "exito": true,
  "mensaje": "Producto guardado exitosamente"
}
```

La interfaz deshabilita el botón de guardar mientras se procesa el alta. Ante `409` muestra el aviso de duplicado; los errores de carga de imagen responden `400` y los de base de datos `500`.

## Modificar un artículo

Al abrir el modal, el navegador solicita `GET /inventario/<id>/modificar`. El método `Producto.leer_producto(id)` busca por ID sin filtrar por estado, por lo que puede obtenerse un artículo inactivo si se conoce su ID.

La respuesta contiene:

- `idproducto_servicio`
- nombre, tipo, marca y medidas
- cantidad actual y cantidad mínima
- precio

El formulario permite modificar esos campos y adjuntar una imagen nueva. `POST /api/inventario/<id>/modificar` actualiza la fila indicada por ID; el método no verifica que exista una fila afectada antes de devolver `True`.

Si no se adjunta un archivo nuevo, la ruta pasa `imagen_producto=None` al método de actualización y la consulta conserva la URL existente. Si se adjunta una imagen nueva, se sube a Cloudinary y la URL resultante reemplaza la anterior.

Respuesta exitosa (`200`):

```json
{
  "exito": true,
  "mensaje": "Producto modificado exitosamente"
}
```

Si la subida de una imagen nueva falla, responde `400`; si falla la actualización en MySQL, responde `500`.

## Desactivar un artículo

La acción **Eliminar** muestra una confirmación y llama a `POST /api/inventario/<id>/desactivar`. La operación es una baja lógica: `Producto.eliminar_producto(id)` actualiza `activo = 0`. Devuelve `True` solo cuando MySQL informa que se modificó una fila; un ID inexistente o ya inactivo se informa como operación fallida. La API responde `200` si tuvo éxito y `400` si no se pudo desactivar.

Los registros desactivados permanecen en la base de datos y sus referencias históricas en ventas y compras se conservan. La ruta usa `POST` para realizar el cambio de estado.

## Clase `Producto`: métodos de acceso a datos

### `Producto.crear_producto(...)`

Normaliza nombre, tipo, marca y medidas quitando espacios al principio y al final. Comprueba duplicados por esos cuatro campos y luego inserta la fila con `activo = 1`, stock, mínimo y precio. Devuelve `True` al crearla; ante error MySQL revierte la transacción y devuelve `None`. El duplicado se comunica mediante la excepción `ProductoDuplicadoError`, no como un valor de retorno.

### `Producto.leer_productos(pagina, por_pagina, buscar, tipo, marca, estado)`

Aplica los filtros opcionales, cuenta las filas que coinciden, devuelve una página ordenada por ID ascendente y además consulta tipos y marcas distintos. Retorna `(total_items, productos, tipos, marcas, exito)`.

El método inicia dos conexiones al comienzo de su ejecución, pero solo conserva y cierra explícitamente la segunda. La conexión inicial queda sin cierre explícito y debería revisarse.

### `Producto.leer_producto(id)`

Obtiene un registro por `idproducto_servicio`, sin excluir los inactivos. Retorna `(producto, True)` si la consulta tuvo éxito, incluso si no encontró una fila; ante error MySQL retorna una colección vacía y `False`.

### `Producto.actualizar_producto(id, ...)`

Reemplaza nombre, tipo, marca, medidas, URL de imagen, stock actual, mínimo y precio de la fila indicada por ID. No comprueba duplicados ni exige que el registro esté activo. Devuelve `True` si la consulta se ejecuta sin error, incluso si el ID no existe.

### `Producto.eliminar_producto(id)`

Desactiva lógicamente el producto con `activo = 0`. Devuelve `True` cuando MySQL informa que una fila cambió y `False` ante error o si no hubo filas afectadas.

### `Producto.alertar_stock_bajo()`

Consulta productos activos cuyo `cantidad_actual` es menor que `cantidad_minima`. Devuelve las filas encontradas; ante error MySQL registra el error y retorna una lista vacía.

## Relación con ventas y compras

El inventario se mantiene en `producto_servicio.cantidad_actual`:

| Operación | Tipos distintos de `servicio` | Tipo `servicio` |
|---|---|---|
| Completar recepción de compra | Suma la cantidad efectivamente recibida. | No modifica stock. |
| Anular compra completada | Resta la cantidad recibida. | No modifica stock. |
| Registrar venta | Resta la cantidad vendida. | No modifica stock. |
| Anular venta | Suma la cantidad vendida. | No modifica stock. |

El tipo es texto libre y las operaciones de stock de compras/ventas tratan como inventariables todos los tipos distintos de `servicio`. La validación de stock suficiente en ventas, sin embargo, actualmente solo cubre el tipo exacto `producto`; ver la documentación del módulo de ventas para ese detalle.

## Tablas principales

### `producto_servicio`

El módulo consulta y escribe principalmente:

- `idproducto_servicio`: identificador usado por compras y ventas
- `nombre`
- `tipo`
- `marca`
- `medidas`
- `imagen_producto`
- `activo`
- `cantidad_actual`
- `cantidad_minima`
- `precio`

La creación y desactivación lógica usan `activo`; la edición actualiza los datos del registro existente y no cambia su estado.

## Consideraciones y limitaciones

- Los tipos de artículo son texto libre; su escritura debe ser consistente, especialmente el valor reservado `servicio`, que se compara literalmente en las operaciones de stock.
- El alta previene duplicados con una búsqueda previa por nombre, tipo, marca y medidas, sin distinguir mayúsculas ni espacios exteriores. La edición no valida duplicados. No hay una restricción única de base de datos, así que el control no evita altas concurrentes ni inserciones hechas por otros clientes SQL.
- La respuesta del listado omite `marca` y `activo`, aunque la tabla intenta mostrarlos.
- Los selectores de marca y tipo se poblan con valores de registros activos e inactivos.
- El inventario permite editar manualmente `cantidad_actual`; no registra un historial de ajustes manuales en este módulo.
- Ante un error HTTP o de red al cargar el listado, la tabla muestra el error, la métrica se restablece a cero y la paginación vuelve a página 1 de 1 con sus botones actualizados.
- `Producto.leer_productos(...)` abre una sola conexión por consulta y la cierra en `finally`.

## Revisión de duplicados en operaciones relacionadas

Compras y ventas guardan ítems con el `idproducto_servicio` de un artículo existente; no insertan registros en `producto_servicio`. La protección contra dos productos de catálogo iguales solo está en el alta del inventario. No se detectaron índices únicos de negocio en el SQL versionado y la edición del producto tampoco busca colisiones.