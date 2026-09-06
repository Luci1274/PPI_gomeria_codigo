document.addEventListener('DOMContentLoaded', () => {
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

    function abrirModal() {
        const selectPagoEl = document.getElementById('select-met-pago');

        if (carrito.length === 0) {
            alert('El carrito está vacío. Agrega productos antes de continuar.');
            return;
        }

        if (!selectPagoEl || !selectPagoEl.value) {
            alert('Por favor, selecciona un método de pago antes de continuar.');
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
    }

    if (btnOpenModal) btnOpenModal.addEventListener('click', abrirModal);
    if (btnCerrarModal) btnCerrarModal.addEventListener('click', cerrarModal);
    if (btnCancelarModal) btnCancelarModal.addEventListener('click', cerrarModal);

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
                alert('Debes seleccionar un método de pago válido.');
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
                    alert(resultado.mensaje || 'Venta registrada con éxito');
                    window.location.href = resultado.redireccion || '/ventas';
                } else {
                    alert(`Error: ${resultado.mensaje || resultado.error || 'No se pudo procesar la venta'}`);
                    btnConfirmarVenta.disabled = false;
                    btnConfirmarVenta.textContent = 'Confirmar Venta';
                }
            } catch (error) {
                console.error('Error en la solicitud HTTP:', error);
                alert('Ocurrió un error de conexión al enviar la venta.');
                btnConfirmarVenta.disabled = false;
                btnConfirmarVenta.textContent = 'Confirmar Venta';
            }
        });
    }
});