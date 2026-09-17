from flask import Flask, render_template, request, redirect, session, flash, jsonify
from config import Config
from modulos.ventas_rutas import ventas_bp
from modulos.empleados_rutas import empleados_bp
from modulos.proveedores_rutas import proveedores_bp
from modulos.comandos_db.comandos_db_pantalla_inicial import mostrar

app = Flask(__name__)

app.config.from_object(Config)

# ---------------------------------------------------------------------------------------------
# 🛡️ GUARDIA DE SEGURIDAD (Control de Sesiones y Roles)
# ---------------------------------------------------------------------------------------------
@app.before_request
def proteger_rutas():
    # 1. Ignorar archivos estáticos y rutas inexistentes
    if not request.endpoint or request.endpoint == 'static' or request.endpoint.endswith('.static'):
        return

    rutas_publicas = app.config.get("RUTAS_PUBLICAS", [])
    endpoint_actual = request.endpoint.split(".")[-1]

    # 2. Permitir si el nombre del endpoint o la URL están en la lista pública
    if endpoint_actual in rutas_publicas or request.path in rutas_publicas:
        return

    # 3. Validar si existe la sesión
    if "id_usuario" not in session:
        # Si la petición viene de un fetch/AJAX (como las APIs), respondemos JSON 401 en lugar de redirigir
        if request.path.startswith("/api/"):
            return jsonify({
                "exito": False,
                "mensaje": "Sesión expirada o no autorizada"
            }), 401

        flash("Debes iniciar sesión para acceder al sistema", "warning")
        return redirect("/iniciar_sesion")

# Ruta principal que sirve la vista
@app.route("/")
def inicio():
    # Le pasamos el usuario guardado en la sesión (o 'Usuario' por defecto)
    nombre_usuario = session.get('nombre_usuario', 'Usuario')
    return render_template("pantalla_principal.html", nombre_usuario=nombre_usuario)


# Ruta API que usará JavaScript para consultar la DB periódicamente
@app.route("/api/datos-dashboard")
def api_datos_dashboard():
    total_productos, total_clientes, ventas_dia, ultimas_ventas, productos_bajos, exito = mostrar()

    if not exito:
        return jsonify({
            "exito": False,
            "mensaje": "Error: No se pudo conectar a la base de datos."
        }), 500

    return jsonify({
        "exito": True,
        "total_productos": total_productos,
        "total_clientes": total_clientes,
        "ventas_dia": ventas_dia,
        "ultimas_ventas": ultimas_ventas,
        "productos_bajos": productos_bajos
    })

app.register_blueprint(ventas_bp)
app.register_blueprint(empleados_bp)
app.register_blueprint(proveedores_bp)
    
@app.route("/resumen_orden_compra")
def resumen_orden_compra():
    return render_template("resumen_orden_compra.html")
@app.route("/gestion")
def gestion():
    return render_template("plantiilla_base_gestion.html")

@app.route("/clientes")
def clientes():
    return render_template("clientes.html")

if __name__ == "__main__":
    app.run(debug=True)