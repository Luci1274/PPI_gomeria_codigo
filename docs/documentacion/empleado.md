# Documentación técnica del módulo de empleados

## Descripción general

El módulo de empleados concentra tres funciones relacionadas:

- inicio y cierre de sesión;
- registro de usuarios, que crea registros en la tabla `empleado`;
- consulta, edición y desactivación lógica de empleados.

La implementación se distribuye entre:

- `src/modulos/empleados_rutas.py`: rutas Flask y respuestas de la API;
- `src/modulos/comandos_db/comandos_db_empleado.py`: clase `Usuario` y operaciones sobre MySQL;
- `src/modulos/comandos_db/comando_db_genericos.py`: utilidades compartidas para búsquedas, filtros, normalización y comprobación de duplicados;
- `src/templates/iniciar_sesion.html` y `src/static/js/login.js`: interfaz de inicio de sesión y registro;
- `src/templates/componentes/cartel_emergente.html`: aviso reutilizable compartido por el acceso, la gestión y las órdenes;
- `src/templates/empleados.html` y `src/static/js/empleados.js`: pantalla de gestión;
- `docs/comandos_creacion_db.sql`: definición estructural de la tabla `empleado`.

La plantilla de gestión extiende `src/templates/plantailla_gestion.html`. Sus estilos se complementan con `src/static/css/empleado.css` y `src/static/css/gestion.css`.

## Modelo de datos

La tabla `empleado` tiene las siguientes columnas:

| Columna | Tipo | Restricciones / valor predeterminado | Uso |
|---|---|---|---|
| `idempleado` | `int` | Clave primaria, autoincremental | Identificador del empleado. |
| `nombre_usuario` | `varchar(45)` | No admite `NULL` | Nombre utilizado como usuario de acceso y mostrado en la gestión. |
| `mail` | `varchar(45)` | Admite `NULL` | Correo electrónico. |
| `contrasena` | `varchar(255)` | No admite `NULL` | Hash de la contraseña. |
| `tipo` | `varchar(45)` | No admite `NULL` | Rol o tipo del usuario. |
| `activo` | `tinyint` | No admite `NULL`; predeterminado `1` | Estado lógico del registro. |
| `telefono` | `varchar(45)` | Admite `NULL` | Teléfono de contacto. |

El esquema está definido en `docs/comandos_creacion_db.sql`. Al registrarse desde la pantalla de inicio de sesión, el usuario se inserta intencionalmente con el tipo `"Empleado"` y el estado activo predeterminado de la tabla.

## Inicio y cierre de sesión

### Inicio de sesión

La vista de acceso se sirve desde `GET /iniciar_sesion`. También se muestra en `GET /registrarse`; ambas rutas renderizan `iniciar_sesion.html`, que permite alternar entre los formularios de inicio y registro.

`POST /api/iniciar_sesion` recibe `txt_input_nombre`, `password_input` y `checkbox_recordar`. La clase `Usuario` busca un usuario activo por `nombre_usuario`, valida la contraseña con Werkzeug y, si las credenciales son correctas, Flask guarda en la sesión:

- `id_usuario`: identificador del empleado;
- `nombre_usuario`: nombre de usuario;
- `tipo`: tipo o rol almacenado en la base de datos.

La respuesta exitosa es `200`:

```json
{
  "exito": true,
  "mensaje": "Inicio de sesión exitoso",
  "redireccion": "/"
}
```

Si la conexión con la base de datos no está disponible, la ruta devuelve `500`. Si las credenciales no son válidas, devuelve `401` con `exito: false`.

El navegador envía el estado real del checkbox (`true` o `false`). El servidor interpreta como verdadero los valores `true`, `1`, `on` o `yes`; de ese modo la sesión solo se hace permanente cuando se marcó «Recordar». La duración de esa sesión depende de la configuración Flask, que no se define en este módulo.

Los errores de acceso, conexión y validación se muestran en el cartel emergente compartido. El HTML del componente se define una sola vez en `src/templates/componentes/cartel_emergente.html` y se incluye desde la plantilla de inicio de sesión.

### Registro

`POST /api/registrarse` recibe:

| Campo JSON | Dato almacenado |
|---|---|
| `input_nombre` | `empleado.nombre_usuario` |
| `txt_registro_email` | `empleado.mail` |
| `tel_input` | `empleado.telefono` |
| `password_registro` | Hash guardado en `empleado.contrasena` |

