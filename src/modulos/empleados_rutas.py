import math
from flask import Blueprint, render_template, request, jsonify, session, redirect
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
    recordar = datos.get("checkbox_recordar")

    datos_devueltos = Usuario.verificar_credenciales(nombre_usuario, contrasena)

    if datos_devueltos:
        session["id_usuario"] = datos_devueltos[0]
        session["nombre_usuario"] = datos_devueltos[2]
        session["tipo"] = datos_devueltos[1]
        if recordar:
            session.permanent = True
        else:
            session.permanent = False
        return jsonify({
            "exito": True,
            "mensaje": "Inicio de sesión exitoso",
            "redireccion": "/"
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
    """Renderiza la vista HTML principal. Los datos de la tabla se cargan vía JavaScript."""
    return render_template("empleados.html")


# ------------------------------------------
# API: Obtener Empleados (Paginación + Buscador)
# ------------------------------------------
@empleados_bp.route("/api/empleados", methods=["GET"])
def api_obtener_empleados():
    if not probar_conexion():
        return (
            jsonify({"exito": False, "mensaje": "Base de datos fuera de línea"}),
            500,
        )

    pagina = request.args.get("pagina", 1, type=int)
    buscar = request.args.get("buscar", None, type=str)
    por_pagina = 10

    total_items, empleados, roles, ok = Usuario.leer_empleados(
        pagina=pagina, por_pagina=por_pagina, buscar=buscar
    )

    if not ok:
        return (
            jsonify(
                {"exito": False, "mensaje": "Error al obtener los empleados."}
            ),
            500,
        )

    total_paginas = (
        math.ceil(total_items / por_pagina) if total_items > 0 else 1
    )

    return (
        jsonify(
            {
                "exito": True,
                "total_items": total_items,
                "total_paginas": total_paginas,
                "limite": por_pagina,
                "empleados": empleados,
            }
        ),
        200,
    )


# # ------------------------------------------
# # API: Registrar Nuevo Empleado En gestion             #
# # ------------------------------------------
# @empleados_bp.route("/api/empleados/crear", methods=["POST"])
# def api_crear_empleado():
#     if not probar_conexion():
#         return (
#             jsonify({"exito": False, "mensaje": "Base de datos fuera de línea"}),
#             500,
#         )

#     datos = request.get_json(silent=True) or request.form
#     nombre = datos.get("nombre")
#     email = datos.get("email")
#     telefono = datos.get("telefono")
#     rol = datos.get("rol", "Empleado")

#     if not nombre or not email:
#         return (
#             jsonify(
#                 {
#                     "exito": False,
#                     "mensaje": "El nombre y el email son campos obligatorios.",
#                 }
#             ),
#             400,
#         )

#     if Usuario.crear_empleado(nombre, email, telefono, rol):
#         return (
#             jsonify(
#                 {"exito": True, "mensaje": "Empleado registrado correctamente."}
#             ),
#             201,
#         )

#     return (
#         jsonify({"exito": False, "mensaje": "No se pudo crear el empleado."}),
#         500,
#     )


# ------------------------------------------
# API: Obtener datos de un Empleado         #
# ------------------------------------------
@empleados_bp.route("/api/empleados/<int:id>/editar", methods=["GET"])
def api_obtener_empleado(id):
    if not probar_conexion():
        return (
            jsonify({"exito": False, "mensaje": "Base de datos fuera de línea"}),
            500,
        )

    empleado, ok = Usuario.leer_empleado(id)

    if ok and empleado:
        return jsonify({"exito": True, "empleado": empleado}), 200

    return (
        jsonify({"exito": False, "mensaje": "Empleado no encontrado."}),
        404,
    )


# ------------------------------------------
# API: Modificar Empleado                   #
# ------------------------------------------
@empleados_bp.route("/api/empleados/<int:id>/editar", methods=["POST"])
def api_modificar_empleado(id):
    if not probar_conexion():
        return (
            jsonify({"exito": False, "mensaje": "Base de datos fuera de línea"}),
            500,
        )

    datos = request.get_json(silent=True) or request.form
    nombre = datos.get("nombre")
    email = datos.get("email")
    telefono = datos.get("telefono")
    rol = datos.get("rol", "Empleado")

    if Usuario.modificar_empleado(id, nombre, email, telefono, rol):
        return (
            jsonify({"exito": True, "mensaje": "Datos actualizados con éxito."}),
            200,
        )

    return (
        jsonify(
            {
                "exito": False,
                "mensaje": "Ha ocurrido un error al modificar el empleado.",
            }
        ),
        500,
    )


# ------------------------------------------
# API: Baja Lógica de Empleado              #
# ------------------------------------------
@empleados_bp.route("/api/empleados/<int:id>/desactivar", methods=["POST"])
def api_desactivar_empleado(id):
    if not probar_conexion():
        return (
            jsonify({"exito": False, "mensaje": "Base de datos fuera de línea"}),
            500,
        )

    if Usuario.eliminar_empleado(id):
        return (
            jsonify(
                {
                    "exito": True,
                    "mensaje": f"El empleado fue desactivado correctamente.",
                }
            ),
            200,
        )

    return (
        jsonify(
            {
                "exito": False,
                "mensaje": "No se pudo dar de baja al empleado indicado.",
            }
        ),
        400,
    )


# ------------------------------------------
# Cierre de Sesión                          #
# ------------------------------------------
@empleados_bp.route("/cerrar_sesion")
def cerrar_sesion():
    session.clear()
    return redirect("/iniciar_sesion")