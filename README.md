# PPI_gomeria_codigo

## Tecnologias a utilizar 

### Frontend
| Tecnologias | Uso | Definicion |
|-------------|-----|------------|
| HTML5 | El uso que le daríamos sería la estructura de la aplicación web | Es un lenguaje de marcado para estructurar el contenido de una página web |
| CSS3 | Diseño y presentación de la aplicación | Lenguaje de estilo para dar formato a las páginas web |
| JavaScript | Interactividad y lógica del lado del cliente | Lenguaje de programación para crear páginas web dinámicas e interactivas |

### Backend
| Tecnologias | Uso | Definicion |
|-------------|-----|------------|
| Python | Lógica del lado del servidor y manejo de datos | Lenguaje de programación fácil de leer y usar, muy popular para desarrollo web, automatización, ciencia de datos e inteligencia artificial |
| Flask | Framework para crear aplicaciones web de forma simple y rápida | Framework (herramienta) de Python para crear aplicaciones web de forma simple y rápida. Es liviano y flexible. |

### Diferencia entre FastAPI y Flask

| Característica | FastAPI | Flask |
|----------------|---------|-------|
| Rendimiento | Alto rendimiento gracias a su uso de ASGI y Pydantic. | Rendimiento adecuado para aplicaciones pequeñas y medianas. |
| Facilidad de uso | Fácil de usar con una sintaxis clara y concisa. | Fácil de usar, pero puede requerir más configuración para aplicaciones complejas. |
| Validación de datos | Utiliza Pydantic para la validación de datos, lo que facilita la gestión de datos y errores. | No tiene una solución integrada para la validación de datos, lo que puede requerir bibliotecas adicionales. |
| Documentación automática | Genera documentación automática de la API utilizando OpenAPI y Swagger. | No tiene soporte integrado para la documentación automática, aunque se pueden usar extensiones como Flask-RESTful. |
| Comunidad y ecosistema | Comunidad en crecimiento con una amplia gama de extensiones y herramientas. | Comunidad establecida con una gran cantidad de extensiones y recursos disponibles. |
|Rendimiento en aplicaciones| Excelente para aplicaciones de alto rendimiento y en tiempo real. | Adecuado para aplicaciones pequeñas y medianas, pero puede no ser ideal para aplicaciones de alto rendimiento. |

### Base de datos
| Tecnologias | Uso | Definicion |
|-------------|-----|------------|
| MYSQL | Almacenamiento y gestión de datos | Sistema de gestión de bases de datos relacional que permite almacenar, organizar y consultar información de manera eficiente. |
| MYSQL Workbench | Diseño y administración de la base de datos | Herramienta gráfica para trabajar con bases de datos MySQL, que permite diseñar, modelar y administrar la base de datos de manera visual y eficiente. |

### Control de versiones
| Tecnologias | Uso | Definicion |
|-------------|-----|------------|
| Git | Control de versiones y colaboración en el desarrollo del proyecto | Sistema de control de versiones que permite guardar cambios en el código, volver a versiones anteriores y trabajar en equipo sin perder información. |
| GitHub | Alojamiento del repositorio del proyecto y colaboración entre los miembros del equipo | Plataforma online basada en Git donde podés subir tus proyectos, compartirlos, colaborar con otros y gestionar versiones de forma remota. |


### Herramientas de desarrollo
| Tecnologias | Uso | Definicion |
|-------------|-----|------------|
| Visual Studio Code | Edición de código y desarrollo de la aplicación | Editor de código fuente desarrollado por Microsoft. Es liviano, gratuito y muy popular para programar en distintos lenguajes como Python, JavaScript y HTML. Permite usar extensiones, depurar código y trabajar con herramientas como Git. |

### Librerias 
| Tecnologias | Uso | Definicion |
|-------------|-----|------------|
| Request | Utilizacion para las peticiones http post y get a las Apis. | Es una librería de Python que se utiliza para realizar solicitudes HTTP a servidores, permitiendo enviar y recibir datos desde APIs o páginas web de forma sencilla.|

