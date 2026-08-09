from flask import Flask, render_template
import modulos.comandos_db.comandos_db_productos as db_productos


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


if __name__ == "__main__":
    app.run(debug=True)
    