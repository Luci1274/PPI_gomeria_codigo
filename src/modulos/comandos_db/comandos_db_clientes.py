import pymysql
from config import Config

class Cliente:

#----------------------------------------------------------------------------
    @staticmethod
    def crear_cliente(nombre, apellido, cuit, numero_tel, mail, ciudad=None, direccion=None):
        """Crea un nuevo cliente en la base de datos."""
        nombre = nombre.strip().title() if nombre else ""
        apellido = apellido.strip().title() if apellido else ""
        ciudad = ciudad.strip().title() if ciudad else ""
        direccion = direccion.strip().title() if direccion else ""
        
        sql = """
            INSERT INTO cliente (nombre, apellido, cuit, numero_tel, mail, ciudad, direccion, activo) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
        """
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                valores = (nombre, apellido, cuit, numero_tel, mail, ciudad, direccion)
                cursor.execute(sql, valores)
                id_nuevo_cliente = cursor.lastrowid
            conexion.commit()
            
            print("Cliente guardado correctamente")
            return id_nuevo_cliente
        
        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al crear cliente: {e}")
            return None
        
        finally:
            conexion.close()

#----------------------------------------------------------------------------
    @staticmethod
    def leer_clientes(pagina=1, por_pagina=10, buscar=None, cuit=None, ciudad=None, activo=1):
        """
        Lee los cliente de la base de datos aplicando paginación y filtros de búsqueda.
        Calcula la deuda acumulada sumando los montos de historial_pago_cliente de ventas activas e incompletas.
        """
        conexion = Config.conectar_db()
        condiciones = []
        parametros = []
        where_sql = ""

        # Filtros dinámicos para la tabla cliente
        if buscar:
            condiciones.append("(c.nombre LIKE %s OR c.apellido LIKE %s OR c.cuit LIKE %s)")
            term = f"%{buscar}%"
            parametros.extend([term, term, term])
        if cuit:
            condiciones.append("c.cuit = %s")
            parametros.append(cuit)
        if ciudad:
            condiciones.append("c.ciudad = %s")
            parametros.append(ciudad)
        if activo is not None and activo != "":
            condiciones.append("c.activo = %s")
            parametros.append(activo)

        if condiciones:
            where_sql = " WHERE " + " AND ".join(condiciones)

        try:
            with conexion.cursor() as cursor:
                # 1. Contar total de filas para paginación
                sql_count = f"SELECT COUNT(c.idcliente) AS total FROM cliente c{where_sql}"
                cursor.execute(sql_count, parametros)
                total_items = cursor.fetchone()["total"]

                # 2. Consulta principal con calculo de deuda (LEFT JOINs) y paginación
                offset = (pagina - 1) * por_pagina
                sql = f"""
                    SELECT 
                        c.idcliente, 
                        c.nombre, 
                        c.apellido, 
                        c.cuit, 
                        c.numero_tel, 
                        c.mail, 
                        c.ciudad,
                        c.direccion,
                        c.activo,
                        IFNULL(SUM(h.monto), 0) AS deuda
                    FROM cliente c
                    LEFT JOIN venta v 
                        ON c.idcliente = v.idcliente AND v.activa = 1 AND v.estado = 0
                    LEFT JOIN historial_pago_cliente h 
                        ON v.idventa = h.idventa
                    {where_sql}
                    GROUP BY c.idcliente, c.nombre, c.apellido, c.cuit, c.numero_tel, c.mail, c.ciudad, c.activo
                    ORDER BY c.idcliente ASC 
                    LIMIT %s OFFSET %s
                """
                parametros_paginados = parametros + [por_pagina, offset]
                cursor.execute(sql, parametros_paginados)
                cliente = cursor.fetchall()

                # 3. Obtener listado de ciudades distintas para los filtros
                cursor.execute("SELECT DISTINCT ciudad FROM cliente WHERE ciudad IS NOT NULL AND ciudad != ''")
                ciudades = cursor.fetchall()

                return total_items, cliente, ciudades, True

        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al leer cliente: {e}")
            return 0, [], [], False

        finally:
            conexion.close()

#----------------------------------------------------------------------------
    @staticmethod
    def leer_cliente(id):
        """Busca un cliente específico por su idcliente y calcula su deuda actual."""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT 
                        c.idcliente, 
                        c.nombre, 
                        c.apellido, 
                        c.cuit, 
                        c.numero_tel, 
                        c.mail, 
                        c.ciudad,
                        c.direccion,
                        c.activo,
                        IFNULL(SUM(h.monto), 0) AS deuda
                    FROM cliente c
                    LEFT JOIN venta v 
                        ON c.idcliente = v.idcliente AND v.activa = 1 AND v.estado = 0
                    LEFT JOIN historial_pago_cliente h 
                        ON v.idventa = h.idventa
                    WHERE c.idcliente = %s AND c.activo = 1
                    GROUP BY c.idcliente, c.nombre, c.apellido, c.cuit, c.numero_tel, c.mail, c.ciudad, c.activo
                """
                cursor.execute(sql, (id,))
                cliente = cursor.fetchone()
                return cliente, True

        except pymysql.MySQLError as e:
            print(f"Error al leer cliente: {e}")
            return None, False
        finally:
            conexion.close()

#----------------------------------------------------------------------------
    @staticmethod
    def modificar_cliente(id, nombre, apellido, cuit, numero_tel, mail, ciudad=None, direccion=None):
        """Modifica los datos de un cliente existente en la base de datos."""
        nombre = nombre.strip().title() if nombre else ""
        apellido = apellido.strip().title() if apellido else ""
        ciudad = ciudad.strip().title() if ciudad else None
        direccion = direccion.strip().title() if direccion else None

        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    UPDATE cliente
                    SET nombre = %s,
                        apellido = %s,
                        cuit = %s,
                        numero_tel = %s,
                        mail = %s,
                        ciudad = %s,
                        direccion = %s
                    WHERE idcliente = %s
                """
                cursor.execute(sql, (nombre, apellido, cuit, numero_tel, mail, ciudad, direccion, id))
                conexion.commit()
                print("Cliente actualizado correctamente")
                return True
        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al modificar cliente: {e}")
            return False
        finally:
            conexion.close()

#----------------------------------------------------------------------------
    @staticmethod
    def eliminar_cliente(id):
        """Elimina un cliente de la base de datos de forma lógica (activo = 0)."""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE cliente SET activo = 0 WHERE idcliente = %s"
                cursor.execute(sql, (id,))
                conexion.commit()
                print("Cliente eliminado correctamente")
                return True
        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al eliminar cliente: {e}")
            return False
        finally:
            conexion.close()