## Dependencias

### Frontend
- HTML: Para estructurar el contenido de la página web
- CSS: Para definir el diseño y la apariencia visual.
- JavaScript: Para agregar interactividad y comportamientos dinámicos.

### Backend
- Flask: Para desarrollar el backend de la aplicación web

### Instalación
- Para instalar las dependencias necesarias, puedes usar pip:

### SECCIÓN VENTA

## Documentación técnica del módulo de ventas

Aquí tienes la documentación técnica completa y actualizada del módulo de ventas, adaptada a la clase `Venta` y a los nuevos formatos de respuesta JSON con redirección.

### Códigos de estado HTTP utilizados

| Código | Significado | Contexto de uso |
|--------|-------------|----------------|
| 200 OK | Solicitud exitosa | Consulta de datos o anulación correcta de una venta. |
| 201 Created | Recurso creado exitosamente | Procesamiento y registro exitoso de una nueva venta. |
| 400 Bad Request | Petición inválida | Carrito vacío, datos faltantes o intento de anular una venta inexistente/ya anulada. |
| 401 Unauthorized | No autorizado | Intento de procesar una venta sin `session["usuario"]` activa. |
| 404 Not Found | No encontrado | Búsqueda de una venta por ID que no existe en la base de datos. |
| 500 Internal Error | Error interno del servidor | Fallo de conexión con MySQL o excepción no controlada en el backend. |

### Clase `Venta` (Capa de Base de Datos / Repositorio)

#### 1. `Venta.registrar(...)`

Descripción: Ejecuta una transacción SQL para validar stock, registrar la cabecera de la venta, insertar los ítems y descontar el inventario de productos.

Recibe:
- `id_cliente` (int | None)
- `id_empleado` (int)
- `lista_items` (list[dict]): ejemplo `[{"idproducto_servicio": 1, "cantidad": 2, "precio_unitario": 100.0}]`
- `numero_factura` (str | None, opcional)
- `iva` (int | float, por defecto 21)
- `descuento` (float, por defecto 0)
- `precio_total` (float)
- `total_productos` (int)

Devuelve: `int` (ID de la venta generada) si es exitoso, o `None` en caso de falla o stock insuficiente.

#### 2. `Venta.obtener_todas(busqueda=None, filtro_fecha="hoy")`

Descripción: Consulta el listado general de ventas activas aplicando filtros por término y/o rango de fecha.

Recibe:
- `busqueda` (str | None)
- `filtro_fecha` (str: `"hoy"`, `"semana"`, `"mes"`, `"anio"`)

Devuelve: `list[dict]` (lista de diccionarios con el resumen de cada venta).

#### 3. `Venta.obtener_por_id(id_venta)`

Descripción: Obtiene los datos de la cabecera de la venta e incrusta la lista de productos asociados.

Recibe:
- `id_venta` (int)

Devuelve: `dict` (estructura embebida) o `None` si no existe:

```json
{
  "idventa": 10,
  "numero_factura": "F-001",
  "fecha_emision_factura": "2026-08-28 14:00:00",
  "descuento": 0.0,
  "cantidad_total_productos": 3,
  "precio_total": 1500.0,
  "nombre_cliente": "Juan Pérez",
  "items": [
    {
      "id_item_venta": 1,
      "cantidad": 2,
      "precio_unitario": 500.0,
      "subtotal": 1000.0,
      "producto_nombre": "Aceite 1L",
      "imagen_producto": "aceite.jpg"
    }
  ]
}
```

#### 4. `Venta.anular(id_venta)`

Descripción: Anula la venta de forma lógica (`activa = 0`) y devuelve las cantidades al inventario (`cantidad_actual`).

Recibe:
- `id_venta` (int)

Devuelve: `bool` (`True` si se anuló correctamente, `False` si falló o ya estaba anulada).

### Rutas de Flask (`ventas_bp`)

#### 1. `GET /ventas` (`vista_gestion_ventas`)

Recibe: petición HTTP GET limpia.

