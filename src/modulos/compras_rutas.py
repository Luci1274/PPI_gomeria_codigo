from flask import Blueprint, render_template, request, jsonify, session
from modulos.comandos_db.comandos_db_compra import Compra
compras_bp = Blueprint("compras", __name__)


# ------------------------------------------
# Cargar listado de compras (Gestion compras)#
# ------------------------------------------
@compras_bp.route("/compras")
def vista_gestion_compras():
    """Carga la vista de gestión de compras"""
    return render_template(
        "compra.html", 
    )
    
# ------------------------------------------
# Filtrar compras por fecha, búsqueda y estado #
# ------------------------------------------
@compras_bp.route("/api/compras", methods=["GET"])
def api_compras():
    """Devuelve JSON con el listado de compras filtrado por término de búsqueda, rango temporal y estado."""

    busqueda = request.args.get("busqueda", "")
    filtro_fecha = request.args.get("filtro_fecha", "hoy")
    fecha_inicio = request.args.get("fecha_inicio", None)
    fecha_fin = request.args.get("fecha_fin", None)

    # El filtro de estado se obtiene de los parámetros (1 por defecto para activas, None para todas)
    estado_param = request.args.get("estado", 1)
    estado = int(estado_param) if estado_param is not None and str(estado_param).isdigit() else None

    pagina = int(request.args.get("pagina", 1))
    limite = int(request.args.get("limite", 20))

    data = Compra.obtener_compras_paginadas(
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
# Cargar compra por id                      #
# ------------------------------------------
@compras_bp.route("/compra/<int:id>/detalle", methods=["GET"])
def vista_detalle_compra(id):
    """Carga la vista de detalle de una orden de compra específica y sus ítems."""
    compra_obtenida, items_compra, estado = Compra.obtener_por_id(id)

    if not estado:
        return jsonify({
            "exito": False,
            "mensaje": "Error: No se pudo conectar a la base de datos.",
            "redireccion": "/compras"
        }), 500

    if not compra_obtenida:
        return jsonify({
            "exito": False,
            "mensaje": f"Error: No se encontró la compra con ID {id}.",
            "redireccion": "/compras"
        }), 404

    return jsonify({
        "exito": True,
        "compra": compra_obtenida,
        "items": items_compra
    }), 200


# ------------------------------------------
# Anular Compra                             #
# ------------------------------------------
@compras_bp.route("/api/compras/anular/<int:id_compra>", methods=["POST"])
def api_anular_compra(id_compra):
    """Anula una compra y ajusta el stock del inventario."""
    try:
        exito = Compra.anular(id_compra)
        if exito:
            return jsonify({
                "exito": True,
                "mensaje": f"La compra #{id_compra} fue anulada y el stock ajustado.",
                "redireccion": "/compras"
            }), 200

        return jsonify({
            "exito": False,
            "mensaje": "No se pudo anular la compra indicada."
        }), 400
    except Exception as e:
        return jsonify({"exito": False, "error": str(e)}), 500
    
    