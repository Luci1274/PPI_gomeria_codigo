# Caso de uso: Completar o dar de baja una compra

# Actores
- Administrador o desarrollador.

# Precondiciones
- La compra existe y está disponible en el listado.
- Para completar: la compra está activa e incompleta.
- Para anular: la compra está activa.

# Camino básico de recepción
1. El usuario selecciona Completar en una compra activa e incompleta.
2. El sistema muestra las cantidades pedidas y permite ingresar las recibidas.
3. El usuario confirma.
4. El sistema valida todos los ítems, cantidades no negativas y ausencia de duplicados.
5. En una transacción, guarda las cantidades entregadas, actualiza el stock y marca `completo = 1`.

# Camino básico de baja
1. El usuario solicita anular una compra.
2. Confirma la operación.
3. El sistema cambia `activo` a `0`.
4. Si la compra estaba completa, descuenta del stock las cantidades entregadas.
5. Si estaba incompleta, no modifica el stock.

# Caminos alternativos
1.A Compra ya anulada o completa
   - El sistema rechaza la operación y no aplica cambios.

1.B Cantidad recibida inválida
   - El usuario debe ingresar cantidades enteras no negativas.

1.C Anulación cancelada
   - Se conserva el estado anterior.

# Postcondiciones
- La compra completada queda activa y cerrada.
- La compra anulada conserva su historial y cambia a `activo = 0`.
- Las cantidades recibidas se revierten solo cuando corresponden a una compra completa.

# Escenarios de éxito
- El stock aumenta con cantidades recibidas válidas.
- La compra anulada refleja baja lógica y stock coherente.

# Escenarios de fracaso
- Datos incompletos o conflicto de estado: `400`.
- Error de base de datos o transacción: `500`.