Devuelve: HTML renderizado (`gestion_ventas.html`) o JSON en caso de error de conexión:

```json
{
  "exito": false,
  "mensaje": "Error: No se pudo conectar a la base de datos.",
  "redireccion": "/index"
}
```

Estado HTTP: `500`.

#### 2. `POST /api/ventas` (`api_filtrar_ventas`)

Recibe JSON:

```json
{
  "busqueda": "Juan",
  "fecha": "semana"
}
```

Devuelve JSON (`HTTP 200`):

```json
{
  "exito": true,
  "listado_ventas": [
    /* Lista de ventas */
  ]
}
```

#### 3. `GET /venta/<int:id>/detalle` (`vista_detalle_venta`)

Recibe: parámetro de URL `id` (int).

Devuelve: render de `detalle_venta.html` o JSON de error si no la encuentra:

```json
{
  "exito": false,
  "mensaje": "Error: No se encontró la venta con ID 10.",
  "redireccion": "/ventas"
}
```

Estado HTTP: `404`.

#### 4. `POST /api/ventas/anular/<int:id_venta>` (`api_anular_venta`)

Recibe: parámetro de URL `id_venta` (int).

Devuelve JSON (`HTTP 200 / 400 / 500`):

```json
{
  "exito": true,
  "mensaje": "La venta #10 fue anulada y el stock restituido.",
  "redireccion": "/ventas"
}
```

#### 5. `POST /api/ventas/procesar` (`api_procesar_venta`)

Recibe:
- Sesión: `session["usuario"]` (contiene el ID del empleado).
- JSON body:

```json
{
  "id_cliente": 5,
  "numero_factura": "F-1002",
  "descuento": 0.0,
  "carrito": [
    {"idproducto_servicio": 1, "cantidad": 2, "precio_unitario": 250.0}
  ]
}
```

Devuelve JSON (`HTTP 201 Created`):

```json
{
  "exito": true,
  "mensaje": "Venta #15 realizada con éxito.",
  "id_venta": 15,
  "redireccion": "/ventas"
}
```

### Detalles importantes y consideraciones

- Manejo de sesión expirada: si `session["usuario"]` no existe al intentar procesar una venta, la API responde con un código `401` y redirige a `/login`.
- Cálculos en servidor: las funciones auxiliares `calcular_total_productos` y `calcular_precio_total` convierten activamente los valores a `int` y `float` para evitar errores si el cliente envía cadenas de texto numéricas.
- Integridad de stock: la verificación de stock disponible en `Venta.registrar` discrimina por la columna `tipo = 'producto'`, evitando bloqueos si la venta incluye servicios.

### SECCIÓN EMPLEADOS

## Documentación técnica del módulo de empleados y autenticación

Aquí tienes la documentación técnica actualizada para el módulo de empleados y autenticación, reflejando el código refactorizado y corregido.

### Códigos de estado HTTP utilizados

| Código | Significado | Contexto de uso |
|--------|-------------|----------------|
| 200 OK | Solicitud exitosa | Inicio de sesión correcto, creación, edición o baja lógica procesada sin fallos. |
| 400 Bad Request | Petición inválida | Intento de registrar un usuario con un nombre ya existente o error en parámetros. |
| 401 Unauthorized | No autorizado | Credenciales (usuario o contraseña) incorrectas al intentar iniciar sesión. |
| 404 Not Found | No encontrado | Consulta de datos para modificar un empleado cuyo ID no existe en la BD. |
| 500 Internal Error | Error interno del servidor | Base de datos fuera de línea o excepción no controlada en las consultas SQL. |

### Clase `Usuario` (Capa de Base de Datos / Repositorio)

#### 1. `Usuario.__init__(nombre=None, correo=None, telefono=None, contrasena=None, tipo="Empleado", id_usuario=None)`

Descripción: Constructor de la clase. Inicializa un objeto `Usuario` con atributos privados.

Recibe: parámetros opcionales con nombre (`str`, `int`).

Devuelve: objeto de instancia `Usuario`.

