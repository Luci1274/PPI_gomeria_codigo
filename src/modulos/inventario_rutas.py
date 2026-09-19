from flask import Blueprint, render_template, request, jsonify, session
from modulos.comandos_db.comandos_db_productos import Producto
from modulos.api_claudinary import subir_imagen

inventario_bp = Blueprint("inventario", __name__)

@inventario_bp.route("/inventario")
def vista_gestion_inventario():
    return render_template("inventario.html")


@inventario_bp.route("/api/inventario", methods=["POST"])
def api_inventario():
    pagina = request.args.get("pagina", 1, type=int)
    buscar = request.args.get("buscar", None)
    tipo = request.args.get("tipo", None)
    marca = request.args.get("marca", None)
    estado = request.args.get("estado", None)
    
    total_items, productos, tipos, marcas, exito = Producto.leer_productos(
        pagina=pagina,
        por_pagina=10,
        buscar=buscar,
        tipo=tipo,
        marca=marca,
        estado=estado    
    )
    
    total_paginas = (total_items + 10 - 1) // 10
    
    if not exito:
        return jsonify({
            "exito": False,
            "Mensaje": "Error no se pudo conectar a la base de datos.",
            "redireccion": "/"
        }), 500
    
    return jsonify({
        "exito": True,
        "productos": productos,
        "tipos": tipos,
        "marcas": marcas,
        "pagina_actual": pagina,
        "total_paginas": total_paginas,
        "total_items": total_items
    }), 200
    
    
@inventario_bp.route("/api/inventario/crear", methods=["POST"])
def api_crear_producto():
    # 1. Obtenemos los textos de request.form
    nombre = request.form.get("nombre")
    tipo = request.form.get("tipo")
    marca = request.form.get("marca")
    medidas = request.form.get("medidas")
    cantidad = request.form.get("cantidad", type=int)
    minimo = request.form.get("minimo", type=int)
    precio = request.form.get("precio", type=float)

    # 2. Obtenemos el archivo de request.files
    imagen_file = request.files.get("imagen_producto")
    url_producto = None

    if imagen_file and imagen_file.filename != "":
        url_producto = subir_imagen(imagen_file)  # Cloudinary procesa directamente el objeto imagen_file
        if not url_producto:
            return jsonify({
                "exito": False,
                "mensaje": "Ocurrió un error al intentar subir la imagen a Cloudinary"
            }), 400

    # 3. Guardamos en BD
    exito = Producto.crear_producto(
        nombre=nombre,
        tipo=tipo,
        marca=marca,
        medidas=medidas,
        imagen_producto=url_producto,
        cantidad_actual=cantidad,
        cantidad_minima=minimo,
        precio=precio   
    )
    
    if not exito:
        return jsonify({"exito": False, "mensaje": "Error al guardar el producto"}), 500

    return jsonify({"exito": True, "mensaje": "Producto guardado exitosamente"}), 201


@inventario_bp.route("/inventario/<int:id>/modificar", methods=["GET"])
def api_obtener_producto(id):
    producto, exito = Producto.leer_producto(id)
    
    if not exito or producto is None:
        return jsonify({
            "exito": False,
            "mensaje": "Error: no se pudo obtener el producto de la base de datos.",
            "redireccion": "/inventario"
        }), 500
    
    return jsonify({
        "exito": True,
        "producto": producto
    }), 200
    
@inventario_bp.route("/api/inventario/<int:id>/modificar", methods=["POST"])
def api_modificar_producto(id):
    # 1. Obtenemos datos de texto usando request.form
    nombre = request.form.get("nombre")
    tipo = request.form.get("tipo")
    marca = request.form.get("marca")
    medidas = request.form.get("medidas")
    cantidad = request.form.get("cantidad", type=int)
    minimo = request.form.get("minimo", type=int)
    precio = request.form.get("precio", type=float)

    # 2. Obtenemos el archivo de imagen de request.files
    imagen_file = request.files.get("imagen_producto")
    url_producto = None

    if imagen_file and imagen_file.filename != "":
        url_producto = subir_imagen(imagen_file)
        if not url_producto:
            return jsonify({
                "exito": False,
                "mensaje": "Ha ocurrido un error al intentar subir la imagen a Cloudinary"
            }), 400

    # 3. Guardamos los cambios en BD
    exito = Producto.actualizar_producto(
        id=id,
        nombre=nombre,
        tipo=tipo,
        marca=marca,
        medidas=medidas,
        imagen_producto=url_producto,
        cantidad_actual=cantidad,
        cantidad_minima=minimo,
        precio=precio   
    )

    if not exito:
        return jsonify({
            "exito": False,
            "mensaje": "Ha ocurrido un error al modificar el producto"
        }), 500

    return jsonify({
        "exito": True,
        "mensaje": "Producto modificado exitosamente"
    }), 200
     
@inventario_bp.route("/api/inventario/<int:id>/desactivar")
def desactivar_producto(id):
    exito = Producto.eliminar_producto(id)
    
    if exito:
        return jsonify({
            "exito": True,
            "mensaje": f"El Producto #{id} fue desactivado.",
            "redireccion": "/inventario"
                    }), 200
    return jsonify({
        "exito": False,
        "mensaje": "No se pudo desactivar el producto indicado."
            }), 400