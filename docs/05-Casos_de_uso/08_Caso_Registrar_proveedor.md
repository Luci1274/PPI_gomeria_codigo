# Caso de uso: Registrar proveedor

# Actores
- Administrador o desarrollador.

# Precondiciones
- El usuario inició sesión con permiso de proveedores.

# Camino básico
1. El usuario abre el formulario de alta.
2. Ingresa nombre, CUIT, teléfono, correo, rubro, ciudad y dirección.
3. El sistema recorta espacios y normaliza rubro y ciudad.
4. Valida nombre, CUIT y rubro; nombre y CUIT son obligatorios.
5. Comprueba que el CUIT no exista.
6. Crea el proveedor con `activo = 1`.
7. Muestra confirmación y actualiza filtros.

# Caminos alternativos
1.A CUIT duplicado
   - El sistema responde `409` y no crea el proveedor.

1.B Campos inválidos o JSON ausente
   - El sistema responde `400`.

1.C Rubro vacío
   - El sistema rechaza el campo vacío si fue enviado explícitamente.

# Postcondiciones
- El proveedor queda activo y disponible para nuevas compras.

# Escenarios de éxito
- Se registra un proveedor válido y se muestra su confirmación.

# Escenarios de fracaso
- Datos inválidos: `400`.
- CUIT duplicado: `409`.
- Error de persistencia: `500`.
