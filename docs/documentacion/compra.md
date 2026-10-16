# Documentación técnica del módulo de compras

## Descripción general

El módulo de compras permite registrar y consultar órdenes de compra, filtrarlas por fecha y estado, visualizar el detalle de una compra y anular compras cuando corresponda. La funcionalidad está dividida entre:

- rutas de Flask en `src/modulos/compras_rutas.py`
- lógica de acceso a datos en `src/modulos/comandos_db/comandos_db_compra.py`
- interfaz web en `src/templates/compra.html` y `src/templates/orden_compra.html`
- interacción del cliente en `src/static/js/compras.js` y `src/static/js/realizar_compra.js`

La idea general del flujo es:

1. La pantalla de gestión de compras lista las órdenes registradas.
2. El usuario puede buscar por número, proveedor o fecha.
3. Puede ver el resumen de una compra en una ventana modal.
4. Desde la pantalla de orden de compra puede elegir productos, un proveedor y registrar la operación.
5. Al registrar la compra se actualiza el stock del inventario y se persiste la compra junto con sus ítems.

## Estructura de archivos

### Rutas y controladores

Archivo: `src/modulos/compras_rutas.py`

Se define el blueprint `compras_bp` con las rutas principales:

| Método y ruta | Función | Descripción |
|---|---|---|
| `GET /compras` | `vista_gestion_compras` | Carga la pantalla de gestión de compras. |
| `GET /api/compras` | `api_compras` | Devuelve el listado paginado con filtros. |
| `GET /compra/<id>/detalle` | `vista_detalle_compra` | Devuelve la cabecera y los ítems de una compra. |
| `POST /api/compras/anular/<id_compra>` | `api_anular_compra` | Anula una compra y ajusta stock. |
| `GET /compras/realizar` | `vista_realizar_compra` | Carga la pantalla de nueva orden. |
| `POST /api/compras/realizar` | `api_realizar_compra` | Registra la compra en base de datos. |

### Plantillas

- `src/templates/compra.html`: pantalla principal con lista, filtros, métricas y modal de detalle.
- `src/templates/orden_compra.html`: pantalla para crear una orden de compra con catálogo de productos y proveedor.

### JavaScript

- `src/static/js/compras.js`: carga la tabla principal, aplica filtros, navega por páginas y maneja la anulación y el modal.
- `src/static/js/realizar_compra.js`: administra el carrito local, la búsqueda de productos, la selección de proveedor y la confirmación final.

## Pantalla de gestión de compras

La vista principal se renderiza con `compra.html` y muestra:

- cabecera con título y botón `Nueva Orden de Compra`
- dos métricas:
  - total de compras
  - total de productos comprados
- filtros por:
  - texto libre
  - rango de fecha
  - estado (`Activas`, `Anuladas`, `Todas`)
- tabla con columnas:
  - N° Orden
  - Fecha
  - Proveedor
  - Tipos de producto
  - Total de productos
  - Acciones
- paginación dinámica
- cartel emergente para mensajes de éxito, error o confirmación
- modal con detalle de la orden y total

### Filtros disponibles

La API `GET /api/compras` recibe los siguientes parámetros:

| Parámetro | Tipo | Valores esperados | Uso |
|---|---|---|---|
| `busqueda` | string | texto libre | busca por número de orden o nombre del proveedor |
| `filtro_fecha` | string | `hoy`, `semana`, `mes`, `anio`, `todos` | define el rango de fechas |
| `fecha_inicio` | string | `YYYY-MM-DD` | rango manual de inicio |
| `fecha_fin` | string | `YYYY-MM-DD` | rango manual de fin |
| `estado` | entero | `1`, `0`, `todos` | activa, anulada o todas |
| `pagina` | entero | `1` por defecto | página actual |
| `limite` | entero | `20` por defecto | cantidad de registros por página |

### Respuesta esperada

La respuesta JSON devuelta por la API tiene esta estructura:

