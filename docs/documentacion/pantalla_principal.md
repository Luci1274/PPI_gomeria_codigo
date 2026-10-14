# Documentación de la pantalla principal

## Objetivo y alcance

La pantalla principal (`/`) presenta un resumen operativo: métricas de productos activos, clientes activos y ventas activas del día; las últimas ventas del día; alertas de stock bajo; accesos rápidos y navegación lateral.

Los datos se solicitan desde el navegador a una API Flask y se refrescan periódicamente. La pantalla no registra ventas ni modifica inventario: sus accesos conducen a los módulos correspondientes.

## Archivos involucrados

| Archivo | Responsabilidad |
|---|---|
| `src/app.py` | Protege `/`, renderiza `pantalla_principal.html` y expone `/api/datos-dashboard`. |
| `src/templates/pantalla_principal.html` | Estructura de métricas, accesos rápidos y tablas. |
| `src/templates/componentes/navbar.html` | Menú lateral y enlaces condicionales por tipo de usuario. |
| `src/static/js/pantalla_principal.js` | Consulta periódica, actualización de métricas/tablas y aviso de error. |
| `src/static/js/navbar.js` | Menú móvil y resaltado del enlace activo. |
| `src/static/css/pantalla_principal.css` | Estilos del contenido, tarjetas, tablas y responsive. |
| `src/static/css/navbar.css` | Estilos de la navegación lateral. |
| `src/modulos/comandos_db/comandos_db_pantalla_inicial.py` | Consultas SQL que componen los indicadores y listados. |

## Protección y renderizado

`GET /` pasa por la guardia global de `src/app.py`; requiere una sesión activa. Si falta, la aplicación redirige al inicio de sesión. La ruta renderiza `pantalla_principal.html` y envía `nombre_usuario` desde la sesión, usando `"Usuario"` como fallback.

El inicio de sesión, el registro y el comportamiento de la sesión se describen en [inicio_sesion_registro.md](./inicio_sesion_registro.md).

La barra lateral muestra además el nombre y el tipo guardados en la sesión. `AD` y `DEV` ven accesos a ventas, compras, inventario, clientes, proveedores y empleados. `Empleado` ve Principal, Ventas y Cerrar Sesión. Los accesos rápidos del cuerpo muestran a `AD` y `DEV` Nueva venta, Nuevo cliente, Cargar stock y Nueva Compra; a `Empleado`, Nueva venta.

La guardia central de `src/app.py` aplica también la autorización por rol en el servidor: `AD` y `DEV` tienen acceso total; `Empleado` solo puede acceder al dashboard y a las funciones de ventas permitidas. Los demás roles reciben `403` en las rutas protegidas.

## Actualización de datos: `GET /api/datos-dashboard`

El endpoint llama a `mostrar()` y devuelve:

```json
{
  "exito": true,
  "total_productos": 25,
  "total_clientes": 40,
  "ventas_dia": 3,
  "ultimas_ventas": [],
  "productos_bajos": []
}
```

Si las consultas a MySQL fallan, el acceso a datos retorna valores vacíos y `exito: false`; la ruta responde `500` con un mensaje de error. Si la API responde con error HTTP, JSON no exitoso o falla la conexión de red, el JavaScript muestra el cartel de error. Una respuesta posterior exitosa oculta el cartel y vuelve a renderizar los datos.

`pantalla_principal.js` hace una carga al abrir el documento y repite la petición cada 10 segundos.

## Métricas

| Indicador | Cálculo |
|---|---|
| Total Productos | Cuenta filas de `producto_servicio` con `activo = 1`. Cuenta servicios también; no representa unidades físicas en stock. |
| Total Clientes | Cuenta filas de `cliente` con `activo = 1`. |
| Ventas del Día | Cuenta ventas con `activa = 1` y fecha de emisión de hoy, según `CURDATE()` de MySQL. |

Las métricas se cuentan independientemente de las ventas listadas debajo.

## Últimas ventas

La consulta selecciona hasta cinco filas de ventas activas cuya fecha de emisión sea la fecha actual de MySQL, ordenadas por `idventa` descendente. Devuelve nombre y apellido del cliente (con textos alternativos si faltan), total, método de pago y `estado`; si no hay ventas, la interfaz muestra **No hay ventas recientes**.

La consulta une ventas con `historial_pago_cliente` y métodos de pago. Si una venta tiene más de un registro de pago, la unión puede producir más de una fila para esa venta y ocupar más de un lugar de los cinco resultados. La interfaz muestra el valor de `estado` sin traducir sus estados numéricos; además usa `venta.estado || 'completa'`, por lo que el valor `0` se presenta como `completa`.

## Alertas de stock bajo

La consulta lista productos activos para los que `cantidad_actual < cantidad_minima`, con ID, nombre y cantidad actual. Si no hay coincidencias, la tabla muestra **No hay productos con stock bajo**. Cada fila ofrece **Reponer**, que enlaza a `/compras/realizar`.

La condición excluye productos cuya cantidad actual sea igual al mínimo. Si `cantidad_minima` es `NULL`, la comparación SQL no clasifica ese artículo como alerta.

## Comportamiento de error

La carga inicial de la plantilla deja las métricas con `--` hasta recibir respuesta. Si la carga falla, se presenta un cartel flotante; las métricas y tablas conservan los últimos valores renderizados, si los había. La actualización automática posterior intenta recuperar el estado sin recargar toda la página.

## Consideraciones y limitaciones

- La tarjeta **Total Productos** mide filas activas del catálogo, no la suma de `cantidad_actual`.
- Las métricas y el filtro de últimas ventas usan el reloj de MySQL (`CURDATE()`), mientras que la fecha visible la construye el navegador con la zona horaria y locale `es-ES`; cerca del cambio de día pueden diferir.
- La consulta de ventas puede repetir una venta si existen varios registros de pago vinculados.
- El campo de estado de las ventas se imprime como valor crudo y el valor `0` se sustituye por el texto `"completa"` por el fallback lógico de JavaScript.
- Ante errores de carga no se limpian las métricas ni las tablas; queda visible el último estado válido junto con el cartel de error.
- Los enlaces ocultos según `session["tipo"]` son una decisión de presentación; la autorización efectiva depende de la guardia de sesión general.
