from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template("estructura_base_compra_inventario_venta.html")
    
@app.route("/resumen_orden_compra")
def resumen_orden_compra():
    return render_template("resumen_orden_compra.html")

@app.route("/gestion")
def gestion():
    return render_template("plantiilla_base_gestion.html")

@app.route("/registro_proveedor")
def registro_proveedor():
    return render_template("registro_proveedor.html")

app.run(debug=True)