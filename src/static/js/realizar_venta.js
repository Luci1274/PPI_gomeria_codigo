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
    const btnCarrito = document.getElementById('btn-carrito-pos');
    const overlayResumen = document.getElementById('overlay-resumen-pos');
    const panelResumen = document.getElementById('panel-resumen-pos');

    function cerrarResumenMovil(devolverFoco = false) {
        document.body.classList.remove('resumen-pos-abierto');
        btnCarrito?.setAttribute('aria-expanded', 'false');
        if (devolverFoco) btnCarrito?.focus();
    }

    btnCarrito?.addEventListener('click', () => {
        const abierto = document.body.classList.toggle('resumen-pos-abierto');
        btnCarrito.setAttribute('aria-expanded', String(abierto));
        if (abierto) panelResumen?.focus();
    });
    overlayResumen?.addEventListener('click', () => cerrarResumenMovil(true));
    document.getElementById('btn-open-modal')?.addEventListener('click', () => cerrarResumenMovil());
    window.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && document.body.classList.contains('resumen-pos-abierto')) {
            cerrarResumenMovil(true);
        }
    });

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

        if (carritoGuardado.some(item =>
            !['producto', 'servicio'].includes(item?.tipo_item)
        )) {
            try {
                localStorage.removeItem(claveCarrito);
            } catch (error) {
                console.error('No se pudo borrar el pedido obsoleto guardado:', error);
            }
            mostrarNotificacion(
                'Pedido anterior no restaurado',
                'El pedido guardado no identifica productos y servicios por separado; comienza uno nuevo.'
            );
            return;
        }

        const tarjetasPorId = new Map(
            Array.from(document.querySelectorAll('.tarjeta-producto'))
                .map(tarjeta => [`${tarjeta.dataset.tipoItem}:${Number(tarjeta.dataset.id)}`, tarjeta])
        );

        carrito = carritoGuardado.reduce((items, guardado) => {
            const id = Number(guardado?.idproducto_servicio);
            const tipoItem = guardado.tipo_item;
            const cantidad = Number(guardado?.cantidad);
            const tarjeta = tarjetasPorId.get(`${tipoItem}:${id}`);
            const precio = Number(tarjeta?.dataset.precio);

            if (!tarjeta || !Number.isSafeInteger(cantidad) || cantidad <= 0 || !Number.isFinite(precio)) {
                return items;
            }

            items.push({
                idproducto_servicio: id,
                tipo_item: tipoItem,
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
            const tipoItem = tarjeta.dataset.tipoItem;
            const nombre = tarjeta.dataset.nombre;
            const precio = parseFloat(tarjeta.dataset.precio);

            const productoExistente = carrito.find(item =>
                item.idproducto_servicio === id && item.tipo_item === tipoItem
            );

            if (productoExistente) {
                productoExistente.cantidad += 1;
            } else {
                carrito.push({
                    idproducto_servicio: id,
                    tipo_item: tipoItem,
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

            const itemPedido = document.createElement('div');
            itemPedido.className = 'item-pedido';
            const detalles = document.createElement('div');
            detalles.className = 'detalles-item';
            const nombre = document.createElement('strong');
            nombre.textContent = item.nombre;
            const cantidad = document.createElement('span');
            cantidad.className = 'cant-item';
            cantidad.textContent = `Cant: ${item.cantidad}`;
            const precio = document.createElement('span');
            precio.className = 'precio-item';
            precio.textContent = `$${subtotal.toFixed(2)}`;
            const btnEliminar = document.createElement('button');
            btnEliminar.type = 'button';
            btnEliminar.className = 'btn-eliminar';
            btnEliminar.dataset.index = index;
            btnEliminar.textContent = '✕';
            detalles.append(nombre, cantidad, precio, btnEliminar);
            itemPedido.appendChild(detalles);
            contenedorLista.appendChild(itemPedido);
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
    const btnInventario = document.getElementById('btn-inventario');

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

                const fila = document.createElement('tr');
                const celdaNombre = document.createElement('td');
                celdaNombre.textContent = item.nombre;
                const celdaCantidad = document.createElement('td');
                celdaCantidad.textContent = `${item.cantidad} unidad(es)`;
                const celdaSubtotal = document.createElement('td');
                celdaSubtotal.textContent = `$${subtotal.toFixed(2)}`;
                fila.append(celdaNombre, celdaCantidad, celdaSubtotal);
                modalTablaBody.appendChild(fila);
            });

            const filaTotal = document.createElement('tr');
            const celdaEtiquetaTotal = document.createElement('td');
            celdaEtiquetaTotal.colSpan = 2;
            celdaEtiquetaTotal.className = 'total-table';
            const etiquetaTotal = document.createElement('strong');
            etiquetaTotal.textContent = 'Total';
            celdaEtiquetaTotal.appendChild(etiquetaTotal);
            const celdaMontoTotal = document.createElement('td');
            celdaMontoTotal.className = 'total-table';
            const montoTotal = document.createElement('strong');
            montoTotal.textContent = `$${totalModal.toFixed(2)}`;
            celdaMontoTotal.appendChild(montoTotal);
            filaTotal.append(celdaEtiquetaTotal, celdaMontoTotal);
            modalTablaBody.appendChild(filaTotal);
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
    function guardarCarritoYRedirigir(destino, descripcion) {
        try {
            localStorage.setItem(claveCarrito, JSON.stringify(
                carrito.map(({ idproducto_servicio, tipo_item, cantidad }) => ({
                    idproducto_servicio,
                    tipo_item,
                    cantidad
                }))
            ));
            window.location.href = destino;
        } catch (error) {
            console.error(`No se pudo guardar el pedido antes de abrir ${descripcion}:`, error);
            mostrarNotificacion('Error', `No se pudo guardar el pedido. No se abrió ${descripcion}.`, 4000);
        }
    }

    btnClientes?.addEventListener('click', () => guardarCarritoYRedirigir('/clientes', 'clientes'));
    btnInventario?.addEventListener('click', () =>
        guardarCarritoYRedirigir('/inventario?volver=venta', 'productos')
    );

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