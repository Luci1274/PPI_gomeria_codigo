from flask import Flask, render_template
import modulos.comandos_db.comandos_db_productos as db_productos
from modulos.comandos_db.comandos_db_venta import sql_leer_ventas


app = Flask(__name__)
app.secret_key = "una_clave_secreta_y_segura_aqui"

@app.route("/")
def inicio():
    return render_template("estructura_base_compra_inventario_venta.html")
    
@app.route("/resumen_orden_compra")
def resumen_orden_compra():
    return render_template("resumen_orden_compra.html")
@app.route("/gestion")
def gestion():
    return render_template("plantiilla_base_gestion.html")

########################################################################
# Me gusta la decoración jajaja por ahora voy a colocar acá las rutas  #
########################################################################
@app.route("/estructura_base_compra_inventario_venta")
def prueba():
    listado_productos = db_productos.sql_leer_productos()
    listado_tipos = db_productos.sql_leer_tipos()
    return render_template("estructura_base_compra_inventario_venta.html", productos = listado_productos, tipos = listado_tipos)

#####################################
# Ventas ############################
####################################

@app.route('/ventas')
def vista_gestion_ventas():
    # Capturar parámetros de búsqueda de la URL
    busqueda = request.args.get('busqueda', '')
    filtro_fecha = request.args.get('fecha', 'todos')

    # Consultar BD con los filtros aplicados
    ventas = sql_leer_ventas(busqueda=busqueda, filtro_fecha=filtro_fecha)
    total_ventas_count = len(ventas)

    # Renderizar la plantilla enviando los datos y los filtros activos (para mantener el estado de los inputs)
    return render_template(
        'gestion_ventas.html', 
        ventas=ventas, 
        total_ventas_count=total_ventas_count,
        busqueda_actual=busqueda,
        fecha_actual=filtro_fecha
    )


if __name__ == "__main__":
    app.run(debug=True)
    