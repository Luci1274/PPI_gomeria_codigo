# Documentación del módulo de empleados

## Objetivo y alcance

El módulo gestiona la pantalla de consulta y edición de empleados y ofrece las rutas de autenticación usadas por el sistema. El inicio de sesión y el registro se documentan en [inicio_sesion_registro.md](./inicio_sesion_registro.md). Los usuarios se almacenan en `empleado`; las credenciales se verifican contra el hash de contraseña y solo las cuentas activas pueden iniciar sesión.

La pantalla de gestión no crea empleados actualmente. El botón **Nuevo Empleado** está en la plantilla, pero no tiene un formulario o manejador activo. El alta implementada es el registro desde la pantalla de inicio de sesión.

## Archivos involucrados

| Archivo | Responsabilidad |
|---|---|
| `src/modulos/empleados_rutas.py` | Rutas de autenticación, listado, edición, baja lógica y cierre de sesión. |
| `src/modulos/comandos_db/comandos_db_empleado.py` | Clase `Usuario`, persistencia de credenciales y consultas de empleados. |
| `src/templates/empleados.html` | Pantalla de gestión y formulario modal de edición. |
| `src/static/js/login.js` | Cambio entre formularios, validación de confirmación y peticiones de login/registro. |
| `src/static/js/empleados.js` | Listado, búsqueda, paginación, edición y desactivación. |

## Protección de rutas y sesión

`src/app.py` aplica una comprobación global antes de cada ruta. Los endpoints configurados como públicos se permiten sin sesión; las demás rutas requieren que exista `session["id_usuario"]`. Las solicitudes API sin sesión reciben `401` JSON; las vistas redirigen a `/iniciar_sesion`.

Con la configuración predeterminada, el inicio de sesión, el registro y sus vistas son públicos. Al iniciar sesión correctamente se guardan en la sesión `id_usuario`, `nombre_usuario` y `tipo`. El cierre de sesión limpia todos los datos de sesión y redirige al login.

La guardia autoriza las rutas según el tipo de sesión:

- **AD** y **DEV** pueden acceder a todas las rutas protegidas.
- **Empleado** (también el código de rol `EM`) puede entrar al inicio y su API de dashboard, consultar ventas, abrir detalles, anularlas y registrar ventas. También puede cerrar sesión.
- Los demás roles no tienen acceso a rutas protegidas. Una API no autorizada responde `403` JSON; una página no autorizada responde `403`.

El control se aplica en el servidor y no depende solamente de los enlaces que muestre la interfaz. El menú del Empleado no ofrece accesos a gestión de empleados, clientes, inventario, proveedores ni compras.

## Rutas

| Método y ruta | Función | Descripción |
|---|---|---|
| `GET /iniciar_sesion` | `iniciar_sesion` | Renderiza los formularios de login y registro. |
| `GET /registrarse` | `iniciar_sesion` | Alias que renderiza la misma plantilla. |
| `POST /api/iniciar_sesion` | `api_iniciar_sesion` | Verifica las credenciales y crea la sesión. |
| `POST /api/registrarse` | `api_registrarse` | Registra una cuenta con rol predeterminado. |
| `GET /empleados` | `gestion_empleados` | Renderiza la pantalla de gestión. |
| `GET /api/empleados` | `api_obtener_empleados` | Devuelve la página de empleados activos y el total. |
| `GET /api/empleados/<id>/editar` | `api_obtener_empleado` | Devuelve los datos del empleado. |
| `POST /api/empleados/<id>/editar` | `api_modificar_empleado` | Actualiza nombre, correo, teléfono y rol. |
| `POST /api/empleados/<id>/desactivar` | `api_desactivar_empleado` | Desactiva lógicamente un empleado. |
| `GET /cerrar_sesion` | `cerrar_sesion` | Limpia la sesión y redirige al login. |

## Gestión de empleados

La pantalla muestra nombre, correo, teléfono y rol, con búsqueda por nombre, correo o teléfono y paginación de 10 registros. La ruta usa `Usuario.leer_empleados(...)` con el estado predeterminado `activo = 1`; por ello el listado solo devuelve empleados activos y no hay filtro visual para consultar inactivos. La métrica refleja el total de coincidencias, no solo la página visible.

La respuesta exitosa de `GET /api/empleados` contiene:

```json
{
  "exito": true,
  "total_items": 1,
  "total_paginas": 1,
  "limite": 10,
  "empleados": [
    {
      "idempleado": 4,
      "nombre": "Nombre",
      "email": "usuario@example.com",
      "telefono": "1122334455",
      "rol": "Empleado",
      "activo": 1
    }
  ]
}
```

