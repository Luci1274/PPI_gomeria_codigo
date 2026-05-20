from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template("estructura_base_compra_inventario_venta.html")
    


app.run(debug=True)   