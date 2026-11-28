# Caso de uso: Listar compras

# Actores
- Administrador o desarrollador.

# Precondiciones
- El usuario inició sesión y tiene permiso de gestión de compras.
- Existe al menos una compra o el usuario acepta una lista sin resultados.

# Camino básico
1. El usuario abre la pantalla `/compras`.
2. El sistema carga el listado con fecha de hoy, todos los estados y órdenes incompletas.
3. El usuario puede buscar por número de compra o proveedor.
4. El usuario puede filtrar por fecha, estado activo/anulado y recepción completa/incompleta.
5. El sistema solicita `/api/compras` y muestra la tabla paginada.
6. El sistema muestra totales de compras y unidades sobre todos los registros que coinciden con los filtros.
7. El usuario selecciona una compra para ver su detalle.
8. El sistema muestra la cabecera y los ítems pedidos/recibidos.
9. El usuario puede descargar el resumen en PDF.

# Caminos alternativos
1.A Sin coincidencias
   - El sistema muestra una tabla vacía y permite modificar o limpiar los filtros.

1.B Rango de fechas manual
   - La API acepta `fecha_inicio` y `fecha_fin`. Deben enviarse juntas y prevalecen sobre el filtro `filtro_fecha`.

1.C Completar una compra
   - Una compra activa e incompleta ofrece la acción Completar.
   - El sistema abre el detalle en modo recepción y permite ingresar cantidades recibidas.

1.D Anular una compra
   - El usuario solicita la baja desde el listado.
   - Confirma la operación; si ya estaba anulada, el sistema rechaza la solicitud.

# Postcondiciones
- La interfaz refleja los filtros y la paginación vigentes.
- La anulación o recepción completada cambia la visualización después de actualizar el listado.

# Escenarios de éxito
- El usuario navega filtros y páginas sin errores.
- La compra seleccionada muestra sus datos y líneas.
- Las métricas corresponden al conjunto filtrado.

# Escenarios de fracaso
- La consulta falla y la API responde `500`.
- Los parámetros inválidos responden `400`.
- No hay resultados que coincidan y el sistema muestra el estado vacío.