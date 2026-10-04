document.addEventListener('DOMContentLoaded', () => {
    const cartelEmergente = document.getElementById('cartel-emergente');
    const cartelTitulo = document.getElementById('cartel-titulo');
    const cartelMensaje = document.getElementById('cartel-mensaje');
    const claveCarrito = 'ordenVentaCarrito';
    let timerNotificacion;

    // ==========================================
    // 1. INICIALIZACIÓN Y FECHA ACTUAL
    // ==========================================
    const selectCliente = document.getElementById('select-cliente');
    const spanFecha = document.getElementById('fecha-actual');

    if (selectCliente && !selectCliente.value) {
        selectCliente.value = "1"; // Consumidor Final por defecto
    }

    if (spanFecha) {
        const hoy = new Date();
        spanFecha.textContent = hoy.toLocaleDateString('es-AR');
    }

    // ==========================================
    // 2. FILTRADO POR BÚSQUEDA Y CATEGORÍA
    // ==========================================
    const inputBuscar = document.getElementById('buscar-producto');
    const selectCategoria = document.getElementById('select-categoria');

    function filtrarProductos() {
        const textoBusqueda = inputBuscar ? inputBuscar.value.toLowerCase().trim() : '';
        const categoriaSeleccionada = selectCategoria ? selectCategoria.value.toLowerCase() : 'todos';

        document.querySelectorAll('.tarjeta-producto').forEach(tarjeta => {
            const nombre = tarjeta.dataset.nombre.toLowerCase();
            const tipo = (tarjeta.dataset.tipo || '').toLowerCase();

            const coincideNombre = nombre.includes(textoBusqueda);
            const coincideCategoria = categoriaSeleccionada === 'todos' || tipo === categoriaSeleccionada;

            if (coincideNombre && coincideCategoria) {
                tarjeta.style.display = 'flex';
            } else {
                tarjeta.style.display = 'none';
            }
        });
    }

    if (inputBuscar) inputBuscar.addEventListener('input', filtrarProductos);
    if (selectCategoria) selectCategoria.addEventListener('change', filtrarProductos);

    // ==========================================
    // 3. LÓGICA DEL CARRITO DE COMPRAS
    // ==========================================
    let carrito = [];

    function restaurarCarrito() {
        let carritoGuardado;
        try {
            const datosGuardados = localStorage.getItem(claveCarrito);
            if (!datosGuardados) return;
            carritoGuardado = JSON.parse(datosGuardados);
        } catch (error) {
            console.error('No se pudo leer el carrito guardado:', error);
            mostrarNotificacion('Aviso', 'No se pudo recuperar el pedido guardado.');
            return;
        }

        if (!Array.isArray(carritoGuardado)) {
            mostrarNotificacion('Aviso', 'El pedido guardado no tiene un formato válido.');
            return;
        }

        const tarjetasPorId = new Map(
            Array.from(document.querySelectorAll('.tarjeta-producto'))
                .map(tarjeta => [Number(tarjeta.dataset.id), tarjeta])
        );

        carrito = carritoGuardado.reduce((items, guardado) => {
            const id = Number(guardado?.idproducto_servicio);
            const cantidad = Number(guardado?.cantidad);
            const tarjeta = tarjetasPorId.get(id);
            const precio = Number(tarjeta?.dataset.precio);

            if (!tarjeta || !Number.isSafeInteger(cantidad) || cantidad <= 0 || !Number.isFinite(precio)) {
                return items;
            }

            items.push({
                idproducto_servicio: id,
                nombre: tarjeta.dataset.nombre || 'Producto',
                precio_unitario: precio,
                cantidad
            });
            return items;
        }, []);

        if (carrito.length !== carritoGuardado.length) {
            mostrarNotificacion('Aviso', 'Se restauraron los productos válidos del pedido guardado.');
        }
    }

    document.querySelectorAll('.tarjeta-producto').forEach(tarjeta => {
        tarjeta.addEventListener('click', () => {
            const id = parseInt(tarjeta.dataset.id);
            const nombre = tarjeta.dataset.nombre;
            const precio = parseFloat(tarjeta.dataset.precio);

            const productoExistente = carrito.find(item => item.idproducto_servicio === id);

            if (productoExistente) {
                productoExistente.cantidad += 1;
            } else {
                carrito.push({
                    idproducto_servicio: id,
                    nombre: nombre,
                    precio_unitario: precio,
                    cantidad: 1
                });
            }

            actualizarResumen();
            mostrarNotificacion('¡Añadido!', 'Producto agregado al pedido.', 2000);
        });
    });

    function actualizarResumen() {
        const contenedorLista = document.getElementById('lista-resumen');
        const totalElemento = document.getElementById('monto-total');
        
        if (!contenedorLista) return;

        contenedorLista.innerHTML = '';
        let total = 0;

        carrito.forEach((item, index) => {
            const subtotal = item.precio_unitario * item.cantidad;
            total += subtotal;

            const itemHTML = `
                <div class="item-pedido">
                    <div class="detalles-item">
                        <strong>${item.nombre}</strong>
                        <span class="cant-item">Cant: ${item.cantidad}</span>
                        <span class="precio-item">$${subtotal.toFixed(2)}</span>
                        <button type="button" class="btn-eliminar" data-index="${index}">✕</button>
                    </div>
                </div>
            `;
            contenedorLista.insertAdjacentHTML('beforeend', itemHTML);
        });

        if (totalElemento) {
            totalElemento.textContent = `$${total.toFixed(2)}`;
        }

        contenedorLista.querySelectorAll('.btn-eliminar').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const idx = parseInt(btn.dataset.index);
                eliminarDelCarrito(idx);
            });
        });
    }

    function eliminarDelCarrito(index) {
        carrito.splice(index, 1);
        actualizarResumen();
    }

    // ==========================================
    // 4. CONTROL DEL MODAL Y RENDERIZADO DETALLADO
    // ==========================================
    const modal = document.getElementById('modal-overlay');
    const btnOpenModal = document.getElementById('btn-open-modal');
    const btnCerrarModal = document.getElementById('btn-cerrar-modal');
    const btnCancelarModal = document.getElementById('btn-cancelar');
    const btnClientes = document.getElementById('btn-clientes');

    function abrirModal() {
        const selectPagoEl = document.getElementById('select-met-pago');

        if (carrito.length === 0) {
            mostrarNotificacion('Carrito vacío', 'Agrega productos antes de continuar.');
            return;
        }

        if (!selectPagoEl || !selectPagoEl.value) {
            mostrarNotificacion('Método de pago requerido', 'Selecciona un método de pago antes de continuar.');
            return;
        }

        // Cargar datos dinámicos en el modal
        const modalFecha = document.getElementById('modal-fecha');
        const modalCliente = document.getElementById('modal-cliente');
        const modalTablaBody = document.getElementById('modal-tabla-body');

        if (modalFecha) modalFecha.textContent = new Date().toLocaleDateString('es-AR');
        if (modalCliente && selectCliente) {
            modalCliente.textContent = selectCliente.options[selectCliente.selectedIndex].text;
        }

        if (modalTablaBody) {
            modalTablaBody.innerHTML = '';
            let totalModal = 0;

            carrito.forEach(item => {
                const subtotal = item.precio_unitario * item.cantidad;
                totalModal += subtotal;

                const fila = `
                    <tr>
                        <td>${item.nombre}</td>
                        <td>${item.cantidad} unidad(es)</td>
                        <td>$${subtotal.toFixed(2)}</td>
                    </tr>
                `;
                modalTablaBody.insertAdjacentHTML('beforeend', fila);
            });

            const filaTotal = `
                <tr>
                    <td colspan="2" class="total-table"><strong>Total</strong></td>
                    <td class="total-table"><strong>$${totalModal.toFixed(2)}</strong></td>
                </tr>
            `;
            modalTablaBody.insertAdjacentHTML('beforeend', filaTotal);
        }

        if (modal) modal.style.display = 'flex';
    }

    function cerrarModal() {
        if (modal) modal.style.display = 'none';
        window.location.href = '/ventas/realizar';
    }

    if (btnOpenModal) btnOpenModal.addEventListener('click', abrirModal);
    if (btnCerrarModal) btnCerrarModal.addEventListener('click', cerrarModal);
    if (btnCancelarModal) btnCancelarModal.addEventListener('click', cerrarModal);
    if (btnClientes) {
        btnClientes.addEventListener('click', () => {
            try {
                localStorage.setItem(claveCarrito, JSON.stringify(
                    carrito.map(({ idproducto_servicio, cantidad }) => ({
                        idproducto_servicio,
                        cantidad
                    }))
                ));
                window.location.href = '/clientes';
            } catch (error) {
                console.error('No se pudo guardar el pedido antes de abrir clientes:', error);
                mostrarNotificacion('Error', 'No se pudo guardar el pedido. No se abrió la página de clientes.', 4000);
            }
        });
    }

    // ==========================================
    // 5. ENVÍO DE LA VENTA AL BACKEND
    // ==========================================
    const btnConfirmarVenta = document.getElementById('btn-confirmar-venta');

    if (btnConfirmarVenta) {
        btnConfirmarVenta.addEventListener('click', async () => {
            const selectPagoEl = document.getElementById('select-met-pago');

            const idCliente = selectCliente && selectCliente.value ? parseInt(selectCliente.value) : 1;
            const idMetodoPago = selectPagoEl && selectPagoEl.value ? parseInt(selectPagoEl.value) : null;

            if (!idMetodoPago) {
                mostrarNotificacion('Método de pago inválido', 'Debes seleccionar un método de pago válido.');
                return;
            }

            const payload = {
                id_cliente: idCliente,
                id_metodo_pago: idMetodoPago,
                descuento: 0.0,
                carrito: carrito
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
                    try {
                        localStorage.removeItem(claveCarrito);
                    } catch (error) {
                        console.error('No se pudo borrar el carrito guardado después de registrar la venta:', error);
                        mostrarNotificacion('Venta registrada', 'La venta se registró, pero no se pudo borrar el pedido guardado.', 4000);
                        setTimeout(() => {
                            window.location.href = resultado.redireccion || '/ventas';
                        }, 3500);
                        return;
                    }

                    mostrarNotificacion('Venta registrada', resultado.mensaje || 'La venta se registró con éxito.', 2500);
                    setTimeout(() => {
                        window.location.href = resultado.redireccion || '/ventas';
                    }, 2000);
                } else {
                    mostrarNotificacion('Error', resultado.mensaje || resultado.error || 'No se pudo procesar la venta.', 4000);
                    btnConfirmarVenta.disabled = false;
                    btnConfirmarVenta.textContent = 'Confirmar Venta';
                }
            } catch (error) {
                console.error('Error en la solicitud HTTP:', error);
                mostrarNotificacion('Error de conexión', 'Ocurrió un error al enviar la venta.', 4000);
                btnConfirmarVenta.disabled = false;
                btnConfirmarVenta.textContent = 'Confirmar Venta';
            }
        });
    }

    restaurarCarrito();
    actualizarResumen();

    function mostrarNotificacion(titulo, mensaje, tiempo = 3000) {
        if (!cartelEmergente || !cartelTitulo || !cartelMensaje) {
            console.warn(`[${titulo}] ${mensaje}`);
            return;
        }

        clearTimeout(timerNotificacion);

        cartelTitulo.textContent = titulo;
        cartelMensaje.textContent = mensaje;
        cartelEmergente.style.display = 'block';

        if (tiempo > 0) {
            timerNotificacion = setTimeout(() => {
                ocultarNotificacion();
            }, tiempo);
        }
    }

    function ocultarNotificacion() {
        if (!cartelEmergente) return;
        cartelEmergente.style.display = 'none';
    }

});