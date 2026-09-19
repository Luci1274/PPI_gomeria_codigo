import pymysql
from config import Config

class Producto:
    
    #----------------------------------------------------------------------------
    def crear_producto(nombre=None, tipo=None, marca=None, medidas=None, imagen_producto=None, cantidad_actual=0, cantidad_minima=0, precio=0.0):
        """Crea un nuevo producto en la DB"""
        sql = """INSERT INTO producto_servicio (
                nombre, tipo, marca, medidas, imagen_producto,
                activo, cantidad_actual, cantidad_minima, precio
                ) VALUES (%s, %s, %s, %s,%s, 1, %s, %s, %s)
            """
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                valores = (nombre, tipo, marca, medidas, imagen_producto, cantidad_actual, cantidad_minima, precio)
                cursor.execute(sql, valores)
            conexion.commit()
                
            """Esto es para nosotros"""
            print("Producto guardado correctamnete")
            return True
        
        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al crear producto/servicio: {e}")
            return None
        
        finally:
            conexion.close()
                
                
    #----------------------------------------------------------------------------
    @staticmethod
    def leer_productos(pagina=1, por_pagina=10, buscar=None,tipo=None,marca=None,estado=None):
        """ 
        Buscar los productos utilizando unos parametros de busqueda, en caso de que los parametros sean None devuelve todos, limitados cada 10        
        """
        conexion = Config.conectar_db()
        condiciones = []
        parametros = []
        where_sql = ""
        
        if buscar:
            condiciones.append("nombre LIKE %s")
            term = f"%{buscar}%"
            parametros.extend([term])
        if tipo:
            condiciones.append("tipo LIKE %s")
            parametros.append(tipo)
        if marca:
            condiciones.append("marca LIKE %s")
            parametros.append(marca)
        if estado is not None and estado != "":
            condiciones.append("activo = %s")
            parametros.append(estado)
            
        if condiciones:
            where_sql += " WHERE " + " AND " .join(condiciones)
        
        print(
            "where_sql:", where_sql,
            "condiciones:", condiciones,
            "parametros:", parametros 
        )
        
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                
                cursor.execute(f"SELECT COUNT (idproducto_servicio) AS total FROM producto_servicio{where_sql}", parametros)
                total_items = cursor.fetchone()["total"]
                print("items totales: " ,total_items)
                
                offset = (pagina - 1) * por_pagina
                sql = f"SELECT p.idproducto_servicio, p.nombre, p.medidas, p.tipo, p.precio, p.cantidad_actual FROM producto_servicio AS p{where_sql} ORDER BY p.idproducto_servicio ASC LIMIT %s OFFSET %s"
                
                parametros_paginados = parametros + [por_pagina,offset]
                cursor.execute(sql, parametros_paginados)
                productos = cursor.fetchall()
                
                print(productos)
                
                cursor.execute("SELECT DISTINCT tipo FROM producto_servicio WHERE tipo IS NOT NULL AND tipo !='' ")
                tipos = cursor.fetchall()
                cursor.execute("SELECT DISTINCT marca FROM producto_servicio WHERE marca IS NOT NULL AND marca !='' ")
                marcas = cursor.fetchall()
                
                return total_items, productos, tipos, marcas, True
            
        except pymysql.MySQLError as e:
                conexion.rollback()
                print(f"Error al crear producto/servicio: {e}")
                return 0, [], [], [], False
            
        finally:
            conexion.close()
    #----------------------------------------------------------------------------
    @staticmethod
    def leer_producto(id):
        """Busca el producto por el id y lo devuelve"""
        conexion = Config.conectar_db()
        
        try:
            with conexion.cursor() as cursor:
                sql = ("SELECT idproducto_servicio, nombre, tipo, marca, medidas, cantidad_actual, cantidad_minima, precio FROM producto_servicio WHERE idproducto_servicio = %s;")
                valor = (id,)
                
                cursor.execute(sql, valor)
                devuelto_producto = cursor.fetchone()
                return devuelto_producto, True 
            
        except pymysql.MySQLError as e:
                conexion.rollback()
                print(f"Error al crear producto/servicio: {e}")
                return [], False
            
        finally:
            conexion.close()

    #----------------------------------------------------------------------------
    def actualizar_producto(id, nombre=None, tipo=None, marca=None, medidas=None, imagen_producto=None, cantidad_actual=0, cantidad_minima=0, precio=0.0):
        """Actualiza los datos del producto """
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = """UPDATE producto_servicio SET
                    nombre = %s,
                    tipo = %s,
                    marca = %s,
                    medidas = %s,
                    imagen_producto = %s,
                    cantidad_actual = %s,
                    cantidad_minima = %s,
                    precio = %s
                    WHERE idproducto_servicio = %s;"""
                
                valores = (nombre, tipo, marca, medidas, imagen_producto, cantidad_actual, cantidad_minima, precio, id)
                
                cursor.execute(sql, valores)
                conexion.commit()
            return True
        
        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al modificar el producto/servicio: {id}, el error es: {e} ")
            return False
        finally:
            conexion.close()

    #----------------------------------------------------------------------------
    def eliminar_producto(id):
        """Elimina el producto de forma logica, no de db"""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = """ UPDATE producto_servicio SET
                    activo = 0 
                    WHERE idproducto_servicio = %s;"""
                cursor.execute(sql, (id,))
            conexion.commit()
            return cursor.rowcount > 0
        
        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al desactivar el producto: {id}, error: {e}")
            return False
        
        finally:
            conexion.close()
            
    #-------------------------------------------------------------------
    def alertar_stock_bajo():
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT idproducto_servicio, nombre, cantidad_actual, cantidad_minima FROM producto_servicio WHERE activo = 1 AND cantidad_actual < cantidad_minima;"
                cursor.execute(sql)
                return cursor.fetchall()
        except pymysql.MySQLError as e:
            print(f"Error al alertar stock bajo: {e}")
            return []
        finally:
            conexion.close()