```json
{
  "compras": [
    {
      "idcompra": 42,
      "fecha": "04/10/2026",
      "horas": "15:30:00",
      "proveedor": "Gomería Central",
      "tipo": "neumático, banda",
      "total_productos": 12,
      "estado": 1
    }
  ],
  "paginacion": {
    "pagina_actual": 1,
    "limite": 20,
    "total_registros": 42,
    "total_paginas": 3
  },
  "resumen": {
    "total_compras": 42,
    "total_productos": 321
  },
  "Exito": true
}
```

En caso de error de la base de datos, la ruta devuelve `500` con un mensaje y una redirección.

## Detalle de una compra

La ruta `GET /compra/<int:id>/detalle` obtiene la cabecera y los ítems pertenecientes a una compra concreta.

### Lógica de consulta

La clase `Compra.obtener_por_id(id_compra)` hace dos consultas:

1. trae la cabecera de la compra:
   - `idcompra`
   - `fecha`
   - `horas`
   - `proveedor`
   - `total_productos`
   - `activo`
2. trae el detalle de los ítems:
   - `iditem_compra`
   - `producto_nombre`
   - `producto_tipo`
   - `cantidad`
   - `precio_unitario`
   - `subtotal`

La respuesta final devuelve un JSON con:

```json
{
  "exito": true,
  "compra": {
    "idcompra": 42,
    "fecha": "04/10/2026",
    "horas": "15:30:00",
    "proveedor": "Gomería Central",
    "total_productos": 12,
    "activo": 1
  },
  "items": [
    {
      "iditem_compra": 15,
      "producto_nombre": "Neumático 185/65R15",
      "producto_tipo": "neumático",
      "cantidad": 4,
      "precio_unitario": 5000,
      "subtotal": 20000
    }
  ]
}
```

## Anulación de compras

La anulación se realiza desde la tabla principal con el botón `Anular`.

### Ruta

`POST /api/compras/anular/<int:id_compra>`

### Comportamiento

La clase `Compra.anular(id_compra)` ejecuta esta lógica:

1. valida que la compra exista y no esté ya anulada
2. obtiene los ítems asociados a la compra
3. descuenta las cantidades de cada producto del stock en `producto_servicio`
4. marca la compra como `activo = 0`
5. confirma la transacción con `commit()`

La lógica se implementa así:

```python
sql_revertir_stock = """
    UPDATE producto_servicio 
    SET cantidad_actual = cantidad_actual - %s 
    WHERE idproducto_servicio = %s AND tipo = 'producto';
"""
```

Esto permite que el stock vuelva a su estado anterior cuando la compra es anulada.

### Respuesta

Respuesta exitosa:

```json
{
  "exito": true,
  "mensaje": "La compra #42 fue anulada y el stock ajustado.",
  "redireccion": "/compras"
}
```

Si la compra no existe o ya está anulada, la API devuelve `400` o `500` según la condición.

## Registro de una nueva orden de compra

La creación de una compra se realiza desde la vista `orden_compra.html`, accesible por `GET /compras/realizar`.

### Funcionalidades de la pantalla

- catálogo de productos activos
- búsqueda por nombre
- filtro por tipo de producto
- selección de proveedor
- carrito local en memoria y persistido con `localStorage`
- resumen del pedido con cantidad total
- modal de confirmación antes de registrar

### Datos cargados al abrir la pantalla

La ruta `vista_realizar_compra()` llama a `Compra.obtener_datos_inicio_compra()` y carga:

- productos activos
- tipos de productos distintos
- proveedores activos

El método devuelve:

```python
productos, tipos, proveedores, estado = Compra.obtener_datos_inicio_compra()
```

### Proceso de compra

Cuando el usuario confirma la operación:

1. `realizar_compra.js` arma el payload en formato JSON.
2. Se envía a `POST /api/compras/realizar`.
3. La ruta valida que:
   - exista un proveedor
   - el carrito tenga al menos un producto
   - cada producto tenga una cantidad válida y positiva
4. Se calcula el total de unidades con `calcular_total_productos(carrito)`.
5. Se llama a `Compra.registrar(...)`.

### Payload esperado

```json
{
  "id_proveedor": 3,
  "carrito": [
    {
      "idproducto_servicio": 12,
      "cantidad": 5
    },
    {
      "idproducto_servicio": 18,
      "cantidad": 2
    }
  ]
}
```

