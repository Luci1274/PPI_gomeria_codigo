from flask import Blueprint, render_template, request, jsonify, flash, redirect, session
from modulos.comandos_db.conexion import probar_conexion
from modulos.comandos_db.comandos_db_empleado import Usuario

empleados_bp = Blueprint("empleados", __name__)

"""Inicializar la pantalla de iniciar sesion"""
@empleados_bp.route("/iniciar_sesion", methods=["GET"])
def iniciar_sesion():
    return render_template("iniciar_sesion.html")

"""Funcionalidad backend y envio json al front"""
@empleados_bp.route("/api/iniciar_sesion", methods=["POST"])
def api_iniciar_sesion():
    """Primero verificamos que la DB esté conectada"""
    if not probar_conexion():
        return jsonify ({
            "exito": False,
            "mensaje": f"Base de datos fuera de linea"
        }), 500
        
    datos = request.get_json(silent=True) or request.form
    nombre_usuario = datos.get("nombre_usuario")
    contrasena = datos.get("contrasena")
    usuario = Usuario()
    datos_devueltos = usuario.verificar_credenciales(
        nombre_usuario, contrasena)
    
    if datos_devueltos:
        id_usuario = datos_devueltos[0]
        tipo_usuario = datos_devueltos[1]
        session["usuario"] = id_usuario
        session["tipo"] = tipo_usuario
        return jsonify({
            "exito": True,
            "mensaje": f"Inicio de sesion exitoso",
            "redireccion": "/index"
        }), 200
    else:
        return jsonify ({
            "exito": False,
            "mensaje": f"Nombre de usuario u contraseña incorrecta",
        }), 401

"""Inicializa el registro de usuario"""
@empleados_bp.route("/registrarse", methods = ["GET"])
def registrarse():
    return render_template("crear_usuario.html")

"""Funcionalidad backend y envio json al front"""
@empleados_bp.route("/api/registrarse", methods = ["POST"])
def api_registrarse():
    if not probar_conexion():
        return jsonify ({
                    "exito": False,
                    "mensaje": f"Base de datos fuera de linea"
                }), 500
    datos = request.get_json(silent=True) or request.form  
    nombre = datos.get("nombre_usuario")
    correo = datos.get("mail_usuario")
    telefono = datos.get("telefono_usuario")
    contrasena = datos.get("contrasena_usuario")  
    
    if Usuario().no_repetir(nombre):
        return jsonify({
            "exito": False,
            "mensaje": "El usuario que intentó registrar ya existe, por favor ingrese otro"
        })
        
    usuario = Usuario(
    nombre,
    correo,
    telefono,
    contrasena
    )
    
    id_usuario = usuario.crear_usuario()
    if id_usuario:
        return jsonify({
                    "exito": True,
                    "mensaje": f"Registro exitoso",
                    "redireccion": "/iniciar_sesion"
                }), 200
    else:
        return jsonify({
                    "exito": False,
                    "mensaje": f"Error al registrar al usuario",
                }), 401

"""Inicializar el html de Gestion empleados"""
@empleados_bp.route("/empleados", methods = ["GET"])
def gestion_empleados():
    """Por el momento solamente se iniciaría y buscaría todos los empleados.
    Devolviendo un diccionario con los datos de estos.
    En el caso de futuro formatos de filtrado/busqueda se modificará."""
    if not probar_conexion():
        return jsonify ({
                            "exito": False,
                            "mensaje": f"Base de datos fuera de linea"
                        }), 500

    lista_empleados = Usuario.leer_usuarios()
    return render_template("gestion_empleados.html", empleados = lista_empleados)

    

"""Inicializacion de edición datos usuarios"""
@empleados_bp.route("/empleados/modificar/<id:int>", methods = ["GET"])
def modificar_usuario(id):
    if not probar_conexion():
        return jsonify ({
                "exito": False,
                "mensaje": f"Base de datos fuera de linea",
                "redireccion": "/empleados"
            }), 500
    datos_usuario = Usuario().leer_usuario(id)
    if datos_usuario:
        return render_template("editar_usuario.html", nombre = datos_usuario[1], mail = datos_usuario[2], telefono = datos_usuario[3], tipo = datos_usuario[4]) #nombre del archivo HTML Provicional

    else:
        return jsonify ({
            "Mensaje": "Hubo un error al intentar obtener los dato del empleado",
            "redireccion": "/empleados"   
        })
    
"""Logica de edicion datos usuarios"""
@empleados_bp.route("/api/empleados/modificar/<id:int>", methods = ["POST"])    
def api_modificar_usuario(id):
    datos = request.get_json(silent=True) or request.form  
    nombre = datos.get("nombre_usuario")
    correo = datos.get("mail_usuario")
    telefono = datos.get("telefono_usuario")
    contrasena = datos.get("contrasena_usuario", False)
    tipo = datos.get("tipo")  
    usuario_moficado = Usuario(
    nombre,
    correo,
    telefono,
    tipo
    )
    if usuario_moficado.actualizar_usuario(contrasena):
        return jsonify({
            "exito": True,
            "mensaje": "Empleado actualizado con exito",
            "redireccion": "/empleados"
        }), 200
    else:
        return jsonify({
                    "exito": False,
                    "mensaje": "Ah ocurrido un error al modificar al empleado",
                    "redireccion": "/empleados"
                }), 500
        

# Falta crear la funcion de borrado de usuario pero no se como va a imprementarse en el front.