from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, jsonify, session
from modulos.comandos_db.comandos_db_venta import (
    Venta,
    VentaConflictoError,
    VentaValidacionError,
)
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
    if filtro_fecha not in {"hoy", "semana", "mes", "anio", "todos"}:
        return jsonify({"exito": False, "mensaje": "El filtro de fecha no es válido."}), 400

    fecha_inicio = request.args.get("fecha_inicio") or None
    fecha_fin = request.args.get("fecha_fin") or None
    if bool(fecha_inicio) != bool(fecha_fin):
        return jsonify({
            "exito": False,
            "mensaje": "Debes indicar ambas fechas para filtrar un intervalo."
        }), 400
    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio_parseada = date.fromisoformat(fecha_inicio)
            fecha_fin_parseada = date.fromisoformat(fecha_fin)
        except ValueError:
            return jsonify({
                "exito": False,
                "mensaje": "Las fechas deben tener el formato AAAA-MM-DD."
            }), 400
        if (
            fecha_inicio_parseada.isoformat() != fecha_inicio
            or fecha_fin_parseada.isoformat() != fecha_fin
        ):
            return jsonify({
                "exito": False,
                "mensaje": "Las fechas deben tener el formato AAAA-MM-DD."
            }), 400
        if fecha_inicio_parseada > fecha_fin_parseada:
            return jsonify({
                "exito": False,
                "mensaje": "La fecha inicial no puede ser posterior a la fecha final."
            }), 400

    estado_param = request.args.get("estado", "1")
    if estado_param not in {"0", "1", "todos"}:
        return jsonify({"exito": False, "mensaje": "El filtro de estado no es válido."}), 400
    estado = int(estado_param) if estado_param in {"0", "1"} else None

    try:
        pagina = int(request.args.get("pagina", 1))
        limite = int(request.args.get("limite", 20))
    except (TypeError, ValueError):
        return jsonify({
            "exito": False,
            "mensaje": "La página y el límite deben ser números enteros."
        }), 400
    if pagina < 1 or limite < 1:
        return jsonify({
            "exito": False,
            "mensaje": "La página y el límite deben ser mayores que cero."
        }), 400

    data = Venta.obtener_ventas_paginadas(
        busqueda=busqueda,
        filtro_fecha=filtro_fecha,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado=estado,
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
    exito = Venta.anular(id_venta)
    if exito is None:
        return jsonify({
            "exito": False,
            "mensaje": "Error al anular la venta por una falla de base de datos."
        }), 500
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
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return jsonify({
            "exito": False,
            "mensaje": "El cuerpo de la solicitud debe ser un objeto JSON."
        }), 400

    carrito = datos.get("carrito")
    if not isinstance(carrito, list) or not carrito:
        return jsonify({
            "exito": False,
            "mensaje": "El carrito de venta no puede estar vacío."
        }), 400
    if datos.get("id_metodo_pago") is None:
        return jsonify({
            "exito": False,
            "mensaje": "Debes seleccionar un método de pago."
        }), 400

    try:
        id_empleado = int(session.get("id_usuario"))
        if id_empleado < 1:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({
            "exito": False,
            "mensaje": "Sesión inválida o expirada.",
            "redireccion": "/iniciar_sesion"
        }), 401

    try:
        descuento = Decimal(str(datos.get("descuento", 0)))
        if not descuento.is_finite():
            raise InvalidOperation
    except (InvalidOperation, TypeError, ValueError):
        return jsonify({
            "exito": False,
            "mensaje": "El descuento debe ser un importe válido."
        }), 400

    try:
        id_nueva_venta = Venta.registrar(
            id_cliente=datos.get("id_cliente", 1),
            id_empleado=id_empleado,
            lista_items=carrito,
            id_metodo_pago=datos["id_metodo_pago"],
            numero_factura=1,
            descuento=descuento,
        )
    except VentaConflictoError as error:
        return jsonify({"exito": False, "mensaje": str(error)}), 409
    except VentaValidacionError as error:
        return jsonify({"exito": False, "mensaje": str(error)}), 400

    if not id_nueva_venta:
        return jsonify({
            "exito": False,
            "mensaje": "Error al registrar la venta en la base de datos."
        }), 500

    return jsonify({
        "exito": True,
        "mensaje": f"Venta #{id_nueva_venta} realizada con éxito.",
        "id_venta": id_nueva_venta,
        "redireccion": "/ventas"
    }), 201