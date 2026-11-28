# Tecnologías utilizadas y justificación

Este documento describe las tecnologías que aparecen en el código o en el flujo de desarrollo y por qué se usan. El resumen para iniciar con el proyecto está en el [README](../README.md); las dependencias Python instalables se mantienen en [`requirements.txt`](../requirements.txt).

## Aplicación y persistencia

| Tecnología | Uso en el proyecto | Justificación |
|---|---|---|
| **Python 3** | Implementa las rutas, validaciones, reglas de negocio y acceso a datos del servidor. | Permite organizar la lógica del sistema en módulos y aprovechar el ecosistema Flask y sus bibliotecas. |
| **Flask** | Crea la aplicación web, registra rutas y blueprints, renderiza plantillas y administra las sesiones. | Es el framework que utiliza actualmente el proyecto y ofrece una estructura ligera para integrar sus módulos. |
| **Jinja** | Genera HTML desde las plantillas y presenta datos de sesión, páginas y permisos. | Permite reutilizar estructuras de interfaz y renderizar contenido del servidor sin construir las páginas manualmente. Viene integrado con Flask. |
| **MySQL** | Guarda clientes, empleados, proveedores, productos, compras, ventas y sus detalles relacionados. | El modelo es relacional: necesita claves, restricciones e integridad transaccional para asociar las operaciones comerciales. El esquema está orientado a MySQL 8. |
| **PyMySQL** | Driver que conecta Python con MySQL; las capas `comandos_db` ejecutan consultas SQL parametrizadas. | Permite acceder a la base de datos desde Python sin incorporar un ORM al flujo actual. |
| **DBUtils (`PooledDB`)** | Mantiene y entrega conexiones reutilizables a través de `Config.conectar_db()`. | Evita crear una conexión independiente para cada solicitud y limita la cantidad de conexiones simultáneas. |
| **python-dotenv** | Carga variables desde `src/.env` al iniciar la configuración. | Mantiene credenciales y opciones locales fuera del código fuente; el archivo real no debe compartirse ni versionarse. |
| **Werkzeug Security** | Genera y verifica hashes de contraseñas de empleados. | Permite almacenar hashes en lugar de contraseñas en texto plano y comprobarlas con las funciones de seguridad de Werkzeug. |

El acceso a datos se implementa con SQL directo y PyMySQL; el proyecto no usa SQLAlchemy actualmente. Las consultas y restricciones principales se describen en la [documentación del modelo de datos](documentacion/sistema_y_base_de_datos.md).

## Interfaz web

| Tecnología | Uso en el proyecto | Justificación |
|---|---|---|
| **HTML5** | Estructura las páginas de inicio de sesión, dashboard y módulos de gestión. | Proporciona los formularios, tablas, controles y regiones de la interfaz. |
| **CSS3** | Define estilos, distribución y comportamiento adaptable de las pantallas. | Separa la presentación visual de la estructura y permite adaptar la interfaz a distintos tamaños. |
| **JavaScript** | Realiza solicitudes `fetch`, administra formularios, filtros, paginación, modales y actualizaciones del dashboard. | Permite actualizar las pantallas con respuestas JSON sin recargar cada página completa. |
| **Font Awesome** | Proporciona iconos cargados desde CDN en las plantillas. | Mantiene una iconografía consistente sin incluir archivos de iconos propios. |
| **intl-tel-input** | Mejora la entrada del teléfono durante el registro y genera números con prefijo internacional. | Facilita capturar teléfonos en formato internacional para la recuperación de contraseña. |
| **html2canvas y jsPDF** | Se cargan desde CDN en las páginas de ventas y compras para preparar y descargar resúmenes en PDF. | Permiten exportar la vista de una orden o venta desde el navegador. |

Las bibliotecas de interfaz mencionadas se incluyen mediante CDN en las plantillas; no son paquetes Python ni forman parte de `requirements.txt`.

## Servicios externos

| Tecnología | Uso en el proyecto | Justificación |
|---|---|---|
| **Cloudinary** | Recibe imágenes de productos desde [`api_claudinary.py`](../src/modulos/api_claudinary.py) y devuelve su URL segura. La carga solicita una imagen de hasta 600 × 600, recorte `fill`, calidad y formato automáticos, y eliminación de metadatos de perfil. | Centraliza el almacenamiento y la transformación de imágenes fuera del servidor Flask. |
| **Twilio** | [`notificaciones.py`](../src/modulos/servicios/notificaciones.py) envía por SMS el código temporal de recuperación cuando el usuario aporta un teléfono. | Utiliza un proveedor de mensajería externo para entregar códigos de un solo uso. |
| **Gmail SMTP** | [`notificaciones.py`](../src/modulos/servicios/notificaciones.py) envía por correo el código de recuperación cuando el usuario aporta una dirección de email; la conexión SMTP inicia TLS. | Aprovecha el correo como canal alternativo de recuperación de cuentas. |

Cloudinary, Twilio y Gmail requieren las variables de entorno indicadas en [`sistema_y_base_de_datos.md`](documentacion/sistema_y_base_de_datos.md). La disponibilidad de estos servicios externos depende de las credenciales y de la conexión de red.

## Ejecución y herramientas de desarrollo

| Tecnología | Uso en el proyecto | Justificación |
|---|---|---|
| **pip y `requirements.txt`** | Instalan las dependencias Python declaradas para la aplicación. | Permiten preparar el entorno de desarrollo y repetir la instalación en otros equipos. |
| **Gunicorn** | Servidor WSGI opcional para ejecutar Flask en despliegues compatibles; el requisito se omite en Windows. | Está destinado a ejecutar la aplicación fuera del servidor de desarrollo integrado de Flask. |
| **Git y GitHub** | Control de versiones y alojamiento del repositorio. | Permiten registrar cambios y colaborar sobre el proyecto. |
| **Visual Studio Code** | Editor y entorno de desarrollo utilizado para trabajar con el código. | Reúne edición, terminal, depuración y navegación del proyecto. |
| **MySQL Workbench** | Herramienta gráfica opcional para explorar el esquema y administrar una instancia MySQL. | Facilita revisar tablas y relaciones; no es necesaria para ejecutar Flask. |

El inicio local usa `python src\app.py` y el servidor integrado de Flask en modo debug. Ese modo es para desarrollo; Gunicorn se instala solo fuera de Windows mediante el marcador de plataforma del archivo de dependencias.
