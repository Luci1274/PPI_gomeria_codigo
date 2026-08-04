from modulos.conexion import conectar_db
#----------------------------------------------------------------------------
def sql_leer_productos():
    """La funcion lee los productos en la db y los devuelve"""
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT p.idproducto_servicio, p.nombre, p.tipo, imagen_producto, s.cantidad FROM producto_servicio AS p JOIN stock_actual AS s   ON p.idproducto_servicio = s.idstock_actual")
    listado_productos = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    return listado_productos
#----------------------------------------------------------------------------