Aunque el acceso a datos también consulta una lista de roles, la ruta no la incluye en su JSON. La pantalla no presenta un selector de rol en la tabla; sí permite editar el rol como texto.

### Modificación

Al editar, la pantalla solicita `GET /api/empleados/<id>/editar`, que devuelve nombre, email, teléfono, rol y estado. La ruta devuelve `404` si no obtiene un empleado y `500` si la comprobación previa de conexión falla.

`POST /api/empleados/<id>/editar` recibe `nombre`, `email`, `telefono` y `rol`. `Usuario.modificar_empleado(...)` normaliza el nombre a formato título, el correo a minúsculas, elimina espacios exteriores del teléfono y convierte el rol a formato título; si no se proporciona rol, usa `"Empleado"`. La ruta no modifica la contraseña ni el estado del usuario.

La API responde `200` si el método de datos devuelve éxito y `500` si devuelve falso. El método de actualización no verifica que el ID exista ni inspecciona `rowcount`, por lo que un ID inexistente puede reportarse como actualizado si la consulta no falla.

### Desactivación lógica

La acción **Eliminar** solicita confirmación y envía `POST /api/empleados/<id>/desactivar`. El método `Usuario.eliminar_empleado(id)` ejecuta `UPDATE empleado SET activo = 0`; el registro y sus referencias históricas se conservan.

La ruta devuelve `200` si el método retorna verdadero y `400` si retorna falso. El método no verifica filas afectadas: un ID inexistente puede resultar en una respuesta de éxito si el `UPDATE` se ejecuta sin error. Los empleados desactivados no aparecen en el listado inicial.

## Acceso a datos: métodos principales

### `Usuario.verificar_credenciales(nombre_ingresado, contrasena_ingresada)`

Busca una cuenta activa por nombre. Devuelve `[idempleado, tipo, nombre_usuario]` si la contraseña coincide, `None` si las credenciales no coinciden o `False` ante error MySQL.

### `Usuario.crear_usuario()`

Genera el hash de la contraseña e inserta nombre de usuario, correo, teléfono, hash y tipo. Devuelve el ID insertado o `None` ante error.

### `Usuario.existe_usuario(nombre_usuario)`

Comprueba si existe exactamente ese nombre de usuario, sin filtrar por estado activo. Devuelve `True` o `False`; ante error MySQL también devuelve `False`.

### `Usuario.leer_empleados(pagina=1, por_pagina=10, buscar=None, rol=None, activo=1)`

Devuelve `(total_items, empleados, roles, exito)`. La búsqueda parcial abarca nombre de usuario, email y teléfono; admite filtros por rol y estado. Un error de base de datos da como resultado `(0, [], [], False)`.

### `Usuario.leer_empleado(id_empleado)`

Busca por ID sin filtrar por estado activo y devuelve `(empleado, True)` si la consulta se ejecuta, incluso si no encuentra fila. Ante error MySQL devuelve `(None, False)`.

### `Usuario.modificar_empleado(...)` y `Usuario.eliminar_empleado(...)`

Actualizan los datos de una cuenta o la desactivan lógicamente. Ambos métodos reportan éxito según la ejecución de la consulta, no según la existencia o cantidad de filas modificadas.

## Consideraciones y limitaciones

- No se encontró un índice único en el SQL versionado para `nombre_usuario` o `mail`.
- El alta primero llama a `existe_usuario` y luego inserta desde otra conexión; la comprobación y el `INSERT` no son atómicos, así que solicitudes concurrentes pueden crear el mismo nombre si la base no tiene una restricción única.
- `Usuario.existe_usuario` devuelve `False` tanto si el nombre no existe como si falla la consulta. Si `probar_conexion()` tuvo éxito pero la consulta específica falla, la ruta puede continuar intentando el alta.
- La edición tampoco verifica duplicados de nombre de usuario o correo.
- El botón **Nuevo Empleado** de la gestión no tiene una ruta de creación activa ni manejador de formulario; el alta existente es el registro público.
- La modificación no cambia contraseña ni estado y no comprueba filas afectadas.
- La desactivación no distingue entre un empleado inexistente y uno actualizado, dado que no comprueba `rowcount`.
- El checkbox **Recordar** no utiliza la propiedad `checked`, por lo que la opción puede quedar activa aunque no se marque.
- La pantalla de gestión no ofrece filtro de estado; solo lista activos por defecto. El acceso a datos permite filtrar inactivos, pero la ruta no expone ese parámetro.
- Las rutas `/api/empleados` exigen sesión por la guardia global, pero no aplican autorización por rol.
