# Caso de uso: Gestionar clientes

# Actores
- Administrador o desarrollador.

# Precondiciones
- El usuario inició sesión con permiso de gestión de clientes.

# Camino básico de alta
1. El usuario abre `/clientes`.
2. Selecciona agregar o registrar cliente.
3. Ingresa nombre completo, CUIT/DNI, teléfono, correo, ciudad y dirección.
4. Confirma el formulario.
5. El sistema crea el cliente con `activo = 1`.
6. El sistema actualiza tabla, filtros y ciudades disponibles.

# Camino básico de consulta y edición
1. El usuario busca por nombre, apellido o CUIT.
2. Puede filtrar por ciudad y estado.
3. Selecciona un cliente activo y abre edición.
4. Modifica los datos disponibles y guarda.
5. El sistema actualiza el registro y vuelve a cargar el listado.

# Caminos alternativos
1.A El usuario desactiva un cliente
   - Confirma la operación.
   - El sistema cambia `activo` a `0`.
   - El cliente permanece disponible al filtrar inactivos o todos.

1.B El usuario reactiva un cliente
   - El sistema cambia `activo` a `1`.

1.C Datos sin validar
   - El código actual no aplica validaciones completas de formato ni unicidad en cada ruta.
   - El usuario debe resolver errores devueltos por la base o por el cliente.

# Postcondiciones
- Los cambios quedan registrados con baja lógica cuando corresponde.
- Las ciudades disponibles se derivan de los clientes existentes.
- La deuda mostrada se calcula desde ventas activas y pagos incompletos.

# Escenarios de éxito
- Se crea, modifica, desactiva o reactiva un cliente válido.
- El listado refleja los filtros y el estado.

# Escenarios de fracaso
- Falla la consulta o persistencia: `500`.
- Una operación de cambio de estado no encuentra el estado esperado: `400`.
