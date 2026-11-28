# Caso de uso: Gestionar productos y servicios

# Actores
- Administrador o desarrollador.

# Precondiciones
- El usuario inició sesión con permiso de inventario.

# Camino básico de producto
1. El usuario abre `/inventario`.
2. Selecciona crear producto.
3. Ingresa nombre, tipo, marca, medidas, stock actual, stock mínimo, precio e imagen opcional.
4. El servidor valida cantidades y precio.
5. El sistema reutiliza o crea el tipo y guarda el producto activo.
6. Si corresponde, carga la imagen en Cloudinary.

# Camino básico de servicio
1. El usuario selecciona crear servicio.
2. Ingresa nombre, tipo y precio.
3. El sistema valida los datos y guarda el servicio activo sin stock.

# Camino básico de consulta/modificación
1. El usuario filtra por búsqueda, tipo, marca, estado y stock bajo.
2. Selecciona un artículo activo y modifica sus datos.
3. El sistema actualiza el artículo y conserva la imagen existente si no se adjunta una nueva.

# Caminos alternativos
1.A Producto duplicado
   - El sistema detecta coincidencia por nombre, tipo, marca y medidas y responde `409`.

1.B Servicio duplicado
   - El sistema detecta coincidencia por nombre y responde `409`.

1.C Baja o reactivación
   - El usuario desactiva o reactiva el artículo; no se elimina físicamente.

1.D Stock bajo
   - El listado incluye productos con `cantidad_actual < cantidad_minima`.
   - Los servicios no aparecen en este filtro.

# Postcondiciones
- El catálogo conserva los cambios de tipos, marcas y estados.
- Los productos mantienen stock y umbral mínimo.
- Los servicios quedan sin inventario propio.

# Escenarios de éxito
- Alta, edición, baja o reactivación exitosa.
- Las ventas descuentan productos y no modifican servicios.

# Escenarios de fracaso
- Datos inválidos o imagen fallida: `400`.
- Duplicado: `409`.
- Error de persistencia o consulta: `500`.
