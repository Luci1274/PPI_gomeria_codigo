from flask import Blueprint, render_template, request, jsonify, flash, redirect, session
from modulos.comandos_db.conexion import probar_conexion

from modulos.comandos_db.comandos_db_empleado import Usuario

empleados_bp = Blueprint("empleados", __name__)

@empleados_bp.route("/iniciar_sesion", methods=["GET", "POST"])
def iniciar_sesion():
    if request.method == "POST":
        nombre_usuario = request.form.get("nombre_usuario")
        contrasena = request.form.get("contrasena")
        usuario = Usuario()
        usuario_verificado = usuario.verificar_credenciales(nombre_usuario, contrasena)
        if usuario_verificado:
            session["usuario"] = nombre_usuario
            flash("Inicio de sesión exitoso.", "success")
            return redirect("/index")  # Redirige a la página principal después del inicio de sesión
        else:
            flash("Nombre de usuario o contraseña incorrectos.", "danger")
            return redirect("/iniciar_sesion")  # Redirige de nuevo a la página de inicio de sesión
    
    return render_template("/iniciar_sesion.html")

@empleados_bp.route("/registrarse", methods = ["GET", "POST"])
def registrarse():
    if request.method == "POST":
        usuario = Usuario(
        nombre_ = request.form["nombre_usuario"],
        correo = request.form["mail_usuario"],
        telefono = request.form["telefono_usuario"],
        contrasena = request.form["contrasena_usuario"]
        )
        
        id_usuario = usuario.crear_usuario()
        if id_usuario:
            redirect("/iniciar_sesion")
        else:
            flash("Error en el registro.", "danger")
    
    return render_template("crear_usuario.html")

@empleados_bp.route("/empleados", methods = ["GET", "POST"])
def gestion_empleados():
    estado_conexion = probar_conexion()
    
    if not estado_conexion:
        flash("Error: No se pudo conectar a la base de datos. No se podrán ver los usuarios.", "danger")
        return render_template("gestion_empleados.html", listado_empleados = [])

    lista_empleados = Usuario.leer_usuarios()
    return render_template("gestion_empleados.html", empleados = lista_empleados)

@empleados_bp.route("/empleados/modificar/<id:int>", methods = ["GET", "POST"])
def modificar_usuario(id):
    if request.method == "POST":
        nuevo_usuario = Usuario(
            nombre_usuario = request.form["nombre_usuario"],
            contrasena = request.form["contrasena_usuario"]
            correo = request.form["correo"],
            telefono = request.form["telefono"],
            tipo = request.form["tipo_empleado"]   
        )
        

    datos_usuario = Usuario.leer_usuario(id)
    if datos_usuario:
        return jsonify({
            "nombre": datos_usuario[0],
            "mail": datos_usuario[1],
            "telefono": datos_usuario[2]
        })
    else:
        flash("Hubo un error al intentar obtener los dato del empleado", "danger")
        redirect("/empleados")
    
    