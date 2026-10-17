import pymysql

from config import Config
from modulos.comandos_db.comando_db_genericos import GenericosDB


class ProductoDuplicadoError(ValueError):
    """Se intenta crear un producto o servicio con una identidad existente."""


class Producto:
    @staticmethod
    def _obtener_o_crear_tipo(cursor, nombre):
        nombre = GenericosDB.normalizar_texto(nombre)
        if not nombre:
            raise ValueError("El tipo es obligatorio.")

        cursor.execute(
            """
            INSERT INTO tipos (nombre)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE idtipo = LAST_INSERT_ID(idtipo), activo = 1
            """,
            (nombre,),
        )
        return cursor.lastrowid

    @staticmethod
    def _es_duplicado(error):
        return bool(error.args) and error.args[0] == 1062

    @staticmethod
    def crear_producto(
        nombre=None,
        tipo=None,
        marca=None,
        medidas=None,
        imagen_producto=None,
        cantidad_actual=0,
        cantidad_minima=0,
        precio=0.0,
    ):
        nombre = GenericosDB.normalizar_texto(nombre)
        marca = GenericosDB.normalizar_texto(marca, predeterminado=None)
        medidas = GenericosDB.normalizar_texto(medidas, predeterminado=None)
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                id_tipo = Producto._obtener_o_crear_tipo(cursor, tipo)
                if GenericosDB.existe_registro(
                    cursor,
                    "producto",
                    {
                        "nombre": nombre,
                        "idtipo": id_tipo,
                        "marca": marca,
                        "medidas": medidas,
                    },
                    columnas_normalizadas=("nombre", "marca", "medidas"),
                ):
                    raise ProductoDuplicadoError(
                        "Ya existe un producto con el mismo nombre, tipo, marca y medidas."
                    )
                cursor.execute(
                    """
                    INSERT INTO producto (
                        nombre, idtipo, marca, medidas, imagen_producto,
                        cantidad_actual, cantidad_minima, precio
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        nombre,
                        id_tipo,
                        marca,
                        medidas,
                        imagen_producto,
                        cantidad_actual,
                        cantidad_minima,
                        precio,
                    ),
                )
            conexion.commit()
            return True
        except ProductoDuplicadoError:
            conexion.rollback()
            raise
        except pymysql.MySQLError as error:
            conexion.rollback()
            if Producto._es_duplicado(error):
                raise ProductoDuplicadoError(
                    "Ya existe un producto con el mismo nombre, tipo, marca y medidas."
                ) from error
            print(f"Error al crear producto: {error}")
            return False
        finally:
            conexion.close()

    @staticmethod
    def crear_servicio(nombre, tipo, precio):
        nombre = GenericosDB.normalizar_texto(nombre)
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                id_tipo = Producto._obtener_o_crear_tipo(cursor, tipo)
                if GenericosDB.existe_registro(
                    cursor, "servicio", {"nombre": nombre}
                ):
                    raise ProductoDuplicadoError(
                        "Ya existe un servicio con ese nombre."
                    )
                cursor.execute(
                    """
                    INSERT INTO servicio (nombre, idtipo, precio)
                    VALUES (%s, %s, %s)
                    """,
                    (nombre, id_tipo, precio),
                )
            conexion.commit()
            return True
        except ProductoDuplicadoError:
            conexion.rollback()
            raise
        except pymysql.MySQLError as error:
            conexion.rollback()
            if Producto._es_duplicado(error):
                raise ProductoDuplicadoError(
                    "Ya existe un servicio con ese nombre."
                ) from error
            print(f"Error al crear servicio: {error}")
            return False
        finally:
            conexion.close()

    @staticmethod
    def _consulta_inventario():
        return """
            SELECT
                p.idproducto AS idproducto_servicio,
                p.nombre,
                t.nombre AS tipo,
                p.marca,
                p.medidas,
                p.precio,
                p.cantidad_actual,
                p.cantidad_minima,
                p.imagen_producto,
                p.activo,
                'producto' AS tipo_item
            FROM producto AS p
            INNER JOIN tipos AS t ON t.idtipo = p.idtipo
            UNION ALL
            SELECT
                s.idservicio AS idproducto_servicio,
                s.nombre,
                t.nombre AS tipo,
                NULL AS marca,
                NULL AS medidas,
                s.precio,
                0 AS cantidad_actual,
                0 AS cantidad_minima,
                NULL AS imagen_producto,
                s.activo,
                'servicio' AS tipo_item
            FROM servicio AS s
            INNER JOIN tipos AS t ON t.idtipo = s.idtipo
        """

    @staticmethod
    def leer_productos(pagina=1, por_pagina=10, buscar=None, tipo=None, marca=None, estado=None):
        conexion = Config.conectar_db()
        condiciones = []
        parametros = []

        GenericosDB.agregar_filtro_busqueda(
            condiciones, parametros, ("inventario.nombre",), buscar
        )
        if tipo:
            condiciones.append("inventario.tipo = %s")
            parametros.append(tipo)
        if marca:
            condiciones.append("inventario.marca = %s")
            parametros.append(marca)
        if estado is not None and estado != "":
            condiciones.append("inventario.activo = %s")
            parametros.append(estado)

        where_sql = GenericosDB.construir_where(condiciones)
        consulta_inventario = Producto._consulta_inventario()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    f"SELECT COUNT(*) AS total FROM ({consulta_inventario}) AS inventario{where_sql}",
                    parametros,
                )
                total_items = cursor.fetchone()["total"]

                offset = max(0, (pagina - 1) * por_pagina)
                cursor.execute(
                    f"""
                    SELECT * FROM ({consulta_inventario}) AS inventario
                    {where_sql}
                    ORDER BY nombre ASC, tipo_item ASC
                    LIMIT %s OFFSET %s
                    """,
                    parametros + [por_pagina, offset],
                )
                items = cursor.fetchall()

                cursor.execute(
                    "SELECT nombre AS tipo FROM tipos WHERE activo = 1 ORDER BY nombre"
                )
                tipos = cursor.fetchall()
                cursor.execute(
                    """
                    SELECT DISTINCT marca
                    FROM producto
                    WHERE marca IS NOT NULL AND marca != ''
                    ORDER BY marca
                    """
                )
                marcas = cursor.fetchall()
                return total_items, items, tipos, marcas, True
        except pymysql.MySQLError as error:
            conexion.rollback()
            print(f"Error al consultar el inventario: {error}")
            return 0, [], [], [], False
        finally:
            conexion.close()

    @staticmethod
    def leer_producto(id, tipo_item="producto"):
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                if tipo_item == "servicio":
                    cursor.execute(
                        """
                        SELECT s.idservicio AS idproducto_servicio, s.nombre,
                               t.nombre AS tipo, s.precio, s.activo,
                               'servicio' AS tipo_item
                        FROM servicio AS s
                        INNER JOIN tipos AS t ON t.idtipo = s.idtipo
                        WHERE s.idservicio = %s
                        """,
                        (id,),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT p.idproducto AS idproducto_servicio, p.nombre,
                               t.nombre AS tipo, p.marca, p.medidas,
                               p.cantidad_actual, p.cantidad_minima, p.precio,
                               p.imagen_producto, p.activo,
                               'producto' AS tipo_item
                        FROM producto AS p
                        INNER JOIN tipos AS t ON t.idtipo = p.idtipo
                        WHERE p.idproducto = %s
                        """,
                        (id,),
                    )
                return cursor.fetchone(), True
        except pymysql.MySQLError as error:
            print(f"Error al obtener {tipo_item} #{id}: {error}")
            return None, False
        finally:
            conexion.close()

    @staticmethod
    def actualizar_producto(
        id,
        nombre=None,
        tipo=None,
        marca=None,
        medidas=None,
        imagen_producto=None,
        cantidad_actual=0,
        cantidad_minima=0,
        precio=0.0,
    ):
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                id_tipo = Producto._obtener_o_crear_tipo(cursor, tipo)
                cursor.execute(
                    """
                    UPDATE producto
                    SET nombre = %s, idtipo = %s, marca = %s, medidas = %s,
                        imagen_producto = COALESCE(%s, imagen_producto),
                        cantidad_actual = %s, cantidad_minima = %s, precio = %s
                    WHERE idproducto = %s
                    """,
                    (
                        GenericosDB.normalizar_texto(nombre),
                        id_tipo,
                        GenericosDB.normalizar_texto(marca, predeterminado=None),
                        GenericosDB.normalizar_texto(medidas, predeterminado=None),
                        imagen_producto,
                        cantidad_actual,
                        cantidad_minima,
                        precio,
                        id,
                    ),
                )
            conexion.commit()
            return True
        except pymysql.MySQLError as error:
            conexion.rollback()
            print(f"Error al modificar producto #{id}: {error}")
            return False
        finally:
            conexion.close()

    @staticmethod
    def actualizar_servicio(id, nombre, tipo, precio):
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                id_tipo = Producto._obtener_o_crear_tipo(cursor, tipo)
                cursor.execute(
                    """
                    UPDATE servicio
                    SET nombre = %s, idtipo = %s, precio = %s
                    WHERE idservicio = %s
                    """,
                    (GenericosDB.normalizar_texto(nombre), id_tipo, precio, id),
                )
            conexion.commit()
            return True
        except pymysql.MySQLError as error:
            conexion.rollback()
            print(f"Error al modificar servicio #{id}: {error}")
            return False
        finally:
            conexion.close()

    @staticmethod
    def eliminar_producto(id, tipo_item="producto"):
        tabla, columna_id = (
            ("servicio", "idservicio")
            if tipo_item == "servicio"
            else ("producto", "idproducto")
        )
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    f"UPDATE {tabla} SET activo = 0 WHERE {columna_id} = %s",
                    (id,),
                )
                afectadas = cursor.rowcount
            conexion.commit()
            return afectadas > 0
        except pymysql.MySQLError as error:
            conexion.rollback()
            print(f"Error al desactivar {tipo_item} #{id}: {error}")
            return False
        finally:
            conexion.close()

    @staticmethod
    def alertar_stock_bajo():
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT idproducto AS idproducto_servicio, nombre,
                           cantidad_actual, cantidad_minima
                    FROM producto
                    WHERE activo = 1 AND cantidad_actual < cantidad_minima
                    """
                )
                return cursor.fetchall()
        except pymysql.MySQLError as error:
            print(f"Error al alertar stock bajo: {error}")
            return []
        finally:
            conexion.close()
