import pymysql
from config import Config

class Proveedor:
    
#----------------------------------------------------------------------------
    def crear_proveedor(nombre, cuit, direccion, mail, ciudad, telefono, rubro):
        """Crea un nuevo proveedor en la base de datos."""
        ciudad = ciudad.strip().title()
        rubro = rubro.strip().title()
        
        sql = """INSERT INTO proveedor (nombre, cuit, direccion, mail, ciudad, telefono, rubro, activo) VALUES (%s, %s, %s, %s, %s, %s, %s, 1)"""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                valores = (nombre, cuit, direccion, mail, ciudad, telefono, rubro)
                cursor.execute(sql, valores)
            conexion.commit()
                
            print("Proveedor guardado correctamente")
            return True
        
        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al crear proveedor: {e}")
            return None
        
        finally:
            conexion.close()

#----------------------------------------------------------------------------
    @staticmethod
    def leer_proveedores(pagina=1, por_pagina=10, buscar=None, rubro=None, activo=None, ciudad=None):
        """ 
        
        """
        conexion = Config.conectar_db()
        condiciones = []
        parametros = []
        where_sql = ""
        
        if buscar:
            condiciones.append("(nombre LIKE %s OR cuit LIKE %s)")
            term = f"%{buscar}%"
            parametros.extend([term, term])
        if rubro:
            condiciones.append("rubro = %s")
            parametros.append(rubro)
        if activo is not None and activo != "":
            condiciones.append("activo = %s")
            parametros.append(activo)
        if ciudad:
            condiciones.append("ciudad = %s")
            parametros.append(ciudad)
        
        if condiciones:
            where_sql += " WHERE " + " AND " .join(condiciones)
        
        print(
           "where_sql:", where_sql,
           "condiciones:", condiciones,
           "parametros:", parametros 
        )
            
        try:
            with conexion.cursor() as cursor:
                """contar total de filas"""
                cursor.execute(f"SELECT COUNT(idproveedor) AS total from proveedor{where_sql}", parametros)
                total_items = cursor.fetchone()["total"]
                print("items totales: " ,total_items)
                
                """consulta final aplicando filtros + limit/offset"""
                offset = (pagina - 1) * por_pagina
                sql = f"SELECT idproveedor, nombre, cuit, direccion, mail, ciudad, telefono, rubro, activo FROM proveedor{where_sql} ORDER BY idproveedor ASC LIMIT %s OFFSET %s"
                print("offset :", offset)
                """Combinar parametros de busqueda  con los de la paginación"""
                parametros_paginados = parametros + [por_pagina, offset]
                cursor.execute(sql, parametros_paginados)
                proveedores = cursor.fetchall()
                
                print(proveedores)
                
                cursor.execute("SELECT DISTINCT rubro FROM proveedor WHERE rubro IS NOT NULL AND rubro != ''")
                rubros = cursor.fetchall()
                print("rubros :", rubros)
                cursor.execute("SELECT DISTINCT ciudad FROM proveedor WHERE ciudad IS NOT NULL AND ciudad != ''")
                ciudades = cursor.fetchall()
                print("Ciudades: ", ciudades)
                return total_items, proveedores, rubros, ciudades, True
                
        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al crear proveedor: {e}")
            return 0, [], [], [], False
        
        finally:
            conexion.close()
#----------------------------------------------------------------------------
    @staticmethod
    def leer_proveedor(id):
        """Busca el proveedor por el id y lo devuelve"""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT idproveedor, nombre, cuit, direccion, mail, ciudad, telefono, rubro FROM proveedor WHERE idproveedor = %s"
                cursor.execute(sql, (id,))
                proveedor = cursor.fetchone()
                return proveedor, True
                
        except pymysql.MySQLError as e:
            print(f"Error al leer proveedor: {e}")
            proveedor = None
            return proveedor, False
        finally:
            conexion.close()

#----------------------------------------------------------------------------
    def modificar_proveedor(id, nombre, cuit, direccion, mail, ciudad, telefono, rubro):
        """Modifica los datos de un proveedor existente en la base de datos."""
        ciudad = ciudad.strip().title()
        rubro = rubro.strip().title()
        
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    UPDATE proveedor
                    SET nombre = %s,
                        cuit = %s,
                        direccion = %s,
                        mail = %s,
                        ciudad = %s,
                        telefono = %s,
                        rubro = %s
                    WHERE idproveedor = %s
                """
                cursor.execute(sql, (nombre, cuit, direccion, mail, ciudad, telefono, rubro, id))
                conexion.commit()
                return True
        except Exception as e:
            print(f"Error al modificar proveedor: {e}")
            conexion.rollback()
            return False
        finally:
            conexion.close()
        
#----------------------------------------------------------------------------
    @staticmethod
    def eliminar_proveedor(id):
        """Elimina un proveedor de la base de datos de forma logica"""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE proveedor SET activo = 0 WHERE idproveedor = %s"
                cursor.execute(sql, (id,))
                conexion.commit()
                return True
        except pymysql.MySQLError as e:
                conexion.rollback()
                print(f"Error al crear proveedor: {e}")
                return None
            
        finally:
            conexion.close()