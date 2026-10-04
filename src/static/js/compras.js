document.addEventListener('DOMContentLoaded', () => {
    // --- ELEMENTOS DE LA INTERFAZ ---
    const tablaBody = document.getElementById('tabla-compras-body');
    const inputBusqueda = document.getElementById('input-busqueda');
    const selectFiltroFecha = document.getElementById('select-filtro-fecha');
    const selectFiltroEstado = document.getElementById('select-filtro-estado');
    const metricaTotalCompras = document.getElementById('metrica-total-compras');
    const metricaTotalProductos = document.getElementById('metrica-total-productos');
    const contenedorPaginacion = document.getElementById('contenedor-paginacion');

    // --- ELEMENTOS DEL CARTEL EMERGENTE ---
    const cartelEmergente = document.getElementById('cartel-emergente');
    const cartelTitulo = document.getElementById('cartel-titulo');
    const cartelMensaje = document.getElementById('cartel-mensaje');
    let timerNotificacion;

    // --- ELEMENTOS DEL MODAL ---
    const modal = document.getElementById('modal-overlay');
    const btnCerrarModal = document.getElementById('btn-cerrar-modal');
    const btnCerrarModalAlt = document.getElementById('btn-cerrar-modal-alt');
    const modalNumCompra = document.getElementById('modal-num-compra');
    const modalFecha = document.getElementById('modal-fecha');
    const modalProveedor = document.getElementById('modal-proveedor');
    const modalTablaBody = document.getElementById('modal-tabla-body');
    const modalTotalMonto = document.getElementById('modal-total-monto');

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

    // 1. Cargar listado dinámico desde la API
    async function cargarCompras() {
        const busqueda = inputBusqueda?.value.trim() || '';
        const filtroFecha = selectFiltroFecha?.value || 'todos';
        const filtroEstado = selectFiltroEstado?.value || '1';
        const solicitud = ++solicitudActual;

        const parametros = new URLSearchParams({
            busqueda,
            filtro_fecha: filtroFecha,
            estado: filtroEstado,
            pagina: paginaActual
        });

        try {
            const response = await fetch(`/api/compras?${parametros}`);
            const data = await response.json();

            if (solicitud !== solicitudActual) return;
            if (!response.ok || !data.Exito) {
                throw new Error(data.mensaje || 'No se pudieron cargar las compras.');
            }

            const paginacion = data.paginacion || {};
            const totalPaginas = Math.max(1, Number(paginacion.total_paginas) || 1);
            const paginaRespuesta = Math.max(1, Number(paginacion.pagina_actual) || 1);

            if (paginaRespuesta > totalPaginas) {
                paginaActual = totalPaginas;
                cargarCompras();
                return;
            }
            paginaActual = paginaRespuesta;

            if (data.resumen) {
                if (metricaTotalCompras) metricaTotalCompras.textContent = data.resumen.total_compras || 0;
                if (metricaTotalProductos) metricaTotalProductos.textContent = data.resumen.total_productos || 0;
            }

            renderizarTabla(data.compras || []);
            renderizarPaginacion(paginaActual, totalPaginas);
        } catch (error) {
            if (solicitud !== solicitudActual) return;
            console.error("Error al cargar compras:", error);
            if (contenedorPaginacion) contenedorPaginacion.replaceChildren();
            if (tablaBody) {
                tablaBody.innerHTML = `<tr><td colspan="6" style="text-align:center;">Error al cargar los datos</td></tr>`;
            }
            mostrarNotificacion("Error", "No se pudieron obtener las compras del servidor.", 4000);
        }
    }

    // 2. Renderizar filas de la tabla principal
    function renderizarTabla(compras) {
        if (!tablaBody) return;
        tablaBody.innerHTML = '';

        if (compras.length === 0) {
            tablaBody.innerHTML = `<tr><td colspan="6" style="text-align:center;">No se encontraron órdenes de compra</td></tr>`;
            return;
        }

        compras.forEach(c => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>#${c.idcompra || c.id_orden}</td>
                <td>${c.fecha}</td>
                <td>${c.proveedor || 'Proveedor General'}</td>
                <td>${c.tipos_producto || 0} tipos</td>
                <td>${c.total_productos || 0} unidades</td>
                <td>
                    <div class="btn-acciones">
                        <button class="btn-accion resumen" data-id="${c.idcompra || c.id_orden}">Ver resumen</button>
                        <button class="btn-accion eliminar" data-id="${c.idcompra || c.id_orden}">Anular</button>
                    </div>
                </td>
            `;
            tablaBody.appendChild(tr);
        });
    }

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
                cargarCompras();
            });
            contenedorPaginacion.appendChild(boton);
        };

        const agregarNumeroPagina = (numero) => {
            const boton = document.createElement('button');
            boton.type = 'button';
            boton.className = `btn-paginacion ${numero === pagina ? 'activo' : ''}`;
            boton.textContent = numero;
            boton.setAttribute('aria-label', `Página ${numero}`);
            if (numero === pagina) boton.setAttribute('aria-current', 'page');
            boton.addEventListener('click', () => {
                paginaActual = numero;
                cargarCompras();
            });
            contenedorPaginacion.appendChild(boton);
        };

        crearBoton('« Anterior', pagina - 1, 'Página anterior', pagina === 1);

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

        crearBoton('Siguiente »', pagina + 1, 'Página siguiente', pagina === totalPaginas);
    }

    // 3. Delegación de eventos para los botones de las filas
    tablaBody?.addEventListener('click', (e) => {
        const btnResumen = e.target.closest('.resumen');
        const btnEliminar = e.target.closest('.eliminar');

        if (btnResumen) {
            const idCompra = btnResumen.dataset.id;
            verResumenCompra(idCompra);
        }

        if (btnEliminar) {
            const idCompra = btnEliminar.dataset.id;
            anularCompra(idCompra);
        }
    });

    // 4. Ver Resumen
    async function verResumenCompra(idCompra) {
        try {
            const response = await fetch(`/api/compras/${idCompra}/detalle`);
            const data = await response.json();

            if (!response.ok || !data.exito) {
                mostrarNotificacion("Atención", data.mensaje || "Ocurrió un error al obtener el detalle de la compra.", 4000);
                return;
            }

            const compra = data.compra;
            const items = data.items || [];

            // Llenar datos de la cabecera del modal
            if (modalNumCompra) modalNumCompra.textContent = compra.idcompra || compra.id_orden;
            if (modalFecha) modalFecha.textContent = compra.fecha || '-';
            if (modalProveedor) modalProveedor.textContent = compra.nombre_proveedor?.trim() || compra.proveedor || 'Proveedor General';
            if (modalTotalMonto) modalTotalMonto.textContent = `$${Number(compra.precio_total || 0).toLocaleString()}`;

            // Llenar la tabla de productos del modal
            if (modalTablaBody) {
                modalTablaBody.innerHTML = '';

                if (items.length === 0) {
                    modalTablaBody.innerHTML = `<tr><td colspan="5" style="text-align:center;">No hay ítems registrados en esta compra</td></tr>`;
                } else {
                    items.forEach(item => {
                        const tr = document.createElement('tr');
                        const precioUnitario = item.precio_unitario 
                            ? `$${Number(item.precio_unitario).toLocaleString()}` 
                            : '-';
                        const subtotal = item.subtotal 
                            ? `$${Number(item.subtotal).toLocaleString()}` 
                            : `$${Number((item.cantidad || 0) * (item.precio_unitario || 0)).toLocaleString()}`;

                        tr.innerHTML = `
                            <td>${item.producto_nombre || item.producto}</td>
                            <td>${item.tipo || '-'}</td>
                            <td>${item.cantidad}</td>
                            <td>${precioUnitario}</td>
                            <td>${subtotal}</td>
                        `;
                        modalTablaBody.appendChild(tr);
                    });
                }
            }

            abrirModal();

        } catch (error) {
            console.error("Error al cargar detalle de compra:", error);
            mostrarNotificacion("Error", "No se pudo cargar la información de la compra.", 4000);
        }
    }

    // 5. Anular / Eliminar Orden de Compra
    async function anularCompra(idCompra) {
        const confirmado = await pedirConfirmacion(
            "Anular Orden de Compra",
            `¿Está seguro de que desea anular la orden de compra #${idCompra}?`
        );

        if (!confirmado) return;

        try {
            const response = await fetch(`/api/compras/anular/${idCompra}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();

            if (response.ok && data.exito) {
                mostrarNotificacion("Éxito", "La orden de compra fue anulada correctamente.", 3000);
                cargarCompras();
            } else {
                mostrarNotificacion("Error", data.mensaje || "No se pudo anular la orden de compra.", 4000);
            }
        } catch (error) {
            console.error("Error al anular compra:", error);
            mostrarNotificacion("Error", "Ocurrió un fallo al intentar anular la orden de compra.", 4000);
        }
    }

    // 6. Control del Modal
    function abrirModal() { modal?.classList.add('activo'); }
    function cerrarModal() { modal?.classList.remove('activo'); }

    btnCerrarModal?.addEventListener('click', cerrarModal);
    btnCerrarModalAlt?.addEventListener('click', cerrarModal);
    window.addEventListener('click', (e) => { if (e.target === modal) cerrarModal(); });

    // 7. Eventos de los filtros
    inputBusqueda?.addEventListener('input', () => {
        paginaActual = 1;
        solicitudActual++;
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(cargarCompras, 300);
    });

    selectFiltroFecha?.addEventListener('change', () => {
        paginaActual = 1;
        cargarCompras();
    });
    selectFiltroEstado?.addEventListener('change', () => {
        paginaActual = 1;
        cargarCompras();
    });

    // Carga inicial
    cargarCompras();
});