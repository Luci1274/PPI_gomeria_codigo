import re

import pymysql
from config import Config


class ProveedorCuitInvalidoError(ValueError):
    """El CUIT está vacío o no contiene caracteres válidos."""


class ProveedorCuitDuplicadoError(ValueError):
    """El CUIT ya está asociado a otro proveedor."""


class ProveedorNoEncontradoError(LookupError):
    """No existe el proveedor solicitado."""


class ProveedorYaInactivoError(ValueError):
    """El proveedor ya estaba desactivado."""


def _normalizar_cuit(cuit):
    if not isinstance(cuit, str):
        raise ProveedorCuitInvalidoError("El CUIT es obligatorio.")
    cuit_normalizado = re.sub(r"[ .-]", "", cuit)
    if not cuit_normalizado or not cuit_normalizado.isdigit():
        raise ProveedorCuitInvalidoError("El CUIT debe contener solo números.")
    return cuit_normalizado


def _buscar_proveedor_por_cuit(cursor, cuit, excluir_id=None):
    sql = """
        SELECT idproveedor
        FROM proveedor
        WHERE REPLACE(REPLACE(REPLACE(TRIM(cuit), '.', ''), '-', ''), ' ', '') = %s
    """
    parametros = [cuit]
    if excluir_id is not None:
        sql += " AND idproveedor != %s"
        parametros.append(excluir_id)
    sql += " LIMIT 1"
    cursor.execute(sql, parametros)
    return cursor.fetchone()


class Proveedor:
    
#----------------------------------------------------------------------------
    @staticmethod
    def crear_proveedor(nombre, cuit, direccion, mail, ciudad, telefono, rubro):
        """Crea un nuevo proveedor en la base de datos."""
        cuit_normalizado = _normalizar_cuit(cuit)
        ciudad = (ciudad or "").strip().title()
        rubro = (rubro or "").strip().title()
        
        sql = """INSERT INTO proveedor (nombre, cuit, direccion, mail, ciudad, telefono, rubro, activo) VALUES (%s, %s, %s, %s, %s, %s, %s, 1)"""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                if _buscar_proveedor_por_cuit(cursor, cuit_normalizado):
                    raise ProveedorCuitDuplicadoError(
                        "Ya existe un proveedor registrado con ese CUIT."
                    )
                valores = (nombre, cuit, direccion, mail, ciudad, telefono, rubro)
                cursor.execute(sql, valores)
            conexion.commit()
                
            print("Proveedor guardado correctamente")
            return True
        
        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al crear proveedor: {e}")
            return None
        except (ProveedorCuitDuplicadoError, ProveedorCuitInvalidoError):
            conexion.rollback()
            raise

        finally:
            conexion.close()

#----------------------------------------------------------------------------
    @staticmethod
    def leer_proveedores(pagina=1, por_pagina=10, buscar=None, rubro=None, activo=None, ciudad=None):
        """ 
        Buscar los proveedores utilizando unos parametros de busqueda, en caso de que los parametros sean None devuelve todos, limitados cada 10
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
            
        try:
            with conexion.cursor() as cursor:
                """contar total de filas"""
                cursor.execute(f"SELECT COUNT(idproveedor) AS total from proveedor{where_sql}", parametros)
                total_items = cursor.fetchone()["total"]
                
                
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
    @staticmethod
    def modificar_proveedor(id, nombre, cuit, direccion, mail, ciudad, telefono, rubro):
        """Modifica los datos de un proveedor existente en la base de datos."""
        cuit_normalizado = _normalizar_cuit(cuit)
        ciudad = (ciudad or "").strip().title()
        rubro = (rubro or "").strip().title()
        
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT idproveedor FROM proveedor WHERE idproveedor = %s FOR UPDATE",
                    (id,),
                )
                if not cursor.fetchone():
                    raise ProveedorNoEncontradoError(
                        f"No existe el proveedor #{id}."
                    )

                if _buscar_proveedor_por_cuit(cursor, cuit_normalizado, excluir_id=id):
                    raise ProveedorCuitDuplicadoError(
                        "Ya existe otro proveedor registrado con ese CUIT."
                    )

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
                if cursor.rowcount == 0:
                    cursor.execute(
                        "SELECT idproveedor FROM proveedor WHERE idproveedor = %s FOR UPDATE",
                        (id,),
                    )
                    if not cursor.fetchone():
                        raise ProveedorNoEncontradoError(
                            f"No existe el proveedor #{id}."
                        )
                conexion.commit()
                return True
        except (ProveedorNoEncontradoError, ProveedorCuitDuplicadoError, ProveedorCuitInvalidoError):
            conexion.rollback()
            raise
        except pymysql.MySQLError as e:
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
                cursor.execute(
                    "SELECT activo FROM proveedor WHERE idproveedor = %s FOR UPDATE",
                    (id,),
                )
                proveedor = cursor.fetchone()
                if not proveedor:
                    raise ProveedorNoEncontradoError(
                        f"No existe el proveedor #{id}."
                    )
                if not proveedor["activo"]:
                    raise ProveedorYaInactivoError(
                        f"El proveedor #{id} ya estaba desactivado."
                    )

                cursor.execute(
                    "UPDATE proveedor SET activo = 0 WHERE idproveedor = %s AND activo = 1",
                    (id,),
                )
                if cursor.rowcount != 1:
                    raise ProveedorNoEncontradoError(
                        f"No se pudo desactivar el proveedor #{id}."
                    )
                conexion.commit()
                return True
        except (
            ProveedorNoEncontradoError,
            ProveedorYaInactivoError,
        ):
            conexion.rollback()
            raise
        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al desactivar proveedor: {id}, error: {e}")
            return False
            
        finally:
            conexion.close()