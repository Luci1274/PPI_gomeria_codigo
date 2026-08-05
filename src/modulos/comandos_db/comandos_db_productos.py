from modulos.conexion import conectar_db
#----------------------------------------------------------------------------
def sql_leer_productos(tipo=None, busqueda=None):
    """Lee los productos activos de la base de datos."""
    """Tipo: permite filtrar por categoria, Busqueda: permite buscar por texto ingresado en la barra de busqueda"""
    
    conexion = conectar_db()
    try:
        with conexion.cursor() as cursor:
            sql = ("SELECT p.idproducto_servicio, p.nombre, p.tipo, p.precio, p.imagen_producto, p.cantidad_actual FROM producto_servicio AS p WHERE activo = 1;")
            
            parametros = []
            
            if tipo:
                sql += "AND tipo = %s"
                parametros.append(tipo)
                
            if busqueda:
                sql += "AND (nombre LIKE %s)"
                parametros.append(busqueda)
            
            cursor.execute(sql, parametros)
            return cursor.fetchall()
        
    except Exception as e:
        print(f"Error al consultar productos: {e}")
        return []
    finally:
        conexion.close()
#----------------------------------------------------------------------------
def sql_leer_producto(id):
    """Busca el producto por el id y lo devuelve"""
    conexion = conectar_db()
    
    try:
        with conexion.cursor() as cursor:
            sql = ("SELECT idproducto_servicio, nombre, tipo, marca, medidas, imagen_producto, cantidad_actual, cantidad_minima, precio FROM producto_servicio WHERE idproducto_servicio = %s;")
            valor = (id,)
            
            cursor.execute(sql, valor)
            return cursor.fetchone()
    except Exception as e:
        print(f"Error al consulta el producto: {e}")
        return None

    finally:
        conexion.close()
#----------------------------------------------------------------------------    
def sql_leer_tipo():
    """Lee el tipo de los productos y servicios para el filtro"""
    
    conexion = conectar_db()
    
    try:
        with conexion.cursor() as cursor:
            sql = ("SELECT DISTINCT tipo FROM producto_servicio WHERE activo = 1;")

            cursor.execute(sql)
            return cursor.fetchall()
    
    except Exception as e:
        print(f"Error al consultar los tipos (categorias): {e}")
        return[]
    
    finally:
        conexion.close()
#----------------------------------------------------------------------------