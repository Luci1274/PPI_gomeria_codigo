from flask import Blueprint, render_template, request, jsonify, session
from modulos.comandos_db.conexion import probar_conexion
from modulos.comandos_db.comandos_db_empleado import Usuario

empleados_bp = Blueprint("empleados", __name__)

# ------------------------------------------
# Iniciar Sesión                            #
# ------------------------------------------
@empleados_bp.route("/registrarse", methods=["GET"])
@empleados_bp.route("/iniciar_sesion", methods=["GET"])
def iniciar_sesion():
    return render_template("iniciar_sesion.html")


@empleados_bp.route("/api/iniciar_sesion", methods=["POST"])
def api_iniciar_sesion():
    if not probar_conexion():
        return jsonify({
            "exito": False,
            "mensaje": "Base de datos fuera de línea"
        }), 500

    datos = request.get_json(silent=True) or request.form
    nombre_usuario = datos.get("txt_input_nombre")
    contrasena = datos.get("password_input")

    datos_devueltos = Usuario.verificar_credenciales(nombre_usuario, contrasena)

    if datos_devueltos:
        session["id_usuario"] = datos_devueltos[0]
        session["nombre_usuario"] = datos_devueltos[2]
        session["tipo"] = datos_devueltos[1]
        return jsonify({
            "exito": True,
            "mensaje": "Inicio de sesión exitoso",
            "redireccion": "/index"
        }), 200
    
    return jsonify({
        "exito": False,
        "mensaje": "Nombre de usuario o contraseña incorrectos"
    }), 401


# ------------------------------------------
# Registro de Usuario                       #
# ------------------------------------------

@empleados_bp.route("/api/registrarse", methods=["POST"])
def api_registrarse():
    if not probar_conexion():
        return jsonify({
            "exito": False,
            "mensaje": "Base de datos fuera de línea"
        }), 500

    datos = request.get_json(silent=True) or request.form
    nombre = datos.get("input_nombre")
    correo = datos.get("txt_registro_email")
    telefono = datos.get("tel_input")
    contrasena = datos.get("password_registro")

    if Usuario.existe_usuario(nombre):
        return jsonify({
            "exito": False,
            "mensaje": "El usuario que intentó registrar ya existe, por favor ingrese otro"
        }), 400

    nuevo_usuario = Usuario(
        nombre=nombre,
        correo=correo,
        telefono=telefono,
        contrasena=contrasena
    )

    id_usuario = nuevo_usuario.crear_usuario()
    if id_usuario:
        return jsonify({
            "exito": True,
            "mensaje": "Registro exitoso",
            "redireccion": "/iniciar_sesion"
        }), 200
    
    return jsonify({
        "exito": False,
        "mensaje": "Error al registrar al usuario"
    }), 500


# ------------------------------------------
# Gestión / Listado de Empleados           #
# ------------------------------------------
@empleados_bp.route("/empleados", methods=["GET"])
def gestion_empleados():
    if not probar_conexion():
        return jsonify({
            "exito": False,
            "mensaje": "Base de datos fuera de línea"
        }), 500

    lista_empleados = Usuario.leer_usuarios()
    return render_template("gestion_empleados.html", empleados=lista_empleados)


# ------------------------------------------
# Edición de Empleados                      #
# ------------------------------------------
@empleados_bp.route("/empleados/modificar/<int:id>", methods=["GET"])
def modificar_usuario(id):
    if not probar_conexion():
        return jsonify({
            "exito": False,
            "mensaje": "Base de datos fuera de línea",
            "redireccion": "/empleados"
        }), 500

    datos_usuario = Usuario.leer_usuario(id)
    if datos_usuario:
        return render_template(
            "editar_usuario.html",
            id_usuario=datos_usuario.get("idempleado"),
            nombre=datos_usuario.get("nombre_usuario"),
            mail=datos_usuario.get("mail"),
            telefono=datos_usuario.get("telefono"),
            tipo=datos_usuario.get("tipo")
        )

    return jsonify({
        "exito": False,
        "mensaje": "Hubo un error al intentar obtener los datos del empleado",
        "redireccion": "/empleados"
    }), 404


@empleados_bp.route("/api/empleados/modificar/<int:id>", methods=["POST"])
def api_modificar_usuario(id):
    datos = request.get_json(silent=True) or request.form
    nombre = datos.get("nombre_usuario")
    correo = datos.get("mail_usuario")
    telefono = datos.get("telefono_usuario")
    contrasena = datos.get("contrasena_usuario", None)
    tipo = datos.get("tipo", "Empleado")

    usuario_modificado = Usuario(
        id_usuario=id,
        nombre=nombre,
        correo=correo,
        telefono=telefono,
        tipo=tipo
    )

    if usuario_modificado.actualizar_usuario(nueva_contrasena=contrasena):
        return jsonify({
            "exito": True,
            "mensaje": "Empleado actualizado con éxito",
            "redireccion": "/empleados"
        }), 200

    return jsonify({
        "exito": False,
        "mensaje": "Ha ocurrido un error al modificar al empleado",
        "redireccion": "/empleados"
    }), 500


# ------------------------------------------
# Baja Lógica de Empleado                   #
# ------------------------------------------
@empleados_bp.route("/api/empleados/eliminar/<int:id>", methods=["POST"])
def api_eliminar_usuario(id):
    """Realiza la baja lógica (activo = 0) del empleado."""
    if not probar_conexion():
        return jsonify({
            "exito": False,
            "mensaje": "Base de datos fuera de línea"
        }), 500

    if Usuario.eliminar_usuario(id):
        return jsonify({
            "exito": True,
            "mensaje": f"El empleado #{id} fue dado de baja correctamente.",
            "redireccion": "/empleados"
        }), 200

    return jsonify({
        "exito": False,
        "mensaje": "No se pudo dar de baja al empleado indicado."
    }), 400