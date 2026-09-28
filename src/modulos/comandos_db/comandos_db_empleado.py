from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import pymysql

class Usuario:
    def __init__(self, nombre=None, correo=None, telefono=None, contrasena=None, tipo="Empleado", id_usuario=None):
        self.__id_usuario = id_usuario
        self.__nombre = nombre
        self.__correo = correo
        self.__telefono = telefono
        self.__contrasena = contrasena
        self.__tipo = tipo

# LOGIN
    @staticmethod
    def hash_contraseña(contraseña):
        return generate_password_hash(contraseña)

    @staticmethod
    def verificar_credenciales(nombre_ingresado, contrasena_ingresada):
        """Verifica si las credenciales coinciden con las almacenadas en la base de datos."""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT idempleado, nombre_usuario, contrasena, tipo FROM empleado WHERE nombre_usuario = %s AND activo = 1"
                cursor.execute(sql, (nombre_ingresado,))
                usuario = cursor.fetchone()

                if usuario and check_password_hash(usuario.get("contrasena"), contrasena_ingresada):
                    return [usuario["idempleado"], usuario["tipo"], usuario["nombre_usuario"]]
                return None
        except pymysql.MySQLError as e:
            print(f"Error al verificar las credenciales: {e}")
            return False
        finally:
            conexion.close()

    def crear_usuario(self):
        """Inserta un nuevo empleado en la base de datos."""
        conexion = Config.conectar_db()
        try:
            hash_contrasena = self.hash_contraseña(self.__contrasena)
            with conexion.cursor() as cursor:
                sql = "INSERT INTO empleado (nombre_usuario, mail, telefono, contrasena, tipo) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (self.__nombre, self.__correo, self.__telefono, hash_contrasena, self.__tipo))
                conexion.commit()
                self.__id_usuario = cursor.lastrowid
                return self.__id_usuario
        except pymysql.MySQLError as e:
            print(f"Error al crear el usuario: {e}")
            return None
        finally:
            conexion.close()

    @staticmethod
    def existe_usuario(nombre_usuario):
        """Comprueba si un usuario ya existe en la base de datos."""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT nombre_usuario FROM empleado WHERE nombre_usuario = %s"
                cursor.execute(sql, (nombre_usuario,))
                resultado = cursor.fetchone()
                return True if resultado else False
        except pymysql.MySQLError as e:
            print(f"Error al verificar existencia del usuario: {e}")
            return False
        finally:
            conexion.close()

# Gestion empleados
    @staticmethod
    def leer_empleados(
        pagina=1, por_pagina=10, buscar=None, rol=None, activo=1
    ):
        """
        Busca empleados aplicando paginación y filtros dinámicos por nombre, email, teléfono o rol.
        """
        conexion = Config.conectar_db()
        condiciones = []
        parametros = []
        where_sql = ""

        # Filtro de búsqueda general (Nombre, Email o Teléfono)
        if buscar:
            condiciones.append(
                "(nombre_usuario LIKE %s OR mail LIKE %s OR telefono LIKE %s)"
            )
            term = f"%{buscar}%"
            parametros.extend([term, term, term])

        # Filtro opcional por Rol / Tipo
        if rol:
            condiciones.append("tipo = %s")
            parametros.append(rol)

        # Filtro por estado activo (por defecto trae activos = 1)
        if activo is not None and activo != "":
            condiciones.append("activo = %s")
            parametros.append(activo)

        if condiciones:
            where_sql = " WHERE " + " AND ".join(condiciones)

        try:
            with conexion.cursor() as cursor:
                # 1. Obtener total de registros
                cursor.execute(
                    f"SELECT COUNT(idempleado) AS total FROM empleado{where_sql}",
                    parametros,
                )
                total_items = cursor.fetchone()["total"]

                # 2. Consulta de empleados paginados
                offset = (pagina - 1) * por_pagina
                sql = f"""
                    SELECT 
                        idempleado, 
                        nombre_usuario AS nombre, 
                        mail AS email, 
                        telefono, 
                        tipo AS rol, 
                        activo 
                    FROM empleado{where_sql} 
                    ORDER BY idempleado ASC 
                    LIMIT %s OFFSET %s
                """
                parametros_paginados = parametros + [por_pagina, offset]
                cursor.execute(sql, parametros_paginados)
                empleados = cursor.fetchall()

                # 3. Obtener roles disponibles para filtros frontend
                cursor.execute(
                    "SELECT DISTINCT tipo AS rol FROM empleado WHERE tipo IS NOT NULL AND tipo != ''"
                )
                roles = [r["rol"] for r in cursor.fetchall()]

                return total_items, empleados, roles, True

        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al consultar empleados: {e}")
            return 0, [], [], False

        finally:
            conexion.close()

    # -------------------------------------------------------------------------
    @staticmethod
    def leer_empleado(id_empleado):
        """Busca un empleado por ID y devuelve sus datos alineados con el modal de edición."""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT 
                        idempleado, 
                        nombre_usuario AS nombre, 
                        mail AS email, 
                        telefono, 
                        tipo AS rol,
                        activo
                    FROM empleado 
                    WHERE idempleado = %s
                """
                cursor.execute(sql, (id_empleado,))
                empleado = cursor.fetchone()
                return empleado, True

        except pymysql.MySQLError as e:
            print(f"Error al leer empleado: {e}")
            return None, False

        finally:
            conexion.close()

    # -------------------------------------------------------------------------
    @staticmethod
    def modificar_empleado(
        id_empleado, nombre, email, telefono, rol, contrasena=None
    ):
        """Modifica los datos de un empleado existente."""
        nombre = nombre.strip().title() if nombre else ""
        email = email.strip().lower() if email else ""
        telefono = telefono.strip() if telefono else ""
        rol = rol.strip().title() if rol else "Empleado"

        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                if contrasena:
                    hash_contrasena = generate_password_hash(contrasena)
                    sql = """
                        UPDATE empleado
                        SET nombre_usuario = %s,
                            mail = %s,
                            telefono = %s,
                            tipo = %s,
                            contrasena = %s
                        WHERE idempleado = %s
                    """
                    cursor.execute(
                        sql,
                        (
                            nombre,
                            email,
                            telefono,
                            rol,
                            hash_contrasena,
                            id_empleado,
                        ),
                    )
                else:
                    sql = """
                        UPDATE empleado
                        SET nombre_usuario = %s,
                            mail = %s,
                            telefono = %s,
                            tipo = %s
                        WHERE idempleado = %s
                    """
                    cursor.execute(
                        sql, (nombre, email, telefono, rol, id_empleado)
                    )

                conexion.commit()
                return True

        except Exception as e:
            print(f"Error al modificar empleado: {e}")
            conexion.rollback()
            return False

        finally:
            conexion.close()

    # -------------------------------------------------------------------------
    @staticmethod
    def eliminar_empleado(id_empleado):
        """Aplica la baja lógica del empleado (activo = 0)."""
        conexion = Config.conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE empleado SET activo = 0 WHERE idempleado = %s"
                cursor.execute(sql, (id_empleado,))
                conexion.commit()
                return True

        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al desactivar empleado: {e}")
            return False

        finally:
            conexion.close()
            
# Crear usuario/empleado desde gestion
# @staticmethod
#     def crear_empleado(
#         nombre, email, telefono, rol, contrasena="123456"
#     ):
#         """Crea un nuevo empleado en la base de datos."""
#         nombre = nombre.strip().title() if nombre else ""
#         email = email.strip().lower() if email else ""
#         telefono = telefono.strip() if telefono else ""
#         rol = rol.strip().title() if rol else "Empleado"
#         hash_contrasena = generate_password_hash(contrasena)

#         sql = """
#             INSERT INTO empleado (nombre_usuario, mail, telefono, contrasena, tipo, activo) 
#             VALUES (%s, %s, %s, %s, %s, 1)
#         """
#         conexion = Config.conectar_db()
#         try:
#             with conexion.cursor() as cursor:
#                 valores = (nombre, email, telefono, hash_contrasena, rol)
#                 cursor.execute(sql, valores)
#                 conexion.commit()

#             print("Empleado guardado correctamente")
#             return True

#         except pymysql.MySQLError as e:
#             conexion.rollback()
#             print(f"Error al crear empleado: {e}")
#             return False

#         finally:
#             conexion.close()