El navegador compara la contraseña con su confirmación antes de enviar la solicitud. El servidor comprueba si ya existe el nombre de usuario y, si no existe, crea el registro con tipo `"Empleado"` y activo. Este formulario de registro es público y se encuentra en la pantalla de inicio de sesión; no hay un alta desde la pantalla de gestión. Si el alta finaliza correctamente, la ruta devuelve `200` y la redirección a `/iniciar_sesion`. Un nombre de usuario existente produce `400`; los errores de conexión o de inserción producen `500`.

El método `Usuario.existe_usuario` comprueba el nombre sin filtrar por estado, de modo que un empleado desactivado también impide registrar de nuevo ese mismo nombre. Si no se puede ejecutar la comprobación por un error de base de datos, el endpoint responde `500` y no continúa con el alta.

### Cierre de sesión

`GET /cerrar_sesion` vacía la sesión mediante `session.clear()` y redirige a `/iniciar_sesion`.

## Gestión de empleados

### Pantalla

`GET /empleados` renderiza `empleados.html`. La tabla se carga y actualiza mediante JavaScript, sin recargar la página. La pantalla muestra:

- el total de empleados que coinciden con la consulta;
- búsqueda por nombre de usuario, correo o teléfono;
- una tabla con nombre, correo, teléfono, rol y acciones;
- paginación de diez registros;
- un modal para modificar los datos;
- confirmación y notificación al desactivar un empleado.

La búsqueda espera 300 ms desde la última modificación del texto antes de consultar la API. No hay un formulario de alta en esta pantalla: el alta disponible se realiza desde el formulario de registro de la pantalla de acceso.

El modal de edición también se cierra al hacer clic sobre el fondo exterior; el manejador global solo consulta el modal que existe en esta pantalla.

### Rutas de gestión

| Método y ruta | Función | Resultado |
|---|---|---|
| `GET /empleados` | `gestion_empleados` | Renderiza la pantalla de gestión. |
| `GET /api/empleados` | `api_obtener_empleados` | Devuelve empleados activos, con búsqueda y paginación. |
| `GET /api/empleados/<id>/editar` | `api_obtener_empleado` | Devuelve los datos de un empleado para el modal. |
| `POST /api/empleados/<id>/editar` | `api_modificar_empleado` | Actualiza nombre, correo, teléfono y rol. |
| `POST /api/empleados/<id>/desactivar` | `api_desactivar_empleado` | Marca el empleado como inactivo. |

### `GET /api/empleados`

Parámetros de consulta:

| Parámetro | Tipo / valor predeterminado | Uso |
|---|---|---|
| `pagina` | Entero, `1` | Página solicitada. |
| `buscar` | Texto opcional | Busca coincidencias en nombre de usuario, correo o teléfono. |

La ruta solicita diez registros por página y filtra por activos al usar el valor predeterminado de `Usuario.leer_empleados`. Una respuesta exitosa (`200`) tiene esta estructura:

```json
{
  "exito": true,
  "total_items": 0,
  "total_paginas": 1,
  "limite": 10,
  "empleados": []
}
```

Cuando no hay coincidencias, `total_paginas` vale `1`. Si falla la conexión o la consulta, la ruta devuelve `500` y `exito: false`.

La capa de acceso a datos también admite filtros por `rol` y `activo`, pero la ruta no los recibe ni los transmite. Tampoco incluye en su respuesta la lista de roles que obtiene el método `leer_empleados`.

### Consulta y modificación

La consulta de un empleado devuelve `200` con `exito: true` y un objeto `empleado` que contiene `idempleado`, `nombre`, `email`, `telefono`, `rol` y `activo`. Si no encuentra el identificador, devuelve `404`.

La modificación recibe un JSON con `nombre`, `email`, `telefono` y `rol`. Si no se envía el rol, la ruta usa `"Empleado"`. La clase `Usuario` normaliza el nombre y el rol a formato título, convierte el correo a minúsculas y quita espacios exteriores de teléfono. La contraseña no forma parte del formulario ni se cambia desde esta ruta.

Una modificación exitosa devuelve `200`; un error de persistencia devuelve `500`.

### Baja lógica

La desactivación se realiza mediante `UPDATE empleado SET activo = 0`; el registro no se elimina físicamente. La ruta devuelve `200` si la operación termina sin error y `400` si falla.

