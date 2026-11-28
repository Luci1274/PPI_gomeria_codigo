# Caso de uso: Registrar venta

# Actores
- Administrador, desarrollador o empleado autorizado.

# Precondiciones
- Hay al menos un producto o servicio activo.
- Hay un método de pago activo.
- Existe la cuenta del cliente consumidor final.
- El usuario inició sesión.

# Camino básico
1. El usuario abre `/ventas/realizar`.
2. El sistema carga catálogo, tipos, clientes y métodos de pago activos.
3. El usuario busca productos o servicios y agrega ítems al carrito.
4. Cada ítem especifica si es producto o servicio, su identificador y cantidad.
5. El usuario selecciona cliente y método de pago.
6. El usuario puede ingresar un descuento monetario fijo.
7. El sistema verifica que el descuento no supere el subtotal mostrado.
8. El usuario confirma la venta.
9. El servidor vuelve a cargar precios vigentes y bloquea los productos.
10. El servidor verifica stock, cliente, método de pago y datos del carrito.
11. El sistema registra cabecera, ítems y pago en una transacción.
12. Descuenta el stock de productos y redirige al listado.

# Caminos alternativos
1.A Precio o stock cambiaron
   - El servidor responde `409`.
   - La operación no se guarda y el usuario debe reconstruir o actualizar el carrito.

1.B Producto o servicio ya no existe
   - El sistema rechaza la operación o deja de restaurarlo al reconstruir el carrito.

1.C Cancelar o quitar ítems
   - El navegador modifica únicamente el carrito local.

1.D Navegar a inventario
   - El carrito y descuento se guardan temporalmente en `localStorage`.
   - Al regresar se reconstruyen con los precios vigentes.

# Postcondiciones
- La venta queda activa y pagada en el flujo actual.
- El stock disminuye solo para productos.
- Los servicios no modifican stock.
- Se registra un pago por el total confirmado y plazo `0`.

# Escenarios de éxito
- La venta confirma datos coherentes y guarda todos los detalles.
- El usuario puede ver el comprobante o imprimirlo como PDF.

# Escenarios de fracaso
- Carrito vacío, cantidad inválida o método ausente: `400`.
- Cambios de precio o stock insuficiente: `409`.
- Fallo de persistencia: `500`.
