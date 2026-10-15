# Documentación de inicio de sesión y registro

## Objetivo y alcance

La pantalla permite iniciar sesión con una cuenta existente o registrar una cuenta nueva. Ambas funciones comparten la plantilla `iniciar_sesion.html` y alternan entre sus formularios sin navegar a otra página.

El registro está habilitado desde la pantalla pública de autenticación. No equivale al alta administrativa desde la pantalla de gestión de empleados: esa función no está implementada actualmente.

## Archivos involucrados

| Archivo | Responsabilidad |
|---|---|
| `src/modulos/empleados_rutas.py` | Render de la pantalla, endpoints de autenticación y creación de la sesión. |
| `src/modulos/comandos_db/comandos_db_empleado.py` | Verificación de credenciales, hash de contraseña y persistencia de cuentas mediante `Usuario`. |
| `src/templates/iniciar_sesion.html` | Formularios HTML de inicio de sesión y registro. |
| `src/static/js/login.js` | Alternancia de pestañas, validación de confirmación y peticiones `fetch`. |
| `src/static/css/iniciar_sesion.css` | Estilos de la pantalla. |
| `src/config.py` y `src/app.py` | Configuración de rutas públicas y protección de rutas con sesión. |

## Rutas

| Método y ruta | Función | Descripción |
|---|---|---|
| `GET /iniciar_sesion` | `iniciar_sesion` | Renderiza la pantalla de autenticación. |
| `GET /registrarse` | `iniciar_sesion` | Alias de la misma pantalla. |
| `POST /api/iniciar_sesion` | `api_iniciar_sesion` | Autentica un usuario activo y crea la sesión. |
| `POST /api/registrarse` | `api_registrarse` | Crea una cuenta con rol predeterminado `Empleado`. |

Las rutas de autenticación están permitidas sin sesión por la lista `RUTAS_PUBLICAS` predeterminada en la configuración. Si se personaliza esa variable de entorno, debe mantenerse públicos el render de login/registro y ambos endpoints API para conservar este flujo.

## Interfaz

La plantilla presenta dos pestañas:

- **Iniciar sesión**: nombre de usuario, contraseña, opción **Recordar** y enlace **¿Olvidaste tu contraseña?**.
- **Crear usuario**: nombre de usuario, correo, teléfono, contraseña y confirmación.

`login.js` oculta un formulario y muestra el otro al cambiar de pestaña. El envío se intercepta en JavaScript y se realiza como JSON. Aunque los formularios tienen `method="post"`, el login especifica `action="/login"`, que no es una ruta implementada; sin JavaScript, el envío HTML tradicional no completa el proceso.

## Inicio de sesión

El cliente envía a `POST /api/iniciar_sesion` un JSON con esta forma:

```json
{
  "txt_input_nombre": "usuario",
  "password_input": "contraseña",
  "checkbox_recordar": "on"
}
```

El endpoint:

1. Comprueba disponibilidad de base de datos con `probar_conexion()`. Si falla, responde `500` con `Base de datos fuera de línea`.
2. Llama a `Usuario.verificar_credenciales(nombre, contraseña)`.
3. El método consulta un empleado con nombre exacto y `activo = 1`. Si lo encuentra, comprueba la contraseña con `werkzeug.security.check_password_hash`.
4. Si autentica, guarda `id_usuario`, `nombre_usuario` y `tipo` en la sesión y responde `200` con `exito: true` y `redireccion: "/"`.
5. Si no autentica, responde `401` con `Nombre de usuario o contraseña incorrectos`.

Un usuario desactivado no puede iniciar sesión. Las contraseñas se guardan como hash con `generate_password_hash`; no se almacenan en texto plano.

### Opción «Recordar»

La ruta interpreta como verdadero cualquier valor no vacío de `checkbox_recordar`, para establecer `session.permanent`. Sin embargo, el JavaScript envía `checkbox_recordar.value` en vez de su propiedad `checked`; por lo general envía `"on"` incluso si la casilla no está marcada. Por eso la opción puede no reflejar la selección real.

## Registro

El navegador compara la contraseña y su confirmación; si no coinciden, muestra una notificación y no envía la petición. Si coinciden, envía a `POST /api/registrarse`:

```json
{
  "input_nombre": "usuario",
  "txt_registro_email": "usuario@example.com",
  "tel_input": "1122334455",
  "password_registro": "contraseña"
}
```

El endpoint comprueba la conexión, verifica el nombre mediante `Usuario.existe_usuario(nombre)` y, si no encuentra coincidencia, crea `Usuario` con tipo predeterminado `Empleado`. `Usuario.crear_usuario()` genera el hash de la contraseña e inserta nombre, correo, teléfono, contraseña cifrada y tipo. La cuenta queda activa por el valor predeterminado de la tabla `empleado`.

Si crea la cuenta, responde `200` con `exito: true`, mensaje y `redireccion: "/iniciar_sesion"`. El flujo no inicia sesión automáticamente. Si el nombre ya existe, la ruta devuelve `400`; si falla la comprobación inicial de conexión o la inserción, devuelve `500`.

## Códigos HTTP y errores

| Código | Contexto |
|---:|---|
| `200` | Inicio de sesión correcto o registro completado. |
| `400` | El nombre de usuario ya existe. |
| `401` | Usuario/contraseña incorrectos o cuenta inactiva. |
| `500` | La comprobación inicial de conexión falla o el registro no se pudo guardar. |

El JavaScript muestra el mensaje de la API en caso de rechazo y un aviso genérico si ocurre un error de red. En el registro exitoso utiliza un `alert()` del navegador y luego redirige.

## Sesión y navegación

Al autenticarse, `src/app.py` conserva en la sesión el ID, el nombre y el tipo del usuario. El resto de las rutas protegidas exige `session["id_usuario"]`; las llamadas a rutas `/api/` sin sesión responden `401` JSON, mientras que las rutas de páginas redirigen al login. `GET /cerrar_sesion` limpia la sesión y redirige a `/iniciar_sesion`.

Después de un inicio de sesión correcto, el navegador va a `/`; para el contenido y las métricas de esa pantalla, consultar [pantalla_principal.md](./pantalla_principal.md).

## Consideraciones y limitaciones

- El nombre de usuario se verifica con una consulta previa, separada de la inserción. El SQL versionado no define una restricción única para `nombre_usuario`, por lo que altas concurrentes podrían superar el control.
- `Usuario.existe_usuario()` devuelve `False` tanto si el usuario no existe como si la consulta MySQL falla; en el segundo caso el registro puede continuar intentando insertar.
- No se validan explícitamente en backend la presencia/formato del nombre, correo o contraseña. La confirmación de contraseña se valida solo en JavaScript.
- El endpoint de registro es público y concede siempre el tipo `Empleado`; no existe en este flujo selección de rol, activación por administrador ni verificación de correo.
- El enlace de recuperación de contraseña apunta a `#`; no hay recuperación implementada.
- El checkbox **Recordar** envía el valor del control y no su estado marcado.
- La interfaz requiere JavaScript para evitar el envío del formulario a rutas HTML no implementadas.

Para la administración de cuentas, listado, edición y desactivación, consultar [empleados.md](./empleados.md).
