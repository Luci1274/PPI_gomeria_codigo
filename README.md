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

### SECCION VENTA

## Documentación técnica del módulo de ventas

El módulo de ventas del proyecto permite registrar transacciones, listar ventas, consultar detalle, filtrar por búsqueda y fecha, y anular ventas manteniendo el stock actualizado. La lógica principal se encuentra en `src/modulos/comandos_db/comandos_db_venta.py` y en `src/modulos/ventas_rutas.py`.

### 1. Funciones de base de datos (`comandos_db_venta.py`)

#### `sql_registrar_venta_completa(...)`
- Recibe: `id_cliente` (int | None), `id_empleado` (int), `lista_items` (list[dict]), `numero_factura` (str | None), `iva` (float), `descuento` (float), `precio_total` (float), `total_productos` (int).
- Devuelve: `int` con el ID de la venta generada si la transacción fue exitosa; `None` si ocurre un error y se ejecuta `rollback`.
- Funcionalidad:
  - Inserta la cabecera de la venta en la tabla `venta`.
  - Inserta cada ítem en `item_venta`.
  - Descuenta stock de productos desde `producto_servicio`.
  - Ejecuta todo dentro de una única transacción atómica.

#### `sql_leer_ventas(busqueda=None, filtro_fecha="hoy")`
- Recibe: `busqueda` (str | None) y `filtro_fecha` ("hoy", "semana", "mes", "anio").
- Devuelve: una `list[dict]` con las ventas filtradas o vacía (`[]`) si ocurre un error.
- Funcionalidad:
  - Busca por ID de venta, número de factura, nombre y apellido del cliente.
  - Filtra por rango de fecha según el valor recibido.
  - Ordena por fecha más reciente.

#### `sql_leer_venta(id_venta)`
- Recibe: `id_venta` (int).
- Devuelve: un `dict` con la cabecera de la venta y una lista embebida de ítems, o `None` si la venta no existe.
- Funcionalidad:
  - Obtiene datos principales de la venta y del cliente.
  - Consulta los productos asociados a la operación.
  - Arma la estructura completa usada por la vista de detalle.

#### `sql_anular_venta(id_venta)`
- Recibe: `id_venta` (int).
- Devuelve: `True` si anuló la venta y restituyó el stock; `False` si la venta no existe, ya estaba anulada o falló la operación SQL.
- Funcionalidad:
  - Verifica si la venta está activa.
  - Obtiene los productos vendidos.
  - Reintegra cantidades al stock en `producto_servicio`.
  - Actualiza `venta.activa = 0` para realizar la anulación lógica.

### 2. Estructura de diccionarios embebidos

La función `sql_leer_venta(id_venta)` devuelve una estructura del tipo:

```python
{
    "idventa": 15,
    "numero_factura": "F-000123",
    "fecha_emision_factura": "2026-08-16 14:30:00",
    "descuento": 10.0,
    "cantidad_total_productos": 3,
    "precio_total": 4500.0,
    "nombre_cliente": "Juan Pérez",
    "items": [
        {
            "iditem_venta": 101,
            "cantidad": 2,
            "precio_unitario": 2000.0,
            "subtotal": 4000.0,
            "producto_nombre": "Aceite Sintético",
            "imagen_url": "/static/img/aceite.jpg"
        },
        {
            "iditem_venta": 102,
            "cantidad": 1,
            "precio_unitario": 500.0,
            "subtotal": 500.0,
            "producto_nombre": "Filtro de Aire",
            "imagen_url": None
        }
    ]
}
```

Estructura del JSON que se recibe en `/api/ventas/procesar` desde el frontend:

```json
{
  "id_cliente": 1,
  "id_empleado": 4,
  "descuento": 10,
  "iva": 21,
  "numero_factura": "FC-0012",
  "carrito": [
    {
      "idproducto_servicio": 5,
      "precio_unitario": 1200.5,
      "cantidad": 2
    }
  ]
}
```

### 3. Endpoints API y vistas (`ventas_bp`)

| Ruta | Método | Espera | Devuelve | Estado HTTP |
|------|--------|--------|----------|-------------|
| `/ventas` | GET | Ninguno | HTML de `gestion_ventas.html` | 200 |
| `/api/ventas` | POST | JSON: `{"busqueda": str, "fecha": str}` | JSON: `{"listado_ventas": [...]}` | 200, 500 |
| `/venta/<id>/detalle` | GET | Parámetro de ruta: `id` | HTML de `detalle_venta.html` o redirect | 200, 302 |
| `/api/ventas/anular/<id_venta>` | POST | Parámetro de ruta: `id_venta` | JSON: `{"exito": bool, "mensaje": str}` | 200, 400, 500 |
| `/ventas/realizar` | GET | Ninguno | HTML de `realizar_venta.html` | 200 |
| `/api/ventas/procesar` | POST | JSON con datos de venta y carrito | JSON: `{"exito": bool, "id_venta": int}` | 201, 400, 500 |

#### Descripción funcional
- `vista_gestion_ventas()`: carga la pantalla principal de ventas y muestra alertas de productos con stock bajo.
- `api_filtrar_ventas()`: devuelve un listado de ventas según búsqueda y filtro de fecha.
- `vista_detalle_venta(id)`: recupera la información completa de una venta y la renderiza.
- `api_anular_venta(id_venta)`: anula de forma lógica la venta y devuelve mensaje de éxito o error.
- `vista_realizar_venta()`: carga la vista del carrito de venta para crear una nueva transacción.
- `api_procesar_venta()`: procesa el carrito enviado por el frontend y registra la venta completa.

### 4. Significado de códigos HTTP utilizados

- `200 OK`: la consulta o petición se procesó correctamente.
- `201 Created`: la venta fue creada correctamente y se asignó un nuevo ID en la base de datos.
- `302 Found`: se redirecciona a `/ventas` cuando la venta no existe o falla la conexión.
- `400 Bad Request`: error de validación del cliente, por ejemplo carrito vacío o intento de anular una venta inexistente/anulada.
- `500 Internal Server Error`: ocurrió una excepción no controlada en el servidor o falló una transacción SQL con rollback.

### 5. Consideraciones faltantes para tener en cuenta

- Arquitectura actual: el módulo de ventas está bien segmentado por rutas y consultas, pero aún conviene agregar validaciones de negocio más robustas para evitar inconsistencias de stock, cliente y facturación.
- Se recomienda implementar pruebas unitarias y de integración para los endpoints de ventas, asegurando que las transacciones sean atómicas y que los errores se manejen adecuadamente.
- Falta terminar la funcion de calcular precio total, se realizará una vez terminado el frontend de ventas, ya que se necesita la información del carrito para poder calcular el precio total de la venta.

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
