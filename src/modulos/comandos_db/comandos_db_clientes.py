import pymysql
from config import Config

class Cliente:

#----------------------------------------------------------------------------
    @staticmethod
    def crear_cliente(nombre, apellido, cuit, numero_tel, mail, activo=1):
        """Crea un nuevo cliente en la base de datos."""
        nombre = nombre.strip().title() if nombre else ""
        apellido = apellido.strip().title() if apellido else ""

        sql = """INSERT INTO clientes (nombre, apellido, cuit, numero_tel, mail, activo) 
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                valores = (nombre, apellido, cuit, numero_tel, mail, activo)
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
    def leer_clientes(pagina=1, por_pagina=10, buscar=None, activo=None, busqueda=None, activa=None):
        """
        Busca clientes aplicando paginación, filtros de búsqueda y calculando la deuda
        obtenida del historial de pagos de ventas incompletas activas.
        """
        conexion = Config.conectar_db()
        condiciones = []
        parametros = []
        where_sql = ""

        # Soporte para alias de nombres de parámetros
        term_buscar = buscar if buscar is not None else busqueda
        term_activo = activo if activo is not None else activa

        if term_buscar:
            condiciones.append("(c.nombre LIKE %s OR c.apellido LIKE %s OR c.cuit LIKE %s)")
            term = f"%{term_buscar}%"
            parametros.extend([term, term, term])

        if term_activo is not None and term_activo != "":
            condiciones.append("c.activo = %s")
            parametros.append(term_activo)

        if condiciones:
            where_sql = " WHERE " + " AND ".join(condiciones)

        try:
            with conexion.cursor() as cursor:
                # Contar el total de registros para la paginación
                sql_count = f"SELECT COUNT(DISTINCT c.id) AS total FROM clientes c{where_sql}"
                cursor.execute(sql_count, parametros)
                resultado_count = cursor.fetchone()
                total_items = resultado_count["total"] if resultado_count else 0

                # Consulta principal con joins para calcular la deuda acumulada
                offset = (pagina - 1) * por_pagina
                sql = f"""
                    SELECT 
                        c.id,
                        c.id AS idcliente,
                        c.nombre,
                        c.apellido,
                        c.cuit,
                        c.numero_tel,
                        c.mail,
                        c.activo,
                        COALESCE(SUM(hpc.monto), 0) AS deuda
                    FROM clientes c
                    LEFT JOIN venta v ON c.id = v.idcliente AND v.activa = 1 AND v.estado = 0
                    LEFT JOIN historial_pago_cliente hpc ON v.idventa = hpc.idventa
                    {where_sql}
                    GROUP BY c.id, c.nombre, c.apellido, c.cuit, c.numero_tel, c.mail, c.activo
                    ORDER BY c.id ASC
                    LIMIT %s OFFSET %s
                """
                parametros_paginados = parametros + [por_pagina, offset]
                cursor.execute(sql, parametros_paginados)
                clientes = cursor.fetchall()

                return total_items, clientes, True

        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al leer clientes: {e}")
            return 0, [], False

        finally:
            conexion.close()

#----------------------------------------------------------------------------
    @staticmethod
    def leer_cliente(id):
        """Busca un cliente específico por su ID y devuelve sus datos."""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT id, id AS idcliente, nombre, apellido, cuit, numero_tel, mail, activo FROM clientes WHERE id = %s"
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
    def actualizar_cliente(id, nombre, apellido, cuit, numero_tel, mail):
        """Actualiza los datos de un cliente existente en la base de datos."""
        nombre = nombre.strip().title() if nombre else ""
        apellido = apellido.strip().title() if apellido else ""

        sql = """
            UPDATE clientes
            SET nombre = %s,
                apellido = %s,
                cuit = %s,
                numero_tel = %s,
                mail = %s
            WHERE id = %s
        """
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                valores = (nombre, apellido, cuit, numero_tel, mail, id)
                cursor.execute(sql, valores)
                conexion.commit()
                print("Cliente actualizado correctamente")
                return True

        except Exception as e:
            conexion.rollback()
            print(f"Error al actualizar cliente: {e}")
            return False

        finally:
            conexion.close()

    # Alias por compatibilidad
    modificar_cliente = actualizar_cliente

#----------------------------------------------------------------------------
    @staticmethod
    def eliminar_cliente(id):
        """Elimina un cliente de la base de datos de forma lógica (activo = 0)."""
        sql = "UPDATE clientes SET activo = 0 WHERE id = %s"
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
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