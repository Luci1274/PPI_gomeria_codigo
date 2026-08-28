from werkzeug.security import generate_password_hash, check_password_hash
from modulos.comandos_db.conexion import conectar_db
import pymysql

class Usuario:
    def __init__(self, nombre=None, correo=None, telefono=None, contrasena=None, tipo="Empleado", id_usuario=None):
        self.__id_usuario = id_usuario
        self.__nombre = nombre
        self.__correo = correo
        self.__telefono = telefono
        self.__contrasena = contrasena
        self.__tipo = tipo

    @staticmethod
    def hash_contraseña(contraseña):
        return generate_password_hash(contraseña)

    @staticmethod
    def verificar_credenciales(nombre_ingresado, contrasena_ingresada):
        """Verifica si las credenciales coinciden con las almacenadas en la base de datos."""
        conexion = conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT idempleado, nombre_usuario, contrasena, tipo FROM empleado WHERE nombre_usuario = %s AND activo = 1"
                cursor.execute(sql, (nombre_ingresado,))
                usuario = cursor.fetchone()

                if usuario and check_password_hash(usuario.get("contrasena") or usuario.get("contraseña"), contrasena_ingresada):
                    return [usuario["idempleado"], usuario["tipo"]]
                return None
        except pymysql.MySQLError as e:
            print(f"Error al verificar las credenciales: {e}")
            return False
        finally:
            conexion.close()

    def crear_usuario(self):
        """Inserta un nuevo empleado en la base de datos."""
        conexion = conectar_db()
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
        conexion = conectar_db()
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

    # Alias por compatibilidad
    no_repetir = existe_usuario

    @staticmethod
    def leer_usuarios():
        """Devuelve todos los usuarios activos de la base de datos."""
        conexion = conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT idempleado, nombre_usuario, mail, telefono, tipo FROM empleado WHERE activo = 1"
                cursor.execute(sql)
                return cursor.fetchall()
        except pymysql.MySQLError as e:
            print(f"Error al leer los usuarios: {e}")
            return []
        finally:
            conexion.close()

    @staticmethod
    def leer_usuario(id_usuario):
        """Obtiene la información de un empleado específico por su ID."""
        conexion = conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT idempleado, nombre_usuario, mail, telefono, tipo FROM empleado WHERE idempleado = %s"
                cursor.execute(sql, (id_usuario,))
                return cursor.fetchone()
        except pymysql.MySQLError as e:
            print(f"Error al leer el usuario: {e}")
            return None
        finally:
            conexion.close()

    def actualizar_usuario(self, nueva_contrasena=None):
        """Actualiza los datos personales y/o la contraseña de un empleado."""
        conexion = conectar_db()
        try:
            with conexion.cursor() as cursor:
                if nueva_contrasena:
                    hash_contrasena = self.hash_contraseña(nueva_contrasena)
                    sql = "UPDATE empleado SET nombre_usuario = %s, mail = %s, telefono = %s, contrasena = %s, tipo = %s WHERE idempleado = %s"
                    valores = (self.__nombre, self.__correo, self.__telefono, hash_contrasena, self.__tipo, self.__id_usuario)
                else:
                    sql = "UPDATE empleado SET nombre_usuario = %s, mail = %s, telefono = %s, tipo = %s WHERE idempleado = %s"
                    valores = (self.__nombre, self.__correo, self.__telefono, self.__tipo, self.__id_usuario)
                
                cursor.execute(sql, valores)
                conexion.commit()
                return True
        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al actualizar el usuario: {e}")
            return False
        finally:
            conexion.close()

    @staticmethod
    def eliminar_usuario(id_usuario):
        """Aplica la baja lógica del usuario (activo = 0)."""
        conexion = conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE empleado SET activo = 0 WHERE idempleado = %s"
                cursor.execute(sql, (id_usuario,))
                conexion.commit()
                return True
        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al eliminar el usuario: {e}")
            return False
        finally:
            conexion.close()