from flask import Blueprint, render_template, request, jsonify, session
from modulos.comandos_db.comandos_db_proveedores import Proveedor
proveedores_bp = Blueprint("proveedores", __name__)

@proveedores_bp.route("/proveedores")
def vista_gestion_proveedores():
    return render_template("proveedor.html")

@proveedores_bp.route("/api/proveedores", methods=["GET"])
def api_proveedores():
    pagina = request.args.get("pagina", 1, type=int)
    buscar = request.args.get('buscar', None)
    rubro = request.args.get('rubro', None)
    activo = request.args.get('activo', None)
    ciudad = request.args.get('ciudad', None)

    total_items, proveedores, rubros, ciudades, exito = Proveedor.leer_proveedores(
        pagina=pagina,
        por_pagina=10,
        buscar=buscar,
        rubro=rubro,
        activo=activo,
        ciudad=ciudad
    )
    
    total_paginas = (total_items + 10 - 1) // 10
    
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
        "pagina_actual": pagina,
        "total_paginas": total_paginas,
        "total_items": total_items
    }), 200
    
@proveedores_bp.route("/api/proveedores", methods=["POST"])
def api_crear_proveedor():
    datos = request.get_json()
    
    exito = Proveedor.crear_proveedor(
        nombre=datos.get("nombre"),
        cuit=datos.get("cuit"),
        direccion=datos.get("direccion"),
        mail=datos.get("mail"),
        ciudad=datos.get("ciudad"),
        telefono=datos.get("telefono"),
        rubro=datos.get("rubro", "General")
    )

    if exito:
        return jsonify({"exito": True, "mensaje": "Proveedor creado exitosamente"}), 201
    else:
        return jsonify({"exito": False, "mensaje": "Error al crear proveedor en la BD"}), 500
    
@proveedores_bp.route("/proveedores/<int:id>/editar", methods=["GET"])
def api_obtener_proveedor(id):    
    proveedor, exito = Proveedor.leer_proveedor(id)
    
    if not exito or proveedor is None:
        return jsonify({
            "exito": False,
            "mensaje": "Error: no se pudo obtener el proveedor de la base de datos.",
            "redireccion": "/proveedores"
        }), 500
    
    return jsonify({
        "exito": True,
        "proveedor": proveedor
    }), 200


@proveedores_bp.route("/api/proveedores/<int:id>/editar", methods=["POST"])
def api_modificar_proveedor(id):
    datos = request.get_json()
    
    exito = Proveedor.modificar_proveedor(
        id=id,
        nombre=datos.get("nombre"),
        cuit=datos.get("cuit"),
        direccion=datos.get("direccion"),
        mail=datos.get("mail"),
        ciudad=datos.get("ciudad"),
        telefono=datos.get("telefono"),
        rubro=datos.get("rubro")
    )

    if exito:
        return jsonify({"exito": True, "mensaje": "Proveedor modificado exitosamente"}), 200
    else:
        return jsonify({"exito": False, "mensaje": "Error al modificar proveedor en la BD"}), 500

@proveedores_bp.route("/proveedores/<int:id>/desactivar")
def desactivar_proveedor(id):
    exito = Proveedor.eliminar_proveedor(id)
    
    if exito:
        return jsonify({
            "exito": True,
            "mensaje": f"El proveedor #{id} fue desactivado.",
            "redireccion": "/proveedores"
                    }), 200
    return jsonify({
        "exito": False,
        "mensaje": "No se pudo desactivar al proveedor indicado."
            }), 400