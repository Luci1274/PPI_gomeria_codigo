# Caso de uso: Listar proveedores

# Actores
- Administrador o desarrollador.

# Precondiciones
- El usuario inició sesión con permiso de gestión de proveedores.

# Camino básico
1. El usuario abre `/proveedores`.
2. Puede buscar por nombre o CUIT.
3. Puede combinar filtros de rubro, ciudad y estado.
4. El sistema solicita `/api/proveedores`.
5. Muestra proveedores paginados y actualiza las opciones de rubro y ciudad.
6. El usuario puede seleccionar modificar, desactivar o activar.
7. Las operaciones actualizan la lista y los filtros disponibles.

# Caminos alternativos
1.A Sin resultados
   - El sistema muestra el estado vacío y permite limpiar filtros.

1.B Página inválida
   - La API rechaza páginas menores que uno con `400`.

# Postcondiciones
- El listado refleja filtros y estado sin eliminar registros.
- Los proveedores inactivos siguen disponibles en el historial de compras.

# Escenarios de éxito
- El usuario puede buscar, filtrar y navegar proveedores.

# Escenarios de fracaso
- Parámetro inválido: `400`.
- Error de base de datos: `500`.
