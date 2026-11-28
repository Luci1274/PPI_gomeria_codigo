from flask import Blueprint, render_template, request, jsonify
from modulos.comandos_db.comandos_db_proveedores import (
    Proveedor,
    ProveedorDuplicadoError,
)
proveedores_bp = Blueprint("proveedores", __name__)

LONGITUDES_CAMPOS = {
    "nombre": 45,
    "cuit": 20,
    "direccion": 45,
    "mail": 45,
    "ciudad": 45,
    "telefono": 45,
    "rubro": 75,
}


def validar_datos_proveedor(datos, rubro_predeterminado=None):
    if not isinstance(datos, dict):
        return None, "El cuerpo de la solicitud debe ser un objeto JSON."

    valores = {}
    for campo, longitud_maxima in LONGITUDES_CAMPOS.items():
        predeterminado = rubro_predeterminado if campo == "rubro" else ""
        valor = datos.get(campo, predeterminado)
        if valor is None:
            valor = ""
        if not isinstance(valor, str):
            return None, f"El campo {campo} debe ser texto."

        valor = valor.strip()
        if campo in {"nombre", "cuit", "rubro"} and not valor:
            return None, f"El campo {campo} es obligatorio."
        if len(valor) > longitud_maxima:
            return None, f"El campo {campo} no puede superar {longitud_maxima} caracteres."
        valores[campo] = valor

    return valores, None


@proveedores_bp.route("/proveedores")
def vista_gestion_proveedores():
    return render_template("proveedor.html")

@proveedores_bp.route("/api/proveedores", methods=["GET"])
def api_proveedores():
    try:
        pagina = int(request.args.get("pagina", "1"))
    except (TypeError, ValueError):
        return jsonify({
            "exito": False,
            "mensaje": "La página debe ser un número entero."
        }), 400
    if pagina < 1:
        return jsonify({
            "exito": False,
            "mensaje": "La página debe ser mayor que cero."
        }), 400

    buscar = request.args.get('buscar', None)
    rubro = request.args.get('rubro', None)
    activo = request.args.get('activo', '')
    if activo not in {'', '0', '1'}:
        return jsonify({
            "exito": False,
            "mensaje": "El filtro de estado no es válido."
        }), 400
    ciudad = request.args.get('ciudad', None)

    (
        total_items,
        proveedores,
        rubros,
        ciudades,
        pagina_actual,
        exito,
    ) = Proveedor.leer_proveedores(
        pagina=pagina,
        por_pagina=10,
        buscar=buscar,
        rubro=rubro,
        activo=activo,
        ciudad=ciudad
    )
    
    total_paginas = max(1, (total_items + 10 - 1) // 10)
    
    if not exito:
        return jsonify({
            "exito": False,
            "mensaje": "Error: no se pudo conectar a la base de datos.",
            "redireccion": "/"
        }), 500
    
    return jsonify ({
        "exito": True,
        "proveedores": proveedores,
        "rubros": rubros,
        "ciudades": ciudades,
        "pagina_actual": pagina_actual,
        "total_paginas": total_paginas,
        "total_items": total_items
    }), 200
    
@proveedores_bp.route("/api/proveedores/crear", methods=["POST"])
def api_crear_proveedor():
    valores, error = validar_datos_proveedor(
        request.get_json(silent=True),
        rubro_predeterminado="General",
    )
    if error:
        return jsonify({"exito": False, "mensaje": error}), 400

    try:
        exito = Proveedor.crear_proveedor(**valores)
    except ProveedorDuplicadoError as e:
        return jsonify({"exito": False, "mensaje": str(e)}), 409

    if exito:
        return jsonify({"exito": True, "mensaje": "Proveedor creado exitosamente"}), 201
    else:
        return jsonify({"exito": False, "mensaje": "Error al crear proveedor en la BD"}), 500
    
@proveedores_bp.route("/proveedores/<int:id>/editar", methods=["GET"])
def api_obtener_proveedor(id):    
    proveedor, exito = Proveedor.leer_proveedor(id)
    
    if not exito:
        return jsonify({
            "exito": False,
            "mensaje": "Error: no se pudo obtener el proveedor de la base de datos.",
            "redireccion": "/proveedores"
        }), 500
    if proveedor is None:
        return jsonify({
            "exito": False,
            "mensaje": "No se encontró el proveedor indicado."
        }), 404
    
    return jsonify({
        "exito": True,
        "proveedor": proveedor
    }), 200


@proveedores_bp.route("/api/proveedores/<int:id>/editar", methods=["POST"])
def api_modificar_proveedor(id):
    valores, error = validar_datos_proveedor(request.get_json(silent=True))
    if error:
        return jsonify({"exito": False, "mensaje": error}), 400

    try:
        exito = Proveedor.modificar_proveedor(id=id, **valores)
    except ProveedorDuplicadoError as e:
        return jsonify({"exito": False, "mensaje": str(e)}), 409

    if exito:
        return jsonify({"exito": True, "mensaje": "Proveedor modificado exitosamente"}), 200
    if exito is False:
        return jsonify({
            "exito": False,
            "mensaje": "No se encontró el proveedor indicado."
        }), 404
    return jsonify({
        "exito": False,
        "mensaje": "Error al modificar proveedor en la base de datos."
    }), 500

@proveedores_bp.route("/proveedores/<int:id>/desactivar", methods=["POST"])
def api_desactivar_proveedor(id):
    exito = Proveedor.eliminar_proveedor(id)
    
    if exito is None:
        return jsonify({
            "exito": False,
            "mensaje": "Error al desactivar el proveedor por una falla de base de datos."
        }), 500
    if exito:
        return jsonify({
            "exito": True,
            "mensaje": f"El proveedor #{id} fue desactivado.",
            "redireccion": "/proveedores"
                    }), 200
    return jsonify({
        "exito": False,
        "mensaje": "No se encontró un proveedor activo con ese identificador."
            }), 404


@proveedores_bp.route("/api/proveedores/<int:id>/activar", methods=["POST"])
def activar_proveedor(id):
    exito = Proveedor.activar_proveedor(id)

    if exito is None:
        return jsonify({
            "exito": False,
            "mensaje": "Error al reactivar el proveedor por una falla de base de datos."
        }), 500
    if exito:
        return jsonify({
            "exito": True,
            "mensaje": f"El proveedor #{id} fue reactivado."
        }), 200

    return jsonify({
        "exito": False,
        "mensaje": "No se encontró un proveedor inactivo con ese identificador."
    }), 404