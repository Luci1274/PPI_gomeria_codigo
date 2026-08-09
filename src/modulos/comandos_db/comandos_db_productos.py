import pymysql
from modulos.comandos_db.conexion import conectar_db

#----------------------------------------------------------------------------
def sql_crear_producto(nombre, tipo, marca=None, medidas=None, imagen_producto=None, cantidad_actual=0, cantidad_minima=0, precio=0.0, activo=1):
    """Crea un nuevo producto en la DB"""
    sql = """INSERT INTO producto_servicio (
            nombre, tipo, marca, medidas, imagen_producto,
            activo, cantidad_actual, cantidad_minima, precio
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    conexion = conectar_db()
    try:
        with conexion.cursor() as cursor:
            valores = (nombre, tipo, marca, medidas, imagen_producto, cantidad_actual, cantidad_minima, precio)
            cursor.execute(sql, valores)
        conexion.commit()
        id_nuevo_producto = cursor.lastrowid
            
        """Esto es para nosotros"""
        print("Producto guardado correctamnete")
        return id_nuevo_producto
    
    except pymysql.MySQLError as e:
        conexion.rollback()
        print(f"Error al crear producto/servicio: {e}")
        return None
    
    finally:
        conexion.close()
            
            
#----------------------------------------------------------------------------
def sql_leer_productos(tipo=None, busqueda=None):
    """Lee los productos activos de la base de datos."""
    """Tipo: permite filtrar por categoria, Busqueda: permite buscar por texto ingresado en la barra de busqueda"""
    
    conexion = conectar_db()
    try:
        with conexion.cursor() as cursor:
            sql = ("SELECT p.idproducto_servicio, p.nombre, p.tipo, p.precio, p.imagen_producto, p.cantidad_actual FROM producto_servicio AS p WHERE activo = 1;")
            
            parametros = []
            
            if tipo:
                sql += "AND tipo = %s"
                parametros.append(tipo)
                
            if busqueda:
                sql += "AND (nombre LIKE %s)"
                parametros.append(busqueda)
            
            cursor.execute(sql, parametros)
            listado_productos = cursor.fetchall()
            return listado_productos
        
    except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al crear producto/servicio: {e}")
            return []
        
    finally:
        conexion.close()
#----------------------------------------------------------------------------
def sql_leer_producto(id):
    """Busca el producto por el id y lo devuelve"""
    conexion = conectar_db()
    
    try:
        with conexion.cursor() as cursor:
            sql = ("SELECT idproducto_servicio, nombre, tipo, marca, medidas, imagen_producto, cantidad_actual, cantidad_minima, precio FROM producto_servicio WHERE idproducto_servicio = %s;")
            valor = (id,)
            
            cursor.execute(sql, valor)
            devuelto_producto = cursor.fetchone()
            return devuelto_producto
        
    except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al crear producto/servicio: {e}")
            return None
        
    finally:
        conexion.close()
#----------------------------------------------------------------------------    
def sql_leer_tipos():
    """Lee el tipo(es la categoría) de los productos y servicios y los devuelve."""
    """La idea es que lea el tipo y con eso armamos un filtro dinamico"""
    
    conexion = conectar_db()
    
    try:
        with conexion.cursor() as cursor:
            sql = ("SELECT DISTINCT tipo FROM producto_servicio WHERE activo = 1;")

            cursor.execute(sql)
            listado_tipos = cursor.fetchall()
            return listado_tipos
    
    except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al crear producto/servicio: {e}")
            return []
        
    finally:
        conexion.close()
#----------------------------------------------------------------------------
def sql_actualizar_producto(id, datos):
    """Actualiza los datos del producto """
    conexion = conectar_db()
    try:
        with conexion.cursor() as cursor:
            sql = """UPADATE producto_servicio SET
                nombre = %s,
                tipo = %s,
                marca = %s,
                medidas = %s,
                imagen_producto = %s,
                cantidad_actual = %s,
                cantidad_minima = %s,
                precio = %s
                WHERE idproducto_servicio = %s;"""
            cursor.execute(sql, (datos.get("nombre"), datos.get("tipo"), datos.get("marca"), datos.get("medidas"), datos.get("imagen_producto"), datos.get("cantidad_actual"), datos.get("cantidad_minima"), datos.get("precio"), id))
            conexion.commit()
        return cursor.rowcount > 0
    
    except pymysql.MySQLError as e:
        conexion.rollback()
        print(f"Error al modificar el producto/servicio: {id}, el error es: {e} ")
        return False
    finally:
        conexion.close()

#----------------------------------------------------------------------------
def sql_eliminar_producto(id):
    """Elimina el producto de forma logica, no de db"""
    conexion = conectar_db()
    try:
        with conexion.cursor() as cursor:
            sql = """ UPDATE producto_servicio SET
                activo = 0 
                WHERE idproducto_servicio = %s;"""
            cursor.execute(sql, (id))
        conexion.commit()
        return cursor.rowcount > 0
    
    except pymysql.MySQLError as e:
        conexion.rollback()
        print(f"Error al desactivar el producto: {id}, error: {e}")
        return False
    
    finally:
        conexion.close()
        
        