El listado filtra por activos de manera predeterminada, por lo que los empleados desactivados dejan de aparecer en la pantalla. No se implementa aquí una operación para reactivarlos.

## Acceso y permisos

Las rutas de inicio de sesión y registro están incluidas entre las rutas públicas predeterminadas de `src/config.py`. El resto de las solicitudes pasa por la guardia global `proteger_rutas` de `src/app.py`, que exige una sesión.

Los usuarios cuyo tipo normalizado sea `AD` o `DEV` pueden acceder a todas las rutas protegidas. Los tipos `EM` o `EMPLEADO` solo pueden acceder a los endpoints incluidos expresamente en `ENDPOINTS_EMPLEADO`; las rutas de gestión de empleados no están en esa lista. Por lo tanto, la gestión queda reservada a los tipos `AD` y `DEV`.

## Clase `Usuario` (acceso a datos)

| Método | Comportamiento |
|---|---|
| `hash_contraseña(contraseña)` | Genera un hash con `werkzeug.security.generate_password_hash`. |
| `verificar_credenciales(nombre, contraseña)` | Busca por nombre de usuario activo, valida el hash y devuelve identificador, tipo y nombre; si no coinciden devuelve `None`. |
| `crear_usuario()` | Genera el hash e inserta nombre, correo, teléfono, contraseña y tipo; devuelve el identificador generado o `None` ante un error de MySQL. |
| `existe_usuario(nombre)` | Comprueba si existe el nombre de usuario, sin filtrar por estado; devuelve `None` si la consulta falla para impedir que el alta continúe sin verificar duplicados. |
| `leer_empleados(...)` | Aplica búsqueda, filtros disponibles en la capa de datos y paginación; devuelve `(total_items, empleados, roles, exito)`. |
| `leer_empleado(id)` | Obtiene un empleado por identificador, incluyendo su estado; no excluye los inactivos. Devuelve `(empleado, True)` aunque no encuentre filas, o `(None, False)` ante un error de MySQL. |
| `modificar_empleado(id, ...)` | Actualiza nombre, correo, teléfono y tipo; admite cambiar también la contraseña si se invoca directamente con ese argumento. |
| `eliminar_empleado(id)` | Realiza la baja lógica actualizando `activo` a `0`. |

Las consultas parametrizan los valores con marcadores `%s`. Los errores de las operaciones de base de datos se imprimen en la salida del servidor; las operaciones de escritura confirman la transacción si terminan correctamente y hacen rollback cuando capturan un error.

## Utilidades compartidas de base de datos

La clase `GenericosDB`, en `src/modulos/comandos_db/comando_db_genericos.py`, reúne lógica que se utiliza desde varias clases de acceso a datos:

- `normalizar_texto` recorta espacios y permite normalizar texto a formato título o minúsculas;
- `agregar_filtro_busqueda` agrega condiciones `LIKE` parametrizadas para una o varias columnas;
- `construir_where` arma la cláusula `WHERE` a partir de condiciones y devuelve una cadena vacía cuando no hay filtros;
- `existe_registro` comprueba duplicados con criterios parametrizados y normalización opcional para comparar textos sin distinguir mayúsculas ni espacios exteriores.

La comprobación de duplicados se usa para nombres de usuario y para la combinación de nombre, tipo, marca y medidas del producto. Es una verificación a nivel de aplicación: el esquema adjunto no define una restricción `UNIQUE` para estos casos, así que dos altas simultáneas aún podrían superar la comprobación antes de insertar.

## Puntos a revisar

- **Validación de datos en servidor:** las rutas de registro y edición no validan de forma explícita los campos obligatorios, formato de correo ni longitudes antes de llamar a la capa de datos. Conviene definir estas reglas en el servidor, además de las restricciones del formulario.
- **Baja sin confirmación de estado en la base:** `eliminar_empleado` devuelve éxito si la consulta no genera excepción, aunque el identificador no exista o ya estuviera inactivo; no comprueba el número de filas afectadas.
- **Edición de empleados inactivos:** la consulta por ID y la actualización no filtran por `activo`, aunque el listado normal solo muestra activos. Un cliente que conozca el ID puede pedir los datos y modificar un registro inactivo.
- **Los filtros de rol y estado no están disponibles en la pantalla:** existen parámetros en la capa de datos, pero no se exponen en la ruta ni en la interfaz.