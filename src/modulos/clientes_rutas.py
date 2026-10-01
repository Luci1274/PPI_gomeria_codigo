from flask import Blueprint, render_template, request, jsonify, session
from modulos.comandos_db.comandos_db_clientes import Cliente

clientes_bp = Blueprint("clientes", __name__)

#----------------------------------------------------------------------------
# VISTA PRINCIPAL
#----------------------------------------------------------------------------
@clientes_bp.route("/clientes")
def vista_gestion_clientes():
    return render_template("clientes.html")

#----------------------------------------------------------------------------
# API: OBTENER LISTADO CON PAGINACIÓN Y FILTROS
#----------------------------------------------------------------------------
@clientes_bp.route("/api/clientes", methods=["GET"])
def api_clientes():
    pagina = request.args.get("pagina", 1, type=int)
    buscar = request.args.get("buscar", None)
    cuit = request.args.get("cuit", None)
    ciudad = request.args.get("ciudad", None)
    activo = request.args.get("activo", 1)

    total_items, clientes, ciudades, exito = Cliente.leer_clientes(
        pagina=pagina,
        por_pagina=10,
        buscar=buscar,
        cuit=cuit,
        ciudad=ciudad,
        activo=activo
    )

    if not exito:
        return jsonify({
            "exito": False,
            "mensaje": "Error: no se pudo conectar a la base de datos.",
            "redireccion": "/"
        }), 500

    total_paginas = (total_items + 10 - 1) // 10

    return jsonify({
        "exito": True,
        "clientes": clientes,
        "ciudades": ciudades,
        "pagina_actual": pagina,
        "total_paginas": total_paginas,
        "total_items": total_items
    }), 200

#----------------------------------------------------------------------------
# API: CREAR CLIENTE
#----------------------------------------------------------------------------
@clientes_bp.route("/api/clientes/crear", methods=["POST"])
def api_crear_cliente():
    datos = request.get_json() or {}

    id_nuevo_cliente = Cliente.crear_cliente(
        nombre=datos.get("nombre"),
        apellido=datos.get("apellido"),
        cuit=datos.get("cuit"),
        numero_tel=datos.get("numero_tel"),
        mail=datos.get("mail"),
        ciudad=datos.get("ciudad"),
        direccion=datos.get("direccion")
    )

    if id_nuevo_cliente is not None:
        return jsonify({
            "exito": True,
            "mensaje": "Cliente creado exitosamente",
            "id_cliente": id_nuevo_cliente
        }), 201
    else:
        return jsonify({
            "exito": False,
            "mensaje": "Error al crear cliente en la BD"
        }), 500

#----------------------------------------------------------------------------
# API: OBTENER UN CLIENTE ESPECÍFICO (PARA EDICIÓN)
#----------------------------------------------------------------------------
@clientes_bp.route("/clientes/<int:id>/editar", methods=["GET"])
def api_obtener_cliente(id):
    cliente, exito = Cliente.leer_cliente(id)

    if not exito or cliente is None:
        return jsonify({
            "exito": False,
            "mensaje": "Error: no se pudo obtener el cliente de la base de datos.",
            "redireccion": "/clientes"
        }), 500

    return jsonify({
        "exito": True,
        "cliente": cliente
    }), 200

#----------------------------------------------------------------------------
# API: MODIFICAR CLIENTE
#----------------------------------------------------------------------------
@clientes_bp.route("/api/clientes/<int:id>/editar", methods=["POST"])
def api_modificar_cliente(id):
    datos = request.get_json() or {}

    exito = Cliente.modificar_cliente(
        id=id,
        nombre=datos.get("nombre"),
        apellido=datos.get("apellido"),
        cuit=datos.get("cuit"),
        numero_tel=datos.get("numero_tel"),
        mail=datos.get("mail"),
        ciudad=datos.get("ciudad"),
        direccion=datos.get("direccion")
    )

    if exito:
        return jsonify({"exito": True, "mensaje": "Cliente modificado exitosamente"}), 200
    else:
        return jsonify({"exito": False, "mensaje": "Error al modificar cliente en la BD"}), 500

#----------------------------------------------------------------------------
# API: DESACTIVAR CLIENTE (ELIMINACIÓN LÓGICA)
#----------------------------------------------------------------------------
@clientes_bp.route("/clientes/<int:id>/desactivar")
def desactivar_cliente(id):
    exito = Cliente.eliminar_cliente(id)

    if exito:
        return jsonify({
            "exito": True,
            "mensaje": f"El cliente #{id} fue desactivado.",
            "redireccion": "/clientes"
        }), 200

    return jsonify({
        "exito": False,
        "mensaje": "No se pudo desactivar al cliente indicado."
    }), 400