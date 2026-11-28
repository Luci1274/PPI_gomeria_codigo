# Documentación técnica del módulo de empleados

## Alcance y archivos

El módulo reúne el inicio de sesión, registro público, recuperación de contraseña y gestión de empleados. Sus componentes principales son:

- Rutas: `src/modulos/empleados_rutas.py`.
- Persistencia y contraseñas: `src/modulos/comandos_db/comandos_db_empleado.py`, clase `Usuario`.
- Gestión: `src/templates/empleados.html` y `src/static/js/empleados.js`.
- Acceso y recuperación: `src/templates/iniciar_sesion.html` y `src/static/js/login.js`.
- Control global de sesión y roles: `src/app.py`; lista de rutas públicas predeterminada: `src/config.py`.
- Esquema de referencia: `docs/estructura_y_datos_DB_27_11_2026.sql`.

La vista de gestión extiende `src/templates/plantailla_gestion.html` y carga `src/static/css/gestion.css` y `src/static/css/navbar.css`. La pantalla de acceso usa `src/static/css/iniciar_sesion.css`.

La visión general de la aplicación, la autorización global, la configuración y las relaciones de la base de datos están en la [documentación general del sistema](./sistema_y_base_de_datos.md). Este documento detalla los flujos de acceso y gestión de empleados.

## Modelo de datos

La tabla `empleado` del esquema de referencia contiene:

| Columna | Tipo | Restricciones / uso |
|---|---|---|
| `idempleado` | `int` | Clave primaria autoincremental. |
| `nombre_usuario` | `varchar(45)` | Obligatorio y único; se usa para iniciar sesión. |
| `mail` | `varchar(45)` | Opcional. |
| `contrasena` | `varchar(255)` | Obligatorio; almacena el hash, no la contraseña en texto plano. |
| `tipo` | `varchar(45)` | Obligatorio; representa el rol. |
| `activo` | `tinyint` | Obligatorio; predeterminado `1`. |
| `telefono` | `varchar(45)` | Opcional. |
| `token_recuperacion` | `varchar(10)` | Código temporal para restablecer la contraseña. |
| `token_expiracion` | `datetime` | Vencimiento del código. |

El esquema define una restricción `UNIQUE` para `nombre_usuario`. La comprobación previa en `Usuario.existe_usuario` mejora el mensaje de duplicado, y la restricción de la base de datos también evita duplicados concurrentes.

## Rutas

| Método y ruta | Función | Descripción |
|---|---|---|
| `GET /iniciar_sesion` | `iniciar_sesion` | Muestra la pantalla de acceso y registro. |
| `GET /registrarse` | `iniciar_sesion` | Alias de la pantalla anterior. |
| `POST /api/iniciar_sesion` | `api_iniciar_sesion` | Valida credenciales y crea la sesión. |
| `POST /api/registrarse` | `api_registrarse` | Registra un usuario con tipo `Empleado`. |
| `POST /api/recuperar/solicitar` | `api_solicitar_recuperacion` | Busca la cuenta y genera un código temporal. |
| `POST /api/recuperar/validar_token` | `api_validar_token` | Verifica el código de recuperación. |
| `POST /api/recuperar/restablecer` | `api_restablecer_contrasena` | Cambia la contraseña y limpia el código. |
| `GET /cerrar_sesion` | `cerrar_sesion` | Vacía la sesión y redirige al acceso. |
| `GET /empleados` | `gestion_empleados` | Renderiza la pantalla de gestión. |
| `GET /api/empleados` | `api_obtener_empleados` | Devuelve resultados paginados y filtrados. |
| `GET /api/empleados/<id>/editar` | `api_obtener_empleado` | Devuelve los datos de un empleado. |
| `POST /api/empleados/<id>/editar` | `api_modificar_empleado` | Actualiza los datos del empleado. |
| `POST /api/empleados/<id>/desactivar` | `api_desactivar_empleado` | Realiza una baja lógica. |
| `POST /api/empleados/<id>/activar` | `api_activar_empleado` | Reactiva un empleado inactivo. |

## Inicio de sesión, registro y recuperación

### Inicio de sesión

`POST /api/iniciar_sesion` recibe `txt_input_nombre`, `password_input` y `checkbox_recordar` como JSON o formulario. `Usuario.verificar_credenciales` busca una cuenta activa y valida el hash con Werkzeug. Si coincide, la ruta guarda en la sesión `id_usuario`, `nombre_usuario` y `tipo`, y responde `200` con redirección a `/`. Una credencial no válida responde `401`; si falla la comprobación inicial de conexión o la consulta de credenciales, responde `500`.