### Respuesta esperada

```json
{
  "exito": true,
  "mensaje": "Compra registrada exitosamente con ID 43.",
  "id_compra": 43,
  "redireccion": "/compras"
}
```

## Clase `Compra` y acceso a datos

La clase `Compra` encapsula la lógica de persistencia y consultas a MySQL.

### `Compra.registrar(id_proveedor, listado_items, total_productos, fecha=None)`

Inserta la cabecera de la compra en la tabla `compra` y, en la misma transacción:

- crea la fila en `compra` con:
  - `fecha`
  - `horas`
  - `cantidad_total`
  - `idproveedor`
  - `activo = 1`
- crea los ítems en `item_compra`
- actualiza `cantidad_actual` en `producto_servicio` sumando la cantidad comprada

Devuelve `(id_compra, True)` si fue exitosa. Si ocurre un error MySQL, hace `rollback()` y retorna `(None, False)`.

### `Compra.obtener_compras_paginadas(...)`

Construye una consulta dinámica con filtros combinados usando `WHERE` y parámetros SQL. Permite filtrar por:

- texto libre
- proveedor
- rango de fechas
- estado activo/anulado

Además calcula:

- total de compras
- total de productos
- total de páginas para la paginación

El resultado final se entrega como diccionario con las claves:

- `compras`
- `paginacion`
- `resumen`
- `Exito`

### `Compra.obtener_por_id(id_compra)`

Lee una compra y sus ítems asociados. La unión se hace con:

- `compra` -> `proveedor`
- `item_compra` -> `producto_servicio`

Esta consulta es la base del modal de detalle del resumen de compra.

### `Compra.anular(id_compra)`

Realiza una baja lógica en la compra y deshace el ingreso de stock que se había realizado al registrar la compra.

### `Compra.obtener_datos_inicio_compra()`

Consulta los datos necesarios para poblar la pantalla de nueva compra:

- productos activos
- tipos distintos
- proveedores activos

## Base de datos involucrada

### Tablas relevantes

- `compra`: almacena la cabecera de la operación
- `item_compra`: guarda cada producto incluído en la orden
- `producto_servicio`: se actualiza con el stock nuevo y luego se revierte al anular
- `proveedor`: se usa para asociar la compra

### Campos principales

#### `compra`

- `idcompra`
- `fecha`
- `horas`
- `cantidad_total`
- `idproveedor`
- `activo`

#### `item_compra`

- `iditem_compra`
- `idproducto_servicio`
- `idcompra`
- `cantidad`
- `precio_unitario` (si está definido en el esquema)

#### `producto_servicio`

- `idproducto_servicio`
- `nombre`
- `tipo`
- `cantidad_actual`
- `activo`

## Consideraciones de implementación

- El carrito de compra se mantiene en el navegador con `localStorage` usando la clave `ordenCompraCarrito`, lo que permite conservar el pedido entre recargas.
- El registro de compra actualiza el stock sumando la cantidad comprada, pero la lógica de creación no calcula ni envía explícitamente un precio unitario para cada ítem en el payload. Esto debería revisarse si la aplicación necesita un costo asociado a cada compra en detalle.
- La vista principal usa `GET /api/compras` con filtros y paginación, por lo que la interfaz queda desacoplada de la recarga completa de la página.
- El módulo permite anular compras de manera lógica, pero no contempla aún un flujo de reactivación ni una consulta de compras anuladas con detalle histórico extendido.
- La validación del lado del servidor se centra en campos básicos (proveedor, carrito no vacío, cantidades positivas), pero no incluye validaciones más profundas de negocio ni control de sesión explícito en estas rutas.

## Resumen funcional

El módulo de compras cubre estos casos de uso principales:

- listar órdenes de compra
- buscar y filtrar órdenes
- ver el detalle de cada orden
- registrar una nueva compra desde el catálogo de productos
- ajustar el stock al registrar la compra
- anular una compra y descontar el stock asociado

Es un módulo central para la operación de inventario y compras del sistema, y actúa como puente entre la gestión de proveedores, productos y stock disponible.
