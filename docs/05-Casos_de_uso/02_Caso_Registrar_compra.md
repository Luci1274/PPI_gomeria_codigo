# Caso de uso: Registrar compra

# Actores
- Administrador o desarrollador.

# Precondiciones
- Existe al menos un proveedor activo.
- Existe al menos un producto activo en el catálogo.
- La sesión tiene permiso para compras.

# Camino básico
1. El usuario abre `/compras/realizar`.
2. El sistema carga productos activos, tipos activos y proveedores activos.
3. El usuario busca o filtra productos y agrega cantidades al carrito.
4. El usuario selecciona un proveedor.
5. El usuario confirma el resumen de la compra.
6. El navegador envía `POST /api/compras/realizar` con proveedor e ítems.
7. El sistema valida proveedor, identificadores y cantidades positivas.
8. El sistema crea una compra activa e incompleta y sus líneas.
9. El sistema informa el ID generado y redirige al listado.

# Caminos alternativos
1.A Se navega al listado de proveedores
   - El carrito se conserva en `localStorage`.
   - Al volver, solo se restauran productos que siguen disponibles y cantidades válidas.

1.B Datos inválidos
   - El sistema rechaza proveedores no activos, cantidades negativas o cero y carritos vacíos con `400`.

1.C Confirmación cancelada
   - El proceso termina sin crear cabecera ni líneas.

# Postcondiciones
- La compra queda registrada con `activo = 1` y `completo = 0`.
- Las cantidades pedidas se suman en `compra.cantidad_total`.
- El stock no cambia al registrar la orden.
- No se registra forma de pago ni precio de costo por línea.

# Escenarios de éxito
- Se crea una compra válida con uno o más productos.
- El usuario puede completarla o verla como incompleta.

# Escenarios de fracaso
- Faltan datos o hay cantidades inválidas: `400`.
- El proveedor o productos no cumplen las condiciones esperadas: rechazo de operación.
- Falla la persistencia: `500`.