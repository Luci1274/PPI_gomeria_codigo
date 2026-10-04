document.addEventListener('DOMContentLoaded', () => {
    // Elementos de la interfaz
    const tablaBody = document.getElementById('tabla-ventas-body');
    const inputBusqueda = document.getElementById('input-busqueda');
    const selectFiltroFecha = document.getElementById('select-filtro-fecha');
    const metricaTotalVentas = document.getElementById('metrica-total-ventas');
    const metricaTotalProductos = document.getElementById('metrica-total-productos');
    const contenedorPaginacion = document.getElementById('contenedor-paginacion');

    // Elementos del Modal
    const modal = document.getElementById('modal-overlay');
    const btnCerrarModal = document.getElementById('btn-cerrar-modal');
    const btnCerrarModalAlt = document.getElementById('btn-cerrar-modal-alt');
    const modalNumVenta = document.getElementById('modal-num-venta');
    const modalFecha = document.getElementById('modal-fecha');
    const modalCliente = document.getElementById('modal-cliente');
    const modalTablaBody = document.getElementById('modal-tabla-body');
    const modalTotalMonto = document.getElementById('modal-total-monto');

    // --- ELEMENTOS DEL CARTEL EMERGENTE ---
    const cartelEmergente = document.getElementById('cartel-emergente');
    const cartelTitulo = document.getElementById('cartel-titulo');
    const cartelMensaje = document.getElementById('cartel-mensaje');
    let timerNotificacion;

    let debounceTimer;
    let paginaActual = 1;
    let solicitudActual = 0;

    // --- NOTIFICACIONES Y CONFIRMACIONES ---

    function limpiarBotonesCartel() {
        if (!cartelEmergente) return;
        const contenedorBotones = cartelEmergente.querySelector('.cartel-acciones');
        if (contenedorBotones) contenedorBotones.remove();
    }

    function mostrarNotificacion(titulo, mensaje, tiempo = 3000) {
        if (!cartelEmergente || !cartelTitulo || !cartelMensaje) {
            console.warn(`[${titulo}] ${mensaje}`);
            return;
        }

        clearTimeout(timerNotificacion);
        limpiarBotonesCartel();

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
        limpiarBotonesCartel();
    }

    function pedirConfirmacion(titulo, mensaje) {
        return new Promise((resolve) => {
            if (!cartelEmergente || !cartelTitulo || !cartelMensaje) {
                const res = confirm(`${titulo}\n\n${mensaje}`);
                return resolve(res);
            }

            clearTimeout(timerNotificacion);
            limpiarBotonesCartel();

            cartelTitulo.textContent = titulo;
            cartelMensaje.textContent = mensaje;

            const contenedorBotones = document.createElement('div');
            contenedorBotones.className = 'cartel-acciones';
            contenedorBotones.style.marginTop = '15px';
            contenedorBotones.style.display = 'flex';
            contenedorBotones.style.justifyContent = 'center';
            contenedorBotones.style.gap = '10px';

            contenedorBotones.innerHTML = `
                <button id="btn-confirmar-cartel" class="btn-accion">Confirmar</button>
                <button id="btn-cancelar-cartel" class="btn-accion borrar">Cancelar</button>
            `;

            cartelEmergente.appendChild(contenedorBotones);
            cartelEmergente.style.display = 'block';

            document.getElementById('btn-confirmar-cartel').onclick = () => {
                ocultarNotificacion();
                resolve(true);
            };

            document.getElementById('btn-cancelar-cartel').onclick = () => {
                ocultarNotificacion();
                resolve(false);
            };
        });
    }

    // 1. Cargar listado dinámico desde la API (con paginación)
    async function cargarVentas() {
        const busqueda = inputBusqueda?.value.trim() || '';
        const filtroFecha = selectFiltroFecha?.value || 'todos';
        const solicitud = ++solicitudActual;

        const url = `/api/ventas?busqueda=${encodeURIComponent(busqueda)}&filtro_fecha=${filtroFecha}&pagina=${paginaActual}`;

        try {
            const response = await fetch(url);
            const data = await response.json();

            if (solicitud !== solicitudActual) return;
            if (!response.ok || !data.Exito) {
                throw new Error(data.mensaje || 'No se pudieron cargar las ventas.');
            }

            const paginacion = data.paginacion || {};
            const totalPaginas = Number(paginacion.total_paginas) || 1;
            const paginaRespuesta = Number(paginacion.pagina_actual) || 1;

            if (paginaRespuesta > totalPaginas) {
                paginaActual = totalPaginas;
                cargarVentas();
                return;
            }
            paginaActual = paginaRespuesta;

            if (data.resumen) {
                if (metricaTotalVentas) metricaTotalVentas.textContent = data.resumen.total_ventas || 0;
                if (metricaTotalProductos) metricaTotalProductos.textContent = data.resumen.total_productos || 0;
            }

            renderizarTabla(data.ventas || []);
            renderizarPaginacion(paginaActual, totalPaginas);
        } catch (error) {
            if (solicitud !== solicitudActual) return;
            console.error("Error al cargar ventas:", error);
            if (contenedorPaginacion) contenedorPaginacion.replaceChildren();
            if (tablaBody) {
                tablaBody.innerHTML = `<tr><td colspan="6" style="text-align:center;">Error al cargar los datos</td></tr>`;
            }
            mostrarNotificacion("Error", "No se pudieron obtener las ventas del servidor.", 4000);
        }
    }

    // 2. Renderizar filas de la tabla principal
    function renderizarTabla(ventas) {
        if (!tablaBody) return;
        tablaBody.innerHTML = '';

        if (ventas.length === 0) {
            tablaBody.innerHTML = `<tr><td colspan="6" style="text-align:center;">No se encontraron registros</td></tr>`;
            return;
        }

        ventas.forEach(v => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>#${v.idventa}</td>
                <td>${v.fecha}</td>
                <td>${v.cliente}</td>
                <td>${v.cantidad_total_productos} productos</td>
                <td>$${Number(v.precio_total).toLocaleString()}</td>
                <td>
                    <div class="btn-acciones">
                        <button class="btn-accion resumen" data-id="${v.idventa}">Ver resumen</button>
                        <button class="btn-accion eliminar" data-id="${v.idventa}">Eliminar</button>
                    </div>
                </td>
            `;
            tablaBody.appendChild(tr);
        });
    }

    // 3. Renderizar controles de paginación dinámica
    function renderizarPaginacion(pagina, totalPaginas) {
        if (!contenedorPaginacion) return;
        contenedorPaginacion.replaceChildren();

        if (totalPaginas <= 1) return;

        const crearBoton = (texto, paginaDestino, etiqueta, deshabilitado = false) => {
            const boton = document.createElement('button');
            boton.type = 'button';
            boton.className = 'btn-paginacion';
            boton.textContent = texto;
            boton.setAttribute('aria-label', etiqueta);
            boton.disabled = deshabilitado;
            boton.addEventListener('click', () => {
                paginaActual = paginaDestino;
                cargarVentas();
            });
            contenedorPaginacion.appendChild(boton);
        };

        // Botón Anterior
        crearBoton('« Anterior', pagina - 1, 'Página anterior', pagina === 1);

        const agregarNumeroPagina = (numero) => {
            const boton = document.createElement('button');
            boton.type = 'button';
            boton.className = `btn-paginacion ${numero === pagina ? 'activo' : ''}`;
            boton.textContent = numero;
            boton.setAttribute('aria-label', `Página ${numero}`);
            if (numero === pagina) boton.setAttribute('aria-current', 'page');
            boton.addEventListener('click', () => {
                paginaActual = numero;
                cargarVentas();
            });
            contenedorPaginacion.appendChild(boton);
        };

        const inicio = Math.max(1, pagina - 2);
        const fin = Math.min(totalPaginas, pagina + 2);

        if (inicio > 1) {
            agregarNumeroPagina(1);
            if (inicio > 2) {
                const separador = document.createElement('span');
                separador.textContent = '…';
                separador.setAttribute('aria-hidden', 'true');
                contenedorPaginacion.appendChild(separador);
            }
        }

        for (let numero = inicio; numero <= fin; numero++) {
            agregarNumeroPagina(numero);
        }

        if (fin < totalPaginas) {
            if (fin < totalPaginas - 1) {
                const separador = document.createElement('span');
                separador.textContent = '…';
                separador.setAttribute('aria-hidden', 'true');
                contenedorPaginacion.appendChild(separador);
            }
            agregarNumeroPagina(totalPaginas);
        }

        // Botón Siguiente
        crearBoton('Siguiente »', pagina + 1, 'Página siguiente', pagina === totalPaginas);
    }

    // 4. Delegación de eventos para los botones de las filas
    tablaBody?.addEventListener('click', (e) => {
        const btnResumen = e.target.closest('.resumen');
        const btnEliminar = e.target.closest('.eliminar');

        if (btnResumen) {
            const idVenta = btnResumen.dataset.id;
            verResumenVenta(idVenta);
        }

        if (btnEliminar) {
            const idVenta = btnEliminar.dataset.id;
            anularVenta(idVenta);
        }
    });

    // 5. Ver Resumen (Obtiene datos de /venta/<id>/detalle)
    async function verResumenVenta(idVenta) {
        try {
            const response = await fetch(`/venta/${idVenta}/detalle`);
            const data = await response.json();

            if (!response.ok || !data.exito) {
                mostrarNotificacion("Error", data.mensaje || "Ocurrió un error al obtener el detalle de la venta.", 4000);
                return;
            }

            const venta = data.venta;
            const items = data.items || [];

            // Llenar datos de la cabecera del modal
            if (modalNumVenta) modalNumVenta.textContent = venta.idventa;
            if (modalFecha) modalFecha.textContent = venta.fecha || '-';
            if (modalCliente) modalCliente.textContent = venta.nombre_cliente?.trim() || 'Cliente General';
            if (modalTotalMonto) modalTotalMonto.textContent = `$${Number(venta.precio_total || 0).toLocaleString()}`;

            // Llenar la tabla de productos
            if (modalTablaBody) {
                modalTablaBody.innerHTML = '';

                if (items.length === 0) {
                    modalTablaBody.innerHTML = `<tr><td colspan="3" style="text-align:center;">No hay ítems registrados</td></tr>`;
                } else {
                    items.forEach(item => {
                        const tr = document.createElement('tr');
                        const precioUnitario = item.precio_unitario
                            ? `$${Number(item.precio_unitario).toLocaleString()}`
                            : '-';

                        tr.innerHTML = `
                            <td><img src="${item.imagen_producto}" alt="${item.producto_nombre}" style="width: 60px; height: 60px;"> - ${item.producto_nombre}</td>
                            <td>${item.cantidad}</td>
                            <td>${precioUnitario}</td>
                        `;
                        modalTablaBody.appendChild(tr);
                    });
                }
            }

            abrirModal();

        } catch (error) {
            console.error("Error al cargar detalle de venta:", error);
            mostrarNotificacion("Error", "No se pudo cargar la información de la venta.", 4000);
        }
    }

    // 6. Anular / Eliminar Venta
    async function anularVenta(idVenta) {
        const confirmada = await pedirConfirmacion(
            "Confirmar anulación",
            `¿Está seguro de que desea anular la venta #${idVenta}?`
        );
        if (!confirmada) {
            return;
        }

        try {
            const response = await fetch(`/api/ventas/anular/${idVenta}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();

            if (response.ok && data.exito) {
                mostrarNotificacion("Venta anulada", `La venta #${idVenta} se anuló correctamente.`);
                await cargarVentas();
            } else {
                mostrarNotificacion("Error", data.mensaje || "No se pudo anular la venta.", 4000);
            }
        } catch (error) {
            console.error("Error al anular venta:", error);
            mostrarNotificacion("Error", "Error al intentar anular la venta.", 4000);
        }
    }

    // 7. Control del Modal
    function abrirModal() { modal?.classList.add('activo'); }
    function cerrarModal() { modal?.classList.remove('activo'); }

    btnCerrarModal?.addEventListener('click', cerrarModal);
    btnCerrarModalAlt?.addEventListener('click', cerrarModal);
    window.addEventListener('click', (e) => { if (e.target === modal) cerrarModal(); });

    // 8. Eventos de los filtros (Resetean a la página 1)
    inputBusqueda?.addEventListener('input', () => {
        paginaActual = 1;
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(cargarVentas, 300);
    });

    selectFiltroFecha?.addEventListener('change', () => {
        paginaActual = 1;
        cargarVentas();
    });

    // Carga inicial
    cargarVentas();
});