#### 2. `Usuario.hash_contraseña(contraseña)`

Descripción: Convierte una clave en texto plano a un hash seguro con Werkzeug.

Recibe: `contraseña` (`str`).

Devuelve: `str` (cadena hash procesada).

#### 3. `Usuario.verificar_credenciales(nombre_ingresado, contrasena_ingresada)`

Descripción: Comprueba si el usuario existe y coincide con la contraseña guardada en la BD.

Recibe:
- `nombre_ingresado` (`str`)
- `contrasena_ingresada` (`str`)

Devuelve: `list` -> `[idempleado (int), tipo (str)]` si la validación es correcta. Devuelve `None` si las credenciales fallan o `False` si hay error de SQL.

#### 4. `Usuario.crear_usuario()`

Descripción: Inserta un nuevo empleado en la base de datos con su contraseña encriptada.

Recibe: lee los atributos de la instancia actual (`self`).

Devuelve: `int` (ID asignado en la BD) o `None` en caso de error.

#### 5. `Usuario.existe_usuario(nombre_usuario)` (alias: `no_repetir`)

Descripción: Verifica la disponibilidad de un nombre de usuario en la BD.

Recibe: `nombre_usuario` (`str`).

Devuelve: `bool` (`True` si ya existe, `False` si está libre o falla la consulta).

#### 6. `Usuario.leer_usuarios()`

Descripción: Obtiene todos los empleados con estado activo (`activo = 1`).

Recibe: ninguno.

Devuelve: `list[dict]` con la lista de usuarios.

```json
[
  {
    "idempleado": 1,
    "nombre_usuario": "admin",
    "mail": "admin@empresa.com",
    "telefono": "341123456",
    "tipo": "Administrador"
  }
]
```

#### 7. `Usuario.leer_usuario(id_usuario)`

Descripción: Busca y devuelve los datos de un único empleado por su ID.

Recibe: `id_usuario` (`int`).

Devuelve: `dict` (con llaves `idempleado`, `nombre_usuario`, `mail`, `telefono`, `tipo`) o `None` si no existe.

#### 8. `Usuario.actualizar_usuario(nueva_contrasena=None)`

Descripción: Actualiza los datos del empleado. Si recibe `nueva_contrasena`, actualiza el hash de la clave.

Recibe: `nueva_contrasena` (`str | None`, opcional).

Devuelve: `bool` (`True` en éxito, `False` en falla).

#### 9. `Usuario.eliminar_usuario(id_usuario)`

Descripción: Ejecuta una baja lógica cambiando `activo = 0`.

Recibe: `id_usuario` (`int`).

Devuelve: `bool` (`True` si se ejecutó la baja, `False` en error).

### Rutas de Flask (`empleados_bp`)

#### 1. `GET /iniciar_sesion` (`iniciar_sesion`)

Recibe: petición HTTP GET.

Devuelve: HTML renderizado (`iniciar_sesion.html`).

#### 2. `POST /api/iniciar_sesion` (`api_iniciar_sesion`)

Recibe body (`JSON` o `Form`):

```json
{
  "nombre_usuario": "admin",
  "contrasena": "1234"
}
```

Efecto en sesión: establece `session["usuario"]` y `session["tipo"]`.

Devuelve JSON (`HTTP 200 / 401 / 500`):

```json
{
  "exito": true,
  "mensaje": "Inicio de sesión exitoso",
  "redireccion": "/index"
}
```

#### 3. `GET /registrarse` (`registrarse`)

Recibe: petición HTTP GET.

Devuelve: HTML renderizado (`crear_usuario.html`).

#### 4. `POST /api/registrarse` (`api_registrarse`)

Recibe body (`JSON` o `Form`):

```json
{
  "nombre_usuario": "pedro",
  "mail_usuario": "pedro@mail.com",
  "telefono_usuario": "443322",
  "contrasena_usuario": "pass123"
}
```

Devuelve JSON (`HTTP 200 / 400 / 500`):

```json
{
  "exito": true,
  "mensaje": "Registro exitoso",
  "redireccion": "/iniciar_sesion"
}
```

#### 5. `GET /empleados` (`gestion_empleados`)

Recibe: petición HTTP GET.

Devuelve: HTML renderizado (`gestion_empleados.html`) pasando la variable `empleados` (`list[dict]`).

#### 6. `GET /empleados/modificar/<int:id>` (`modificar_usuario`)

Recibe: parámetro de URL `id` (`int`).

Devuelve: HTML renderizado (`editar_usuario.html`) con variables individuales (`id_usuario`, `nombre`, `mail`, `telefono`, `tipo`) o JSON de error (`HTTP 404 / 500`).

#### 7. `POST /api/empleados/modificar/<int:id>` (`api_modificar_usuario`)

Recibe:
- parámetro `id` (`int`)
- body:

```json
{
  "nombre_usuario": "pedro_edit",
  "mail_usuario": "p@mail.com",
  "telefono_usuario": "123",
  "contrasena_usuario": "",
  "tipo": "Empleado"
}
```

Devuelve JSON (`HTTP 200 / 500`):

```json
{
  "exito": true,
  "mensaje": "Empleado actualizado con éxito",
  "redireccion": "/empleados"
}
```

#### 8. `POST /api/empleados/eliminar/<int:id>` (`api_eliminar_usuario`)

Recibe: parámetro de URL `id` (`int`).

Devuelve JSON (`HTTP 200 / 400 / 500`):

```json
{
  "exito": true,
  "mensaje": "El empleado #5 fue dado de baja correctamente.",
  "redireccion": "/empleados"
}
```

## Esquema de archivos

```text
PPI_gomeria_codigo/
├── README.md
├── docs/
│   ├── comandos_creacion_db.sql
│   ├── Dependencias.md
│   ├── Tecnologias.md
│   ├── modelo_esquema_gomeria.mwb
│   ├── modelo_esquema_gomeria.mwb.bak
│   └── 01_Diagrama_arquitectura_web/
│       └── Diagrama_arquitectura.puml
├── src/
│   ├── app.py
│   ├── requirements.txt
│   ├── modulos/
│   │   ├── __init__.py
│   │   ├── api_claudinary.py
│   │   ├── compras_rutas.py
│   │   ├── empleados_rutas.py
│   │   ├── inventario_rutas.py
│   │   ├── ventas_rutas.py
│   │   ├── comandos_db/
│   │   │   ├── __init__.py
│   │   │   ├── conexion.py
│   │   │   ├── comandos_db_clientes.py
│   │   │   ├── comandos_db_compra.py
│   │   │   ├── comandos_db_empleado.py
│   │   │   ├── comandos_db_productos.py
│   │   │   ├── comandos_db_proveedores.py
│   │   │   ├── comandos_db_venta.py
│   │   │   └── comandos_db_venta.py
│   ├── static/
│   │   ├── css/
│   │   │   ├── estructura_base_compra_inventario_venta.css
│   │   │   ├── gestion.css
│   │   │   ├── iniciar_sesion.css
│   │   │   ├── resumen_orden_compra.css
│   │   │   └── style.css
│   │   ├── image/
│   │   └── js/
│   │       ├── barral_navegacion.js
│   │       ├── estructura_base_compra_inventario_venta.js
│   │       └── script.js
│   └── templates/
│       ├── crear_usuario.html
│       ├── estructura_base_compra_inventario_venta.html
│       ├── gestion_clientes.html
│       ├── gestion_venta.html
│       ├── index.html
│       ├── iniciar_sesion.html
│       ├── plantilla_base_gestion.html
│       ├── resumen_orden_compra.html
│       └── componentes/
│           ├── filtro.html
│           ├── header.html
│           └── navbar.html
└── .gitignore
```

> Nota: el esquema anterior refleja la estructura general del proyecto. En el módulo de ventas, el punto de entrada clave es `src/modulos/ventas_rutas.py`, mientras que la lógica de acceso a datos se centraliza en `src/modulos/comandos_db/comandos_db_venta.py`.
