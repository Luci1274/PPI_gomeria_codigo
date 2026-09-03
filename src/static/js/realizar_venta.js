document.addEventListener('DOMContentLoaded', () => {
    let carrito = [];
    let filtroTipoActual = 'todos';

    // Referencias al DOM
    const listaCarrito = document.getElementById('lista_carrito');
    const totalVentaElem = document.getElementById('total_venta');
    const inputDescuento = document.getElementById('input_descuento');
    const selectCliente = document.getElementById('select_cliente');
    const btnConfirmarVenta = document.getElementById('btn_confirmar_venta');
    const contenedorProductos = document.querySelector('.contenedor_grilla_productos');
    
    // Elementos de Filtrado y Búsqueda
    const inputBusqueda = document.querySelector('input[name="busqueda"]');
    const botonesTipo = document.querySelectorAll('.btn_tipo');

    // ----------------------------------------------------
    // 1. FILTRADO Y BÚSQUEDA EN TIEMPO REAL
    // ----------------------------------------------------
    function aplicarFiltros() {
        const tarjetas = document.querySelectorAll('.tarjeta_producto');
        const textoBusqueda = inputBusqueda ? inputBusqueda.value.toLowerCase().trim() : '';

        tarjetas.forEach(tarjeta => {
            const nombre = (tarjeta.dataset.nombre || '').toLowerCase();
            const tipo = (tarjeta.dataset.tipo || '').toLowerCase();

            const coincideNombre = nombre.includes(textoBusqueda);
            const coincideTipo = (filtroTipoActual === 'todos' || tipo === filtroTipoActual.toLowerCase());

            if (coincideNombre && coincideTipo) {
                tarjeta.style.display = '';
            } else {
                tarjeta.style.display = 'none';
            }
        });
    }

    if (inputBusqueda) {
        inputBusqueda.addEventListener('input', aplicarFiltros);
        // Evitar que la tecla Enter recargue la página si está en un form
        inputBusqueda.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') e.preventDefault();
        });
    }

    if (botonesTipo.length > 0) {
        botonesTipo.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                botonesTipo.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                filtroTipoActual = btn.dataset.tipo || 'todos';
                aplicarFiltros();
            });
        });
    }

    // ----------------------------------------------------
    // 2. GESTIÓN DE PRODUCTOS Y CARRITO
    // ----------------------------------------------------
    if (contenedorProductos) {
        contenedorProductos.addEventListener('click', (e) => {
            const tarjeta = e.target.closest('.tarjeta_producto');
            if (!tarjeta) return;

            const id = tarjeta.dataset.id;
            const nombre = tarjeta.dataset.nombre;
            const precio = parseFloat(tarjeta.dataset.precio);

            if (!id) return;
            agregarAlCarrito({ id, nombre, precio });
        });
    }

    function agregarAlCarrito(producto) {
        const itemExistente = carrito.find(item => String(item.idproducto_servicio) === String(producto.id));

        if (itemExistente) {
            itemExistente.cantidad += 1;
        } else {
            carrito.push({
                idproducto_servicio: producto.id,
                nombre: producto.nombre,
                precio_unitario: producto.precio,
                cantidad: 1
            });
        }

        renderizarCarrito();
    }

    // ----------------------------------------------------
    // 3. CÁLCULO DE TOTALES (SUBTOTAL - DESCUENTO)
    // ----------------------------------------------------
    function calcularTotales() {
        const subtotal = carrito.reduce((acc, item) => acc + (item.precio_unitario * item.cantidad), 0);

        let descuento = 0;
        if (inputDescuento && inputDescuento.value) {
            descuento = parseInt(inputDescuento.value, 10) || 0;
            if (descuento < 0) descuento = 0; // Prevenir números negativos
        }

        const totalFinal = Math.max(0, subtotal - descuento);
        return { subtotal, descuento, totalFinal };
    }

    function renderizarCarrito() {
        if (!listaCarrito || !totalVentaElem) return;

        if (carrito.length === 0) {
            listaCarrito.innerHTML = '<p class="carrito_vacio">No hay productos agregados a la venta.</p>';
            totalVentaElem.textContent = '0.00';
            return;
        }

        listaCarrito.innerHTML = '';

        carrito.forEach(item => {
            const subtotalItem = item.precio_unitario * item.cantidad;

            const itemDiv = document.createElement('div');
            itemDiv.classList.add('item_carrito');
            itemDiv.innerHTML = `
                <div class="info_item">
                    <p class="nombre_item"><strong>${item.nombre}</strong></p>
                    <p class="subtotal_item">$${item.precio_unitario.toFixed(2)} x ${item.cantidad} = $${subtotalItem.toFixed(2)}</p>
                </div>
                <div class="acciones_item">
                    <button type="button" class="btn_decrementar" data-id="${item.idproducto_servicio}">-</button>
                    <span>${item.cantidad}</span>
                    <button type="button" class="btn_incrementar" data-id="${item.idproducto_servicio}">+</button>
                    <button type="button" class="btn_eliminar" data-id="${item.idproducto_servicio}">&times;</button>
                </div>
            `;
            listaCarrito.appendChild(itemDiv);
        });

        const { totalFinal } = calcularTotales();
        totalVentaElem.textContent = totalFinal.toFixed(2);
    }

    // Recalcular total cuando se escribe un descuento
    if (inputDescuento) {
        inputDescuento.addEventListener('input', () => {
            const { totalFinal } = calcularTotales();
            totalVentaElem.textContent = totalFinal.toFixed(2);
        });
    }

    // Controles dentro de las tarjetas del carrito (+, -, eliminar)
    if (listaCarrito) {
        listaCarrito.addEventListener('click', (e) => {
            const id = e.target.dataset.id;
            if (!id) return;

            const item = carrito.find(i => String(i.idproducto_servicio) === String(id));

            if (e.target.classList.contains('btn_incrementar')) {
                if (item) item.cantidad += 1;
            } else if (e.target.classList.contains('btn_decrementar')) {
                if (item) {
                    item.cantidad -= 1;
                    if (item.cantidad <= 0) {
                        carrito = carrito.filter(i => String(i.idproducto_servicio) !== String(id));
                    }
                }
            } else if (e.target.classList.contains('btn_eliminar')) {
                carrito = carrito.filter(i => String(i.idproducto_servicio) !== String(id));
            }

            renderizarCarrito();
        });
    }

    // ----------------------------------------------------
    // 4. CONFIRMAR Y ENVIAR VENTA
    // ----------------------------------------------------
    if (btnConfirmarVenta) {
        btnConfirmarVenta.addEventListener('click', async () => {
            if (carrito.length === 0) {
                alert('Debe agregar al menos un producto para realizar la venta.');
                return;
            }

            const idCliente = selectCliente && selectCliente.value !== "" ? selectCliente.value : null;
            const { descuento } = calcularTotales();

            const payload = {
                id_cliente: idCliente,
                carrito: carrito,
                descuento: descuento,
                numero_factura: null
            };

            try {
                btnConfirmarVenta.disabled = true;
                btnConfirmarVenta.textContent = 'Procesando...';

                const respuesta = await fetch('/api/ventas/realizar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const resultado = await respuesta.json();

                if (respuesta.ok && resultado.exito) {
                    alert(resultado.mensaje || 'Venta realizada con éxito.');
                    if (resultado.redireccion) {
                        window.location.href = resultado.redireccion;
                    } else {
                        carrito = [];
                        if (inputDescuento) inputDescuento.value = '';
                        renderizarCarrito();
                    }
                } else {
                    alert(resultado.mensaje || 'Error al procesar la venta.');
                }
            } catch (error) {
                console.error('Error en la petición:', error);
                alert('Ocurrió un error de red al intentar procesar la venta.');
            } finally {
                btnConfirmarVenta.disabled = false;
                btnConfirmarVenta.textContent = 'Confirmar Venta';
            }
        });
    }
});