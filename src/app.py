from flask import Flask, render_template

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

if __name__ == "__main__":
    app.run(debug=True)