El navegador envía el estado del checkbox «Recordar». El servidor lo interpreta como verdadero para `true`, `1`, `on` o `yes` y asigna `session.permanent`. La duración concreta depende de la configuración de Flask.

### Registro

`POST /api/registrarse` recibe:

| Campo JSON | Columna |
|---|---|
| `input_nombre` | `nombre_usuario` |
| `txt_registro_email` | `mail` |
| `tel_input` | `telefono` |
| `password_registro` | Contraseña, guardada como hash en `contrasena`. |

En el navegador se comparan la contraseña y su confirmación; el servidor también exige nombre de usuario y contraseña no vacíos. Si se usa `intl-tel-input`, se envía el teléfono con código internacional. El servidor comprueba el nombre de usuario y crea la cuenta con tipo `Empleado` y estado activo; no hay un alta de empleado desde la pantalla de gestión.

La ruta responde `200` al registrar, `400` si faltan el nombre o la contraseña, si el nombre ya existe o si la base rechaza el duplicado; devuelve `500` si no puede comprobar el nombre o insertar el usuario por otra falla. La base de datos también impone unicidad sobre `nombre_usuario`.

### Recuperar contraseña

La pantalla de acceso presenta un modal de tres pasos:

1. Solicita el nombre de usuario y el correo o teléfono asociado.
2. Permite ingresar el código de seis dígitos.
3. Solicita la nueva contraseña y su confirmación.

El navegador compara las dos contraseñas antes de solicitar el cambio. El servidor busca una cuenta activa cuyo nombre coincida y cuyo correo o teléfono coincida exactamente con el contacto. El código se guarda con vencimiento a los 15 minutos. Si el contacto contiene `@`, se intenta enviar por correo; en otro caso, por SMS.

`POST /api/recuperar/solicitar` responde `400` si faltan datos, `404` si no encuentra una coincidencia, `500` si no puede conectarse o guardar el código y `200` si lo genera. Actualmente el servicio de envío captura sus propios errores, imprime el código en la consola del servidor y no los propaga a la ruta; por eso la respuesta puede indicar éxito aunque el envío externo haya fallado.

`POST /api/recuperar/validar_token` responde `200` si el código aún es válido y `400` si es incorrecto o expiró. `POST /api/recuperar/restablecer` exige una nueva contraseña no vacía y vuelve a verificar el código antes de guardar el nuevo hash; al actualizarlo, limpia `token_recuperacion` y `token_expiracion`. Responde `400` si falta la contraseña o el código es inválido/expiró, `200` si se actualiza y `500` si falla la escritura.

La búsqueda de cuenta y la verificación del token convierten algunos errores de consulta en el mismo resultado que «cuenta no encontrada» o «código inválido»; por eso esas fallas pueden responder `404` o `400` en lugar de `500`.

## Gestión de empleados

`GET /empleados` carga la estructura HTML; JavaScript consulta la API para poblar la tabla. La pantalla permite:

- buscar por nombre de usuario, correo o teléfono, con una espera de 300 ms;
- filtrar por rol y por estado, combinando ambos filtros con la búsqueda;
- navegar los resultados de diez en diez;
- editar nombre, correo, teléfono y rol desde un modal;
- desactivar empleados activos con confirmación y reactivar los inactivos.

La métrica muestra la cantidad total de filas que coinciden con los filtros actuales. Las bajas son lógicas (`activo = 0`); las filas inactivas se resaltan y ofrecen reactivación en lugar de edición o desactivación. El formulario no permite cambiar la contraseña.

### `GET /api/empleados`

Parámetros:

| Parámetro | Predeterminado | Uso |
|---|---|---|
| `pagina` | `1` | Página solicitada. |
| `buscar` | Vacío | Coincidencia parcial en nombre de usuario, correo o teléfono. |
| `rol` | Sin filtro | Coincidencia exacta con el tipo/rol. |
| `activo` | `1` | `1` activos, `0` inactivos o vacío para todos. |

La interfaz solicita diez filas por página y envía vacío para `rol` o `activo` cuando se selecciona «Todos». Si no hay coincidencias, `total_paginas` es `1`.

Respuesta exitosa (`200`):

```json
{
  "exito": true,
  "total_items": 0,
  "total_paginas": 1,
  "limite": 10,
  "empleados": [],
  "roles": []
}
```

`roles` contiene los valores distintos no vacíos de `empleado.tipo`, incluidos los que solo pertenecen a empleados inactivos. Si falla la comprobación de conexión o la consulta, la ruta responde `500`.

### Consulta, edición y estado

`GET /api/empleados/<id>/editar` devuelve `200` con `exito: true` y `empleado` (`idempleado`, `nombre`, `email`, `telefono`, `rol`, `activo`). Si no existe el ID responde `404`; si falla la consulta, `500`.

`POST /api/empleados/<id>/editar` recibe `nombre`, `email`, `telefono` y `rol`. Si se omite `rol`, la ruta usa `Empleado`. La capa de datos recorta espacios, normaliza el nombre y el rol a formato título, convierte el correo a minúsculas y quita espacios exteriores del teléfono. La ruta no recibe una contraseña. Responde `200` si se ejecuta la actualización o `500` ante un error; la capa de datos no verifica si el ID afectó una fila.

`POST /api/empleados/<id>/desactivar` actualiza solo empleados activos. Responde `200` si se modificó una fila, `400` si no se modificó ninguna fila o falla la operación de actualización y `500` si falla la comprobación inicial de conexión.

`POST /api/empleados/<id>/activar` cambia solo empleados inactivos a activos. Responde `200` si se modificó una fila, `400` si no estaba inactivo o falla la operación de actualización y `500` si falla la comprobación inicial de conexión.

## Sesión y permisos

`proteger_rutas`, en `src/app.py`, aplica la autorización global antes de cada solicitud:

- Las rutas estáticas se omiten.
- Sin `id_usuario` en sesión, una página redirige a `/iniciar_sesion`; una solicitud API recibe `401` JSON.
- Los tipos de usuario `AD` y `DEV` pueden acceder a todas las rutas protegidas.
- Los tipos `EM` y `EMPLEADO` solo pueden acceder a los endpoints enumerados en `ENDPOINTS_EMPLEADO` (`inicio`, ventas permitidas y cierre de sesión). La gestión de empleados no está incluida, por lo que queda restringida a `AD` y `DEV`.
- Con sesión pero sin permiso, las API reciben `403` JSON y las páginas redirigen a `/`.

Por defecto, `src/config.py` marca como públicas las vistas de acceso/registro y las API de inicio de sesión, registro y recuperación. Si se configura `RUTAS_PUBLICAS` en el entorno, esa lista reemplaza los valores predeterminados.

`Config.SECRET_KEY` se obtiene de `CLAVE_SECRETA`, pero actualmente usa `clave_por_defecto_dev` si la variable no está definida. En un despliegue debe configurarse una clave secreta propia mediante el entorno.

## Clase `Usuario` y utilidades de datos

| Método | Comportamiento |
|---|---|
| `hash_contraseña` / `verificar_credenciales` | Genera y valida hashes de contraseña con Werkzeug. El login solo encuentra cuentas activas. |
| `crear_usuario` | Inserta el empleado y devuelve su ID o `None` si falla MySQL. |
| `existe_usuario` | Busca por nombre, sin filtrar por estado; los usuarios inactivos también reservan su nombre. Devuelve `None` si no se puede comprobar. |
| `leer_empleados(...)` | Busca, filtra por rol/estado y pagina; devuelve `(total_items, empleados, roles, exito)`. |
| `leer_empleado(id)` | Consulta por ID sin filtrar por estado; devuelve `(empleado, True)` incluso sin fila y `(None, False)` ante error de MySQL. |
| `modificar_empleado(...)` | Normaliza y actualiza datos; permite contraseña opcional al invocarse directamente, pero la ruta de gestión no la envía. |
| `eliminar_empleado(id)` / `activar_empleado(id)` | Cambia `activo` y devuelve si se modificó una fila. |
| Métodos de recuperación | Buscan cuenta activa por nombre/contacto, guardan y verifican el token temporal, y actualizan la contraseña limpiando el token. |

`GenericosDB`, en `src/modulos/comandos_db/comando_db_genericos.py`, aporta la búsqueda `LIKE`, construcción de `WHERE`, normalización y comprobación de duplicados. Las operaciones de acceso a datos parametrizan los valores SQL.

## Consideraciones

- El servidor exige nombre y contraseña en el registro, y contraseña no vacía al restablecerla, pero no aplica una política de longitud/fuerza ni valida el formato del correo. La edición tampoco valida de forma completa los campos obligatorios ni sus longitudes; las validaciones HTML/JavaScript no sustituyen las del servidor.
- La edición por ID no filtra por estado y `modificar_empleado` no comprueba el número de filas afectadas. La pantalla solo ofrece editar para empleados activos, pero el endpoint protegido puede recibir un ID inactivo.
- El filtro por estado ya estaba disponible; el filtro por rol ahora se expone en la API y en la interfaz, reutilizando la lista `roles` que ya obtenía la capa de datos.
- La comprobación de nombre duplicado se complementa con la restricción única de la base. Si una carrera entre altas alcanza el `INSERT`, la restricción detiene la segunda inserción y la API devuelve `500`.
