from flask import Blueprint, render_template, request, jsonify, flash, redirect
from modulos.comandos_db.comandos_db_venta import sql_registrar_venta_completa, sql_leer_ventas, sql_anular_venta, sql_leer_venta
from modulos.comandos_db.comandos_db_productos import sql_leer_productos, sql_alertar_stock_bajo
from modulos.comandos_db.conexion import probar_conexion

ventas_bp = Blueprint("ventas", __name__)

# ------------------------------------------
# Cargar listado de ventas (Gestion ventas)#
# ------------------------------------------
@ventas_bp.route("/ventas", methods=["GET"])
def vista_gestion_ventas():
    """
    Carga la vista de gestión de ventas, mostrando el listado de ventas y alertando sobre productos con stock bajo.
    """
    
    estado_conexion = probar_conexion()
    if not estado_conexion:
        flash("Error: No se pudo conectar a la base de datos. No se podrán ver ni registrar ventas.", "danger")
        return render_template("ventas/gestion_ventas.html", listado_ventas=[], listado_productos_bajos=[])

    listado_productos_bajos = sql_alertar_stock_bajo()
    if listado_productos_bajos:
        flash("Alerta: Algunos productos están por debajo del stock mínimo. Por favor, revise el inventario.", "warning")
        
    listado_ventas = sql_leer_ventas()
    return render_template("ventas/gestion_ventas.html", listado_ventas=listado_ventas, listado_productos_bajos=listado_productos_bajos)


# ------------------------------------------
# Filtrar ventas por fecha y/o búsqueda    #
# ------------------------------------------
@ventas_bp.route("/api/ventas", methods=["POST"])
def api_filtrar_ventas():
    """
    Carga el listado de ventas filtrado por fecha y/o búsqueda.
    Recibe datos JSON desde JS (fetch / axios) y devuelve un JSON con el listado de ventas filtrado.
    """
    
    try:
        # Obtiene datos JSON enviados desde JS (fetch / axios)
        datos = request.get_json() or {}
        busqueda = datos.get("busqueda", "")
        filtro_fecha = datos.get("fecha", "hoy")
        
        listado_ventas_filtrado = sql_leer_ventas(busqueda=busqueda, filtro_fecha=filtro_fecha)
        return jsonify({"listado_ventas": listado_ventas_filtrado})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------------------------
# Cargar venta por id                      #
# ------------------------------------------
@ventas_bp.route("/venta/<int:id>/detalle", methods=["GET"])
def vista_detalle_venta(id):
    """
    Carga la vista de detalle de una venta específica, mostrando la información de la venta y sus productos.
    """
    
    estado_conexion = probar_conexion()
    if not estado_conexion:
        flash("Error: No se pudo conectar a la base de datos. No se podrán ver los detalles de la venta.", "danger")
        return redirect("/ventas")

    venta = sql_leer_venta(id)
    
    if not venta:
        flash(f"Error: No se encontró la venta con ID {id}.", "danger")
        return redirect("/ventas")

    return render_template("ventas/detalle_venta.html", venta=venta)    

# ------------------------------------------
# Anular Venta                             #
# ------------------------------------------
@ventas_bp.route("/api/ventas/anular/<int:id_venta>", methods=["POST"])
def api_anular_venta(id_venta):
    try:
        exito = sql_anular_venta(id_venta)
        if exito:
            return jsonify({"exito": True, "mensaje": f"La venta #{id_venta} fue anulada y el stock restituido."}), 200
        return jsonify({"exito": False, "mensaje": "No se pudo anular la venta indicada."}), 400
    except Exception as e:
        return jsonify({"exito": False, "error": str(e)}), 500

# ------------------------------------------
# Cargar pantalla realizar venta           #
# ------------------------------------------
@ventas_bp.route("/ventas/realizar", methods=["GET"])
def vista_realizar_venta():
    """
    Carga la vista para realizar una nueva venta.
    """
    
    estado_conexion = probar_conexion()
    if not estado_conexion:
        flash("Error: No se pudo conectar a la base de datos. No se podrán ver ni registrar ventas.", "danger")
        return render_template("ventas/realizar_venta.html", listado_productos=[], listado_productos_bajos=[])

    listado_productos = sql_leer_productos()

    return render_template("ventas/realizar_venta.html", listado_productos=listado_productos)

# ------------------------------------------
# Procesar Venta (Recibe el carrito)       #
# ------------------------------------------
@ventas_bp.route("/api/ventas/procesar", methods=["POST"])
def api_procesar_venta():
    """
    Recibe la estructura enviada por el frontend con los datos de la venta (cliente, empleado, items, descuento) y registra la venta en la base de datos.
    """
    try:
        datos = request.get_json() or {}
        carrito = datos.get("carrito", [])
        
        # Validación de negocio
        if not carrito:
            return jsonify({"exito": False, "mensaje": "El carrito de compra no puede estar vacío."}), 400

        total_productos = calcular_total_productos(carrito)
        precio_total = calcular_precio_total(carrito, float(datos.get("descuento", 0.0)))

        id_empleado_actual = datos.get("id_empleado", 4)  # Valor por defecto si no se proporciona el 4to usuario es el empleado por defecto

        id_nueva_venta = sql_registrar_venta_completa(
            id_cliente=datos.get("id_cliente"),
            id_empleado=id_empleado_actual,
            descuento=float(datos.get("descuento", 0.0)),
            lista_items=carrito,
            total_productos=total_productos,
            precio_total=precio_total
        )

        if id_nueva_venta:
            return jsonify({"exito": True, "mensaje": "Venta realizada con éxito", "id_venta": id_nueva_venta}), 201
        
        return jsonify({"exito": False, "mensaje": "Error al registrar la venta en la base de datos."}), 500

    except Exception as e:
        return jsonify({"exito": False, "error": str(e)}), 500


# ------------------------------------------
# Funciones                                #
# ------------------------------------------

def calcular_total_productos(lista_items):
    try:
        return sum(item['cantidad'] for item in lista_items)
    except Exception:
        return 0

# Esto se revisa despues, porque cambia dependiendo como termine siendo el frontend, si se envia el descuento como porcentaje o como valor absoluto. Por ahora lo dejo asi.
def calcular_precio_total(lista_items, descuento):
    try:
        total = sum(item['precio_unitario'] * item['cantidad'] for item in lista_items)
        return total - (total * descuento)
    except Exception:
        return 0