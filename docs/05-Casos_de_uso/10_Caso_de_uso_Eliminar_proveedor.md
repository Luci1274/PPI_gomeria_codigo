# Caso de uso: Dar de baja proveedor

# Actores
- Administrador o desarrollador.

# Precondiciones
- El proveedor existe y está activo.
- El usuario inició sesión con permiso de proveedores.

# Camino básico
1. El usuario solicita desactivar un proveedor activo.
2. El sistema pide confirmación.
3. El usuario confirma.
4. El sistema cambia `activo` a `0`.
5. El proveedor deja de ofrecerse para nuevas compras.
6. El sistema actualiza el listado.

# Caminos alternativos
1.A El usuario cancela
   - No cambia el estado.

1.B El proveedor ya está inactivo
   - La operación de desactivación informa que no encontró el estado esperado.

1.C Reactivación
   - El usuario solicita activar.
   - El sistema cambia `activo` a `1`.

# Postcondiciones
- El proveedor queda inactivo o activo según la operación.
- No se elimina físicamente ni se pierde su relación con compras históricas.

# Escenarios de éxito
- Se desactiva o reactiva correctamente.

# Escenarios de fracaso
- Estado no coincidente: `404` para desactivar según la API actual.
- Error de base de datos: `500`.
