import pymysql
from config import Config
from modulos.comandos_db.comando_db_genericos import GenericosDB


class ProveedorDuplicadoError(ValueError):
    """El CUIT ya pertenece a otro proveedor."""


def _es_error_cuit_duplicado(error):
    return bool(error.args) and error.args[0] == 1062


class Proveedor:
    
#----------------------------------------------------------------------------
    @staticmethod
    def crear_proveedor(nombre, cuit, direccion, mail, ciudad, telefono, rubro):
        """Crea un nuevo proveedor en la base de datos."""
        ciudad = GenericosDB.normalizar_texto(ciudad, estilo="titulo")
        rubro = GenericosDB.normalizar_texto(rubro, estilo="titulo")
        
        sql = """INSERT INTO proveedor (nombre, cuit, direccion, mail, ciudad, telefono, rubro, activo) VALUES (%s, %s, %s, %s, %s, %s, %s, 1)"""
        conexion = None
        try:
            conexion = Config.conectar_db()
            with conexion.cursor() as cursor:
                valores = (nombre, cuit, direccion, mail, ciudad, telefono, rubro)
                cursor.execute(sql, valores)
            conexion.commit()
                
            print("Proveedor guardado correctamente")
            return True
        
        except pymysql.MySQLError as e:
            if conexion:
                conexion.rollback()
            if _es_error_cuit_duplicado(e):
                raise ProveedorDuplicadoError("Ya existe un proveedor con ese CUIT.") from e
            print(f"Error al crear proveedor: {e}")
            return None
        
        finally:
            if conexion:
                conexion.close()

#----------------------------------------------------------------------------
    @staticmethod
    def leer_proveedores(pagina=1, por_pagina=10, buscar=None, rubro=None, activo=None, ciudad=None):
        """ 
        Buscar los proveedores utilizando unos parametros de busqueda, en caso de que los parametros sean None devuelve todos, limitados cada 10
        """
        conexion = None
        condiciones = []
        parametros = []
        
        GenericosDB.agregar_filtro_busqueda(
            condiciones, parametros, ("nombre", "cuit"), buscar
        )
        if rubro:
            condiciones.append("rubro = %s")
            parametros.append(rubro)
        if activo is not None and activo != "":
            condiciones.append("activo = %s")
            parametros.append(activo)
        if ciudad:
            condiciones.append("ciudad = %s")
            parametros.append(ciudad)
        
        where_sql = GenericosDB.construir_where(condiciones)
            
        try:
            conexion = Config.conectar_db()
            with conexion.cursor() as cursor:
                """contar total de filas"""
                cursor.execute(f"SELECT COUNT(idproveedor) AS total from proveedor{where_sql}", parametros)
                total_items = cursor.fetchone()["total"]
                total_paginas = max(1, (total_items + por_pagina - 1) // por_pagina)
                pagina = min(pagina, total_paginas)
                
                
                """consulta final aplicando filtros + limit/offset"""
                offset = (pagina - 1) * por_pagina
                sql = f"SELECT idproveedor, nombre, cuit, direccion, mail, ciudad, telefono, rubro, activo FROM proveedor{where_sql} ORDER BY idproveedor ASC LIMIT %s OFFSET %s"
                """Combinar parametros de busqueda  con los de la paginación"""
                parametros_paginados = parametros + [por_pagina, offset]
                cursor.execute(sql, parametros_paginados)
                proveedores = cursor.fetchall()
                
                cursor.execute("SELECT DISTINCT rubro FROM proveedor WHERE rubro IS NOT NULL AND rubro != ''")
                rubros = cursor.fetchall()
                cursor.execute("SELECT DISTINCT ciudad FROM proveedor WHERE ciudad IS NOT NULL AND ciudad != ''")
                ciudades = cursor.fetchall()
                return total_items, proveedores, rubros, ciudades, pagina, True
                
        except pymysql.MySQLError as e:
            if conexion:
                conexion.rollback()
            print(f"Error al consultar proveedores: {e}")
            return 0, [], [], [], 1, False
        
        finally:
            if conexion:
                conexion.close()
#----------------------------------------------------------------------------
    @staticmethod
    def leer_proveedor(id):
        """Busca el proveedor por el id y lo devuelve"""
        conexion = None
        try:
            conexion = Config.conectar_db()
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
            if conexion:
                conexion.close()

#----------------------------------------------------------------------------
    @staticmethod
    def modificar_proveedor(id, nombre, cuit, direccion, mail, ciudad, telefono, rubro):
        """Modifica los datos de un proveedor existente en la base de datos."""
        ciudad = GenericosDB.normalizar_texto(ciudad, estilo="titulo")
        rubro = GenericosDB.normalizar_texto(rubro, estilo="titulo")
        
        conexion = None
        try:
            conexion = Config.conectar_db()
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM proveedor WHERE idproveedor = %s",
                    (id,),
                )
                if not cursor.fetchone():
                    return False

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
        except pymysql.MySQLError as e:
            if conexion:
                conexion.rollback()
            if _es_error_cuit_duplicado(e):
                raise ProveedorDuplicadoError("Ya existe un proveedor con ese CUIT.") from e
            print(f"Error al modificar proveedor: {e}")
            return None
        finally:
            if conexion:
                conexion.close()
        
#----------------------------------------------------------------------------
    @staticmethod
    def eliminar_proveedor(id):
        """Elimina un proveedor de la base de datos de forma logica"""
        conexion = None
        try:
            conexion = Config.conectar_db()
            with conexion.cursor() as cursor:
                sql = "UPDATE proveedor SET activo = 0 WHERE idproveedor = %s AND activo = 1"
                cursor.execute(sql, (id,))
                actualizado = cursor.rowcount > 0
                conexion.commit()
                return actualizado
        except pymysql.MySQLError as e:
            if conexion:
                conexion.rollback()
            print(f"Error al desactivar proveedor: {e}")
            return None
            
        finally:
            if conexion:
                conexion.close()

    @staticmethod
    def activar_proveedor(id):
        """Reactiva un proveedor que fue dado de baja lógicamente."""
        conexion = None
        try:
            conexion = Config.conectar_db()
            with conexion.cursor() as cursor:
                cursor.execute(
                    "UPDATE proveedor SET activo = 1 WHERE idproveedor = %s AND activo = 0",
                    (id,),
                )
                actualizado = cursor.rowcount > 0
                conexion.commit()
                return actualizado
        except pymysql.MySQLError as e:
            if conexion:
                conexion.rollback()
            print(f"Error al reactivar proveedor: {e}")
            return None
        finally:
            if conexion:
                conexion.close()