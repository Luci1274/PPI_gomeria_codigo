from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template("estructura_base_compra_inventario_venta.html")
    
@app.route("/resumen_orden_compra")
def resumen_orden_compra():
    return render_template(
        "resumen_orden_compra.html",
        h1="Resumen orden de compra"
        )
@app.route("/gestion")
def gestion():
    return render_template("plantiilla_base_gestion.html")

app.run(debug=True)   