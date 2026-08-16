from flask import Flask, render_template, request, redirect, session, flash, jsonify
import modulos.comandos_db.comandos_db_productos as db_productos
import modulos.comandos_db.comandos_db_venta as db_ventas
import modulos.comandos_db.comandos_db_clientes as db_clientes


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
# LE FALTA EL CSS A LA TABLA QUE SE CREA DESDE LA DB
@app.route("/estructura_base_compra_inventario_venta", methods=["GET", "POST"])
def prueba():
    busqueda = request.args.get('busqueda', '')
    listado_productos = db_productos.sql_leer_productos(busqueda=busqueda)
    listado_tipos = db_productos.sql_leer_tipos()
    return render_template("estructura_base_compra_inventario_venta.html", productos = listado_productos, tipos = listado_tipos)

#####################################
# GESTION Ventas (le falta el css)  #
#####################################

@app.route('/ventas', methods=['GET', 'POST'])
def vista_gestion_ventas():
    """Muestra la vista de gestión de ventas con filtros de búsqueda y fecha."""
    if request.method == "POST":
        # Capturar parámetros de búsqueda de la URL
        busqueda = request.args.get('busqueda', '')
        filtro_fecha = request.args.get('fecha', 'todos')
        

        # Consultar BD con los filtros aplicados
        ventas = db_ventas.sql_leer_ventas(busqueda=busqueda, filtro_fecha=filtro_fecha)
        total_ventas_count = len(ventas)
        
        return render_template(
            'gestion_ventas.html',
            ventas=ventas,
            total_ventas_count=total_ventas_count,
            busqueda_actual=busqueda,
            fecha_actual=filtro_fecha
        )

    else:
        # Si es una solicitud GET, mostrar todas las ventas sin filtros
        
        ventas = db_ventas.sql_leer_ventas(busqueda=None, filtro_fecha=None)
        total_ventas_count = len(ventas)
        
        return render_template(
            'gestion_ventas.html',
            ventas=ventas,
            total_ventas_count=total_ventas_count,
            busqueda_actual=None,
            fecha_actual=None
        )

#####################################
# GESTION CLIENTES (le falta el css)#
#####################################
@app.route('/clientes', methods=['GET', 'POST'])
def vista_gestion_clientes():
    if request.method == 'POST':
        busqueda = request.form.get('busqueda', '')
        listado_clientes = db_clientes.sql_leer_clientes(busqueda=busqueda)
        return render_template('gestion_clientes.html', clientes=listado_clientes, busqueda_actual=busqueda)
    
    else:
        listado_clientes = db_clientes.sql_leer_clientes(busqueda=None)
        return render_template('gestion_clientes.html', clientes=listado_clientes, busqueda_actual=None)

#####################################################################
# MICHA DESPUES TE ROBO EL FORMULARIO PARA PODER REGISTRAR CLIENTES #
#####################################################################
@app.route('/clientes/registar', methods=['GET', 'POST'])
def registrar_cliente():
    if request.method == 'POST':
        # Capturar los datos del formulario
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        cuit = request.form.get('cuit')
        numero_tel = request.form.get('numero_tel')
        mail = request.form.get('mail')
        plazo_de_pago = request.form.get('plazo_de_pago')
        deuda = request.form.get('deuda', 0)  # Valor por defecto 0 si no se proporciona
        activo = 1  # Por defecto, el cliente está activo al registrarse

        # Llamar a la función para guardar el cliente en la base de datos
        id_nuevo_cliente = db_clientes.sql_crear_cliente(nombre, apellido, cuit, numero_tel, mail, plazo_de_pago, deuda, activo)

        if id_nuevo_cliente:
            return redirect('/clientes')  # Redirigir a la vista de gestión de clientes después del registro exitoso
        else:
            flash('Error al registrar el cliente. Por favor, inténtelo de nuevo.', 'error')

    return render_template('formulario_registro_cliente.html')

#####################################################################
# MICHA DESPUES TE ROBO EL FORMULARIO PARA PODER MODIFICAR CLIENTES #
#####################################################################
@app.route('/clientes/modificar/<int:id>', methods=['GET', 'POST'])
def modificar_cliente(id):
    if request.method == 'POST':
        # Capturar los datos del formulario
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        cuit = request.form.get('cuit')
        numero_tel = request.form.get('numero_tel')
        mail = request.form.get('mail')
        plazo_de_pago = request.form.get('plazo_de_pago')
        deuda = request.form.get('deuda', 0)  # Valor por defecto 0 si no se proporciona

        # Llamar a la función para actualizar el cliente en la base de datos
        exito = db_clientes.sql_actualizar_cliente(id, nombre, apellido, cuit, numero_tel, mail, plazo_de_pago, deuda)

        if exito:
            return redirect('/clientes')  # Redirigir a la vista de gestión de clientes después de la actualización exitosa
        else:
            flash('Error al modificar el cliente. Por favor, inténtelo de nuevo.', 'error')

    # Obtener los datos del cliente a modificar
    cliente = db_clientes.sql_leer_cliente(id)
    return render_template('formulario_modificacion_cliente.html', cliente=cliente)

#####################
# Eliminar CLIENTES #
#####################
@app.route('/clientes/eliminar/<int:id>', methods=['POST'])
def eliminar_cliente(id):
    exito = db_clientes.sql_eliminar_cliente(id)
    if exito:
        return redirect('/clientes')  # Redirigir a la vista de gestión de clientes después de la eliminación exitosa
    else:
        flash('Error al eliminar el cliente. Por favor, inténtelo de nuevo.', 'error')

if __name__ == "__main__":
    app.run(debug=True)
    