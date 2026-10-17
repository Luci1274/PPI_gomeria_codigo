import math
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from flask import Blueprint, render_template, request, jsonify, session
from modulos.comandos_db.comandos_db_venta import Venta
ventas_bp = Blueprint("ventas", __name__)


# ------------------------------------------
# Cargar listado de ventas (Gestion ventas)#
# ------------------------------------------
@ventas_bp.route("/ventas")
def vista_gestion_ventas():
    """Carga la vista de gestión de ventas"""
    return render_template(
        "ventas.html", 
    )

# ------------------------------------------
# Filtrar ventas por fecha y/o búsqueda    #
# ------------------------------------------
@ventas_bp.route("/api/ventas", methods=["GET"])
def api_ventas():
    """Devuelve JSON con el listado de ventas filtrado por término de búsqueda y/o rango temporal."""
    
    busqueda = request.args.get("busqueda", "")
    filtro_fecha = request.args.get("filtro_fecha", "hoy")
    fecha_inicio = request.args.get("fecha_inicio", None)
    fecha_fin = request.args.get("fecha_fin", None)
    pagina = int(request.args.get("pagina", 1))
    limite = int(request.args.get("limite", 20))

    data = Venta.obtener_ventas_paginadas(
        busqueda=busqueda,
        filtro_fecha=filtro_fecha,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        pagina=pagina,
        limite=limite,
    )
    
    if not data["Exito"]:
        return jsonify({
            "exito": False,
            "mensaje": "Error: No se pudo conectar a la base de datos.",
            "redireccion": "/"
        }), 500

    return jsonify(data)


# ------------------------------------------
# Cargar venta por id                      #
# ------------------------------------------
@ventas_bp.route("/venta/<int:id>/detalle", methods=["GET"])
def vista_detalle_venta(id):
    """Carga la vista de detalle de una venta específica y sus productos."""
    venta_obtenida, items_venta, estado = Venta.obtener_por_id(id)
    if not estado:
        return jsonify({
            "exito": False,
            "mensaje": "Error: No se pudo conectar a la base de datos.",
            "redireccion": "/ventas"
        }), 500

    if not venta_obtenida:
        return jsonify({
            "exito": False,
            "mensaje": f"Error: No se encontró la venta con ID {id}.",
            "redireccion": "/ventas"
        }), 404

    return jsonify({
        "exito": True,
        "venta": venta_obtenida,
        "items": items_venta
    }), 200


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
    
    productos, tipos, clientes, metodos, estado = Venta.obtener_datos_inicio_venta()
  
    if not estado:
        return render_template(
            "orden_venta.html", 
            listado_productos=[], 
            listado_tipos=[], 
            listado_clientes=[],
            metodos_pago=[],
            error_db=True
        ), 500

    return render_template(
        "orden_venta.html", 
        listado_productos=productos, 
        listado_tipos=tipos,
        listado_clientes=clientes,
        metodos_pago= metodos,
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

        # 1. Obtener id_empleado de forma segura evitando KeyError
        id_empleado_actual = session.get("id_usuario")
        if not id_empleado_actual:
            return jsonify({
                "exito": False,
                "mensaje": "Sesión inválida o expirada.",
                "redireccion": "/registrarse"
            }), 401

        # 2. Extraer cliente y método de pago
        id_cliente = datos.get("id_cliente", 1)
        id_metodo_pago = datos.get("id_metodo_pago", 1)  # <-- Extraer el ID enviado por JS

        try:
            descuento_decimal = Decimal(str(datos.get("descuento", 0.0))).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )
        except (InvalidOperation, ValueError):
            return jsonify({
                "exito": False,
                "mensaje": "El descuento debe ser un importe válido."
            }), 400

        if not descuento_decimal.is_finite():
            return jsonify({
                "exito": False,
                "mensaje": "El descuento debe ser un importe válido."
            }), 400

        descuento_valor = float(descuento_decimal)
        subtotal = sum(
            float(item.get("precio_unitario", 0.0)) * int(item.get("cantidad", 0))
            for item in carrito
        )
        subtotal = round(subtotal, 2)
        if (
            not math.isfinite(descuento_valor)
            or descuento_valor < 0
            or descuento_valor > subtotal
        ):
            return jsonify({
                "exito": False,
                "mensaje": "El descuento debe ser mayor o igual a cero y no puede superar el subtotal."
            }), 400

        total_productos = calcular_total_productos(carrito)
        precio_total = calcular_precio_total(carrito, descuento_valor)

        # 3. Guardar venta en DB pasando id_metodo_pago
        id_nueva_venta = Venta.registrar(
            id_cliente=id_cliente,
            id_empleado=int(id_empleado_actual),
            lista_items=carrito,
            id_metodo_pago=int(id_metodo_pago),  # <-- Pasamos la variable a Venta.registrar
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

def calcular_total_productos(carrito):
    """Calcula la cantidad total de unidades dentro del carrito."""
    return sum(int(item.get("cantidad", 0)) for item in carrito)


def calcular_precio_total(carrito, descuento=0.0):
    """
    Calcula el precio subtotal del carrito, restando el descuento enviado.
    Valida que el descuento no supere el subtotal y redondea el total a dos decimales.
    """
    subtotal = sum(
        float(item.get("precio_unitario", 0.0)) * int(item.get("cantidad", 0))
        for item in carrito
    )

    try:
        descuento_valor = float(descuento)
    except (ValueError, TypeError):
        raise ValueError("El descuento debe ser un importe válido.") from None

    if (
        not math.isfinite(descuento_valor)
        or descuento_valor < 0
        or descuento_valor > subtotal
    ):
        raise ValueError("El descuento debe estar entre cero y el subtotal.")

    precio_final = max(0.0, subtotal - descuento_valor)

    return round(precio_final, 2)