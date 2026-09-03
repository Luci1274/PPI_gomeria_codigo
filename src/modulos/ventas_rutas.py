from flask import Blueprint, render_template, request, jsonify, session
from modulos.comandos_db.comandos_db_venta import Venta
from modulos.comandos_db.comandos_db_productos import sql_alertar_stock_bajo
from modulos.comandos_db.conexion import probar_conexion

ventas_bp = Blueprint("ventas", __name__)


# ------------------------------------------
# Cargar listado de ventas (Gestion ventas)#
# ------------------------------------------
@ventas_bp.route("/ventas", methods=["GET"])
def vista_gestion_ventas():
    """Carga la vista de gestión de ventas con el listado y alertas de stock bajo."""
    estado_conexion = probar_conexion()
    if not estado_conexion:
        return jsonify({
            "exito": False,
            "mensaje": "Error: No se pudo conectar a la base de datos.",
            "redireccion": "/index"
        }), 500

    listado_productos_bajos = sql_alertar_stock_bajo()
    listado_ventas = Venta.obtener_todas()
    
    return render_template(
        "gestion_ventas.html", 
        listado_ventas=listado_ventas, 
        listado_productos_bajos=listado_productos_bajos
    )


# ------------------------------------------
# Filtrar ventas por fecha y/o búsqueda    #
# ------------------------------------------
@ventas_bp.route("/api/ventas", methods=["POST"])
def api_filtrar_ventas():
    """Devuelve JSON con el listado de ventas filtrado por término de búsqueda y/o rango temporal."""
    try:
        datos = request.get_json() or {}
        busqueda = datos.get("busqueda", "")
        filtro_fecha = datos.get("fecha", "hoy")

        listado_ventas_filtrado = Venta.obtener_todas(busqueda=busqueda, filtro_fecha=filtro_fecha)
        return jsonify({
            "exito": True,
            "listado_ventas": listado_ventas_filtrado
        }), 200
    except Exception as e:
        return jsonify({"exito": False, "error": str(e)}), 500


# ------------------------------------------
# Cargar venta por id                      #
# ------------------------------------------
@ventas_bp.route("/venta/<int:id>/detalle", methods=["GET"])
def vista_detalle_venta(id):
    """Carga la vista de detalle de una venta específica y sus productos."""
    estado_conexion = probar_conexion()
    if not estado_conexion:
        return jsonify({
            "exito": False,
            "mensaje": "Error: No se pudo conectar a la base de datos.",
            "redireccion": "/ventas"
        }), 500

    venta = Venta.obtener_por_id(id)

    if not venta:
        return jsonify({
            "exito": False,
            "mensaje": f"Error: No se encontró la venta con ID {id}.",
            "redireccion": "/ventas"
        }), 404

    return render_template("detalle_venta.html", venta=venta)


# ------------------------------------------
# Anular Venta                             #
# ------------------------------------------
@ventas_bp.route("/api/ventas/anular/<int:id_venta>", methods=["POST"])
def api_anular_venta(id_venta):
    """Anula una venta y restablece las existencias en inventario."""
    try:
        exito = Venta.anular(id_venta)
        if exito:
            return jsonify({
                "exito": True,
                "mensaje": f"La venta #{id_venta} fue anulada y el stock restituido.",
                "redireccion": "/ventas"
            }), 200
            
        return jsonify({
            "exito": False,
            "mensaje": "No se pudo anular la venta indicada."
        }), 400
    except Exception as e:
        return jsonify({"exito": False, "error": str(e)}), 500


# ------------------------------------------
# Cargar pantalla realizar venta           #
# ------------------------------------------
@ventas_bp.route("/ventas/realizar", methods=["GET"])
def vista_realizar_venta():
    
    productos, tipos, clientes, estado = Venta.obtener_datos_inicio_venta()
    
    if not estado:
        return render_template(
            "realizar_venta.html", 
            listado_productos=[], 
            listado_tipos=[], 
            listado_clientes=[],
            error_db=True
        ), 500

    return render_template(
        "realizar_venta.html", 
        listado_productos=productos, 
        listado_tipos=tipos,
        listado_clientes=clientes,
        error_db=False
    )

# ------------------------------------------
# Procesar Venta (Recibe el carrito)       #
# ------------------------------------------
@ventas_bp.route("/api/ventas/realizar", methods=["POST"])
def api_procesar_venta():
    """Recibe la solicitud del carrito y registra la transacción mediante Venta.registrar."""
    try:
        datos = request.get_json() or {}
        carrito = datos.get("carrito", [])

        if not carrito:
            return jsonify({
                "exito": False, 
                "mensaje": "El carrito de compra no puede estar vacío."
            }), 400

        id_empleado_actual = 1
        if not id_empleado_actual:
            return jsonify({
                "exito": False,
                "mensaje": "Sesión inválida o expirada.",
                "redireccion": "/login"
            }), 401

        descuento_valor = float(datos.get("descuento", 0.0))
        total_productos = calcular_total_productos(carrito)
        precio_total = calcular_precio_total(carrito, descuento_valor)

        id_nueva_venta = Venta.registrar(
            id_cliente=datos.get("id_cliente"),
            id_empleado=id_empleado_actual,
            lista_items=carrito,
            numero_factura=1,
            descuento=descuento_valor,
            precio_total=precio_total,
            total_productos=total_productos
        )

        if id_nueva_venta:
            return jsonify({
                "exito": True,
                "mensaje": f"Venta #{id_nueva_venta} realizada con éxito.",
                "id_venta": id_nueva_venta,
                "redireccion": "/ventas"
            }), 201

        return jsonify({
            "exito": False, 
            "mensaje": "Error al registrar la venta en la base de datos."
        }), 500

    except Exception as e:
        return jsonify({"exito": False, "error": str(e)}), 500


# ------------------------------------------
# Funciones Auxiliares                     #
# ------------------------------------------

def calcular_total_productos(lista_items):
    try:
        return sum(int(item['cantidad']) for item in lista_items)
    except Exception:
        return 0


def calcular_precio_total(lista_items, descuento):
    try:
        total = sum(float(item['precio_unitario']) * int(item['cantidad']) for item in lista_items)
        return total - (total * descuento)
    except Exception:
        return 0.0
