from werkzeug.security import generate_password_hash, check_password_hash
from modulos.comandos_db.conexion import conectar_db
import pymysql

class Usuario:
    def __init__(self, id_usuario = None, nombre = None, correo = None, telefono = None, contrasena = None, tipo = "Empleado"):
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
    def verificar_credenciales(self, nombre_ingresado, contrasena_ingresada):
        """Verifica si las credenciales ingresadas coinciden con las almacenadas en la base de datos.
        Esto es para el login de los empleados"""
        conexion = conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT idempleado, nombre_usuario, contraseña, tipo FROM empleado WHERE nombre_usuario = %s AND activo = 1"
                cursor.execute(sql, (nombre_ingresado,))
                usuario = cursor.fetchone()
                
                if usuario and check_password_hash(usuario["contraseña"], contrasena_ingresada):
                    datos_devolver = [usuario["idempleado"], usuario["tipo"]]
                    return datos_devolver
                else:
                    return None
        except pymysql.MySQLError as e:
            print(f"Error al verificar las credenciales: {e}")
            return False
        finally:
            conexion.close()
            
        
    
    def crear_usuario(self):
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
        
        finally:
            conexion.close()
    
    @staticmethod
    def existe_usuario(self, nombre_usuario):
        conexion = conectar_db()
        """Comprobar la no existencia del usuario"""
        try:
            with conexion.cursor() as cursor:        
                buscar_nombre = "SELECT nombre_usuario FROM empleado WHERE nombre_usuario = %s"
                cursor.execute(buscar_nombre,(nombre_usuario))
                nombre_db = cursor.fetchone()
                if nombre_db == nombre_usuario:
                    return True
                else:
                    return False
        except pymysql.MySQLError as e:
            print(f"Error al intentar verificar la no existencia del usuario a crear: {e}")
            return False
        finally:
            conexion.close()
        
    @staticmethod        
    def leer_usuarios(self):
        """Lee todos los usuarios de la base de datos y los devuelve en un diccionario.
        Esto sirve para gestion de usuarios"""
        conecxion = conectar_db()
        try:
            with conecxion.cursor() as cursor:
                sql = "SELECT idempleado, nombre_usuario, mail, telefono, tipo FROM empleado WHERE activo = 1"
                cursor.execute(sql)
                conecxion.commit()
                resultados = cursor.fetchall()
                return resultados
        except pymysql.MySQLError as e:
            print(f"Error al leer los usuarios: {e}")
            return []
        finally:
            conecxion.close()
            
    @staticmethod
    def leer_usuario(self, id):
        """Lee un usuario de la base de datos y lo devuelve en un diccionario.
        Esto sirve para el momento de edicion de un usuario"""
        conexion = conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = "SELECT idempleado, nombre_usuario, mail, telefono, tipo FROM empleado WHERE idempleado = %s"
                cursor.execute(sql, (id,))
                resultado = cursor.fetchone()
                return resultado
        except pymysql.MySQLError as e:
            print(f"Error al leer el usuario: {e}")
            conexion.rollback()
            return None
        finally:
            conexion.close()
            
    def actualizar_usuario(self, nueva_contrasena = None):
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
    def eliminar_usuario(self, id):
        conexion = conectar_db()
        try:
            with conexion.cursor() as cursor:
                sql = "UPDATE empleado SET activo = 0 WHERE idempleado = %s"
                cursor.execute(sql, (id,))
                conexion.commit()
                return True
        except pymysql.MySQLError as e:
            conexion.rollback()
            print(f"Error al eliminar el usuario: {e}")
            return False
        finally:
            conexion.close()