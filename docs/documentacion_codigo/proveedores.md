# Documentación técnica del módulo de proveedores

## Descripción general

El módulo permite consultar, buscar, filtrar, crear, modificar, desactivar y reactivar proveedores. La baja es lógica: los registros permanecen en la base de datos para conservar las referencias de las compras anteriores. Solo los proveedores activos se ofrecen para crear nuevas compras.

Archivos principales:

- Rutas Flask: [`src/modulos/proveedores_rutas.py`](../../src/modulos/proveedores_rutas.py).
- Acceso a datos: [`src/modulos/comandos_db/comandos_db_proveedores.py`](../../src/modulos/comandos_db/comandos_db_proveedores.py).
- Interfaz: [`src/templates/proveedor.html`](../../src/templates/proveedor.html) y [`src/static/js/proveedores.js`](../../src/static/js/proveedores.js).
- Esquema de referencia: [`estructura_y_datos_DB_27_11_2026.sql`](../estructura_y_datos_DB_27_11_2026.sql).

## Acceso y permisos

Todas las rutas requieren una sesión iniciada. Según la protección global de `app.py`, la gestión de proveedores está permitida a usuarios administradores (`AD`) y desarrolladores (`DEV`); no forma parte de los endpoints habilitados para empleados. Las solicitudes API sin sesión reciben `401` y las sesiones sin permisos reciben `403`. El acceso no autorizado a páginas normales se redirige.

## Rutas

| Método y ruta | Función | Resultado |
|---|---|---|
| `GET /proveedores` | `vista_gestion_proveedores` | Renderiza la pantalla de gestión. |
| `GET /api/proveedores` | `api_proveedores` | Devuelve proveedores filtrados y paginados, además de rubros y ciudades disponibles. |
| `POST /api/proveedores/crear` | `api_crear_proveedor` | Crea un proveedor activo. |
| `GET /proveedores/<id>/editar` | `api_obtener_proveedor` | Devuelve los datos de un proveedor para el formulario de edición. |
| `POST /api/proveedores/<id>/editar` | `api_modificar_proveedor` | Actualiza sus datos. |
| `POST /proveedores/<id>/desactivar` | `api_desactivar_proveedor` | Desactiva lógicamente un proveedor activo. |
| `POST /api/proveedores/<id>/activar` | `activar_proveedor` | Reactiva un proveedor inactivo. |

Las rutas para desactivar y reactivar modifican datos y por eso utilizan `POST`.

## Listado, búsqueda y filtros

La pantalla muestra el total de resultados que coinciden con los filtros, una tabla de proveedores y paginación de 10 registros por página. La tabla presenta identificador, nombre y rubro, CUIT, ciudad y dirección, teléfono, correo, estado y acciones.

| Filtro | Parámetro | Comportamiento |
|---|---|---|
| Texto | `buscar` | Coincidencia parcial por nombre o CUIT. |
| Rubro | `rubro` | Coincidencia exacta. |
| Estado | `activo` | `1` para activos, `0` para inactivos y vacío para todos. La pantalla inicia mostrando activos. |
| Ciudad | `ciudad` | Coincidencia exacta. |
| Página | `pagina` | Entero desde 1; predeterminado `1`. |

La lista se ordena por `idproveedor` ascendente. `total_items` cuenta todos los resultados filtrados, no solo los de la página visible. `total_paginas` es al menos 1, incluso si no hay resultados; una página solicitada mayor que la última disponible se ajusta a la última página. Los catálogos de rubros y ciudades se obtienen del conjunto completo de proveedores y se actualizan en la interfaz después de cada carga.

Respuesta exitosa de `GET /api/proveedores`:

```json
{
  "exito": true,
  "proveedores": [
    {
      "idproveedor": 12,
      "nombre": "Proveedor Ejemplo",
      "cuit": "30123456789",
      "direccion": "San Martín 123",
      "mail": "contacto@example.com",
      "ciudad": "Rosario",
      "telefono": "3411234567",
      "rubro": "Insumos",
      "activo": 1
    }
  ],
  "rubros": [{"rubro": "Insumos"}],
  "ciudades": [{"ciudad": "Rosario"}],
  "pagina_actual": 1,
  "total_paginas": 1,
  "total_items": 1
}
```

`rubros` y `ciudades` incluyen valores distintos no vacíos, también de proveedores inactivos. La API responde `400` si la página no es un entero positivo o si `activo` no es vacío, `0` o `1`; responde `500` si falla la consulta.

## Crear y modificar proveedores

El formulario recoge nombre, CUIT, teléfono, correo, rubro, ciudad y dirección. Nombre, CUIT y rubro son obligatorios; los demás campos son opcionales. La API recibe y recorta espacios en los campos de texto. En la creación, si se omite `rubro`, se usa `General`; si se envía vacío, se rechaza. Rubro y ciudad se normalizan con mayúscula inicial por palabra al guardarse.

El esquema limita los campos a:

| Campo | Máximo |
|---|---:|
| `nombre` | 45 caracteres |
| `cuit` | 20 caracteres |
| `direccion` | 45 caracteres |
| `mail` | 45 caracteres |
| `ciudad` | 45 caracteres |
| `telefono` | 45 caracteres |
| `rubro` | 75 caracteres |

El CUIT tiene una restricción de unicidad en la base de datos. No se fuerza un formato numérico de 11 dígitos en la aplicación; se conserva el formato como texto y se respetan los datos históricos.

| Operación | Éxito | Errores principales |
|---|---|---|
| Crear | `201` | `400` por JSON/campos inválidos, `409` por CUIT duplicado, `500` por error de base de datos. |
| Obtener para editar | `200` | `404` si no existe, `500` por error de base de datos. |
| Modificar | `200` | `400` por JSON/campos inválidos, `404` si no existe, `409` por CUIT duplicado, `500` por error de base de datos. |

## Baja y reactivación

Desactivar no elimina la fila: actualiza `proveedor.activo` a `0`. Los proveedores inactivos siguen apareciendo si el filtro de estado es “Todos” o “Inactivo”, pero no se ofrecen para nuevas órdenes de compra. Reactivar actualiza el indicador a `1`.

La API devuelve `404` si no existe un proveedor en el estado requerido para la operación y `500` si falla la base de datos. Las compras existentes conservan su relación con el proveedor.

## Esquema de datos

La tabla `proveedor` utiliza `idproveedor` como clave primaria autoincremental y `cuit` como clave única. `nombre` y `rubro` son obligatorios; ciudad, dirección, correo y teléfono admiten `NULL` en el esquema; `activo` es un indicador lógico con valor predeterminado `1`.

La tabla `compra` referencia `proveedor.idproveedor` mediante una clave foránea. Por ese motivo, la baja lógica preserva la integridad y el historial de compras.