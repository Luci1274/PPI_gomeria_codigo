# Caso de uso: Modificar proveedor

# Actores
- Administrador o desarrollador.

# Precondiciones
- El proveedor existe.
- El usuario inició sesión con permiso de proveedores.

# Camino básico
1. El usuario selecciona un proveedor en el listado.
2. Solicita modificar.
3. El sistema carga los datos actuales.
4. El usuario cambia nombre, CUIT, teléfono, correo, rubro, ciudad o dirección.
5. El sistema valida los campos.
6. Comprueba que el CUIT nuevo no pertenezca a otro proveedor.
7. Guarda los cambios y actualiza el listado.

# Caminos alternativos
1.A Datos inválidos
   - El sistema responde `400` y conserva los datos originales.

1.B CUIT duplicado
   - El sistema responde `409`.

1.C Proveedor inexistente
   - El sistema responde `404`.

# Postcondiciones
- Los datos nuevos quedan persistidos.
- Las compras anteriores conservan la relación con el proveedor.

# Escenarios de éxito
- Se modifica el proveedor y se muestra confirmación.

# Escenarios de fracaso
- Datos inválidos, proveedor inexistente o CUIT duplicado.
- Error de base de datos: `500`.
