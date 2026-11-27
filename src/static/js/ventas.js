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
    const modalSubtotal = document.getElementById('modal-subtotal');
    const modalDescuento = document.getElementById('modal-descuento');
    const modalTotalMonto = document.getElementById('modal-total-monto');

    // Botones de acciones del Modal
    const btnDescargarPdf = document.getElementById('btn-descargar-pdf');
    const btnImprimir = document.getElementById('btn-imprimir');
    const contenedorTicketPdf = document.getElementById('contenedor-ticket-pdf');

    // Variables de estado de la venta activa
    let ventaActual = null;
    let itemsActuales = [];

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

            // Almacenar referencias de la venta activa
            ventaActual = data.venta;
            itemsActuales = data.items || [];

            // Llenar datos de la cabecera del modal
            if (modalNumVenta) modalNumVenta.textContent = ventaActual.idventa;
            if (modalFecha) modalFecha.textContent = ventaActual.fecha || '-';
            if (modalCliente) modalCliente.textContent = ventaActual.nombre_cliente?.trim() || 'Cliente General';
            const totalFinal = Number(ventaActual.precio_total || 0);
            const descuento = Number(ventaActual.descuento || 0);
            const subtotal = totalFinal + descuento;
            if (modalSubtotal) modalSubtotal.textContent = `$${subtotal.toFixed(2)}`;
            if (modalDescuento) modalDescuento.textContent = `$${descuento.toFixed(2)}`;
            if (modalTotalMonto) modalTotalMonto.textContent = `$${totalFinal.toFixed(2)}`;

            // Llenar la tabla de productos
            if (modalTablaBody) {
                modalTablaBody.innerHTML = '';

                if (itemsActuales.length === 0) {
                    modalTablaBody.innerHTML = `<tr><td colspan="3" style="text-align:center;">No hay ítems registrados</td></tr>`;
                } else {
                    itemsActuales.forEach(item => {
                        const tr = document.createElement('tr');
                        const precioUnitario = item.precio_unitario
                            ? `$${Number(item.precio_unitario).toLocaleString()}`
                            : '-';

                        tr.innerHTML = `
                            <td>
                                <div class="producto-resumen">
                                    <img class="producto-resumen-imagen" src="${item.imagen_producto}" alt="${item.producto_nombre}">
                                    <span class="producto-resumen-nombre">${item.producto_nombre}</span>
                                </div>
                            </td>
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

    // --- GENERADOR DE HTML TICKET ---
    function generarHTMLTicket(venta, items) {
        const totalFinal = Number(venta.precio_total || 0);
        const descuento = Number(venta.descuento || 0);
        const subtotal = totalFinal + descuento;
        const fecha = venta.fecha || '-';
        const cliente = venta.nombre_cliente?.trim() || 'Cliente General';

        const filasItems = items.map(item => {
            const pUnit = Number(item.precio_unitario || 0);
            const cant = Number(item.cantidad || 0);
            const sub = cant * pUnit;
            return `
                <tr>
                    <td colspan="3" style="padding-top: 4px; font-weight: bold;">${item.producto_nombre}</td>
                </tr>
                <tr>
                    <td style="padding-bottom: 4px;">${cant} x $${pUnit.toLocaleString()}</td>
                    <td></td>
                    <td style="text-align: right; padding-bottom: 4px;">$${sub.toLocaleString()}</td>
                </tr>
            `;
        }).join('');

        return `
            <div style="text-align: center;">
                <h2 style="margin: 0; font-size: 16px;">SISTEMA GOMERÍA</h2>
                <p style="margin: 3px 0; font-size: 11px;">Comprobante de Venta</p>
                <p style="margin: 3px 0; font-weight: bold;">Ticket #${venta.idventa}</p>
            </div>
            <div style="border-top: 1px dashed #000; margin: 6px 0;"></div>
            <div style="font-size: 11px;">
                <p style="margin: 2px 0;"><strong>Fecha:</strong> ${fecha}</p>
                <p style="margin: 2px 0;"><strong>Cliente:</strong> ${cliente}</p>
            </div>
            <div style="border-top: 1px dashed #000; margin: 6px 0;"></div>
            <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
                <thead>
                    <tr style="border-bottom: 1px solid #000;">
                        <th style="text-align: left;">Cant x P.Unit</th>
                        <th></th>
                        <th style="text-align: right;">Total</th>
                    </tr>
                </thead>
                <tbody>
                    ${filasItems}
                </tbody>
            </table>
            <div style="border-top: 1px dashed #000; margin: 6px 0;"></div>
            <div style="font-size: 11px; text-align: right;">
                <p style="margin: 2px 0;">Subtotal: $${subtotal.toFixed(2)}</p>
                <p style="margin: 2px 0;">Descuento: $${descuento.toFixed(2)}</p>
                <p style="margin: 4px 0; font-size: 13px; font-weight: bold;">Total: $${totalFinal.toFixed(2)}</p>
            </div>
            <div style="border-top: 1px dashed #000; margin: 6px 0;"></div>
            <div style="text-align: center; font-size: 10px; margin-top: 8px;">
                <p style="margin: 0;">¡Gracias por su compra!</p>
            </div>
        `;
    }

    // --- ACCIÓN: IMPRIMIR TICKET ---
    btnImprimir?.addEventListener('click', () => {
        if (!ventaActual) return;

        // Crear un iframe temporal para lanzar el diálogo de impresión
        const iframe = document.createElement('iframe');
        iframe.style.position = 'fixed';
        iframe.style.right = '0';
        iframe.style.bottom = '0';
        iframe.style.width = '0';
        iframe.style.height = '0';
        iframe.style.border = '0';
        document.body.appendChild(iframe);

        const doc = iframe.contentWindow.document;
        doc.open();
        doc.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Ticket #${ventaActual.idventa}</title>
                <style>
                    @page { margin: 0; size: auto; }
                    body {
                        font-family: 'Courier New', Courier, monospace;
                        width: 280px;
                        margin: 10px auto;
                        color: #000;
                        background: #fff;
                    }
                </style>
            </head>
            <body>
                ${generarHTMLTicket(ventaActual, itemsActuales)}
            </body>
            </html>
        `);
        doc.close();

        iframe.contentWindow.focus();
        setTimeout(() => {
            iframe.contentWindow.print();
            document.body.removeChild(iframe);
        }, 300);
    });

    // --- ACCIÓN: DESCARGAR PDF TICKET ---
    btnDescargarPdf?.addEventListener('click', async () => {
        if (!ventaActual || !contenedorTicketPdf) return;

        try {
            // Llenar el contenedor invisible con la plantilla del ticket
            contenedorTicketPdf.innerHTML = generarHTMLTicket(ventaActual, itemsActuales);

            const { jsPDF } = window.jspdf;

            // Renderizar la sección a imagen
            const canvas = await html2canvas(contenedorTicketPdf, { scale: 2 });
            const imgData = canvas.toDataURL('image/png');

            // Formato de Ticket estándar: 80mm de ancho y alto dinámico
            const pdfAncho = 80;
            const pdfAlto = (canvas.height * pdfAncho) / canvas.width;

            const pdf = new jsPDF('p', 'mm', [pdfAncho, pdfAlto]);
            pdf.addImage(imgData, 'PNG', 0, 0, pdfAncho, pdfAlto);

            const clienteNombre = (ventaActual.nombre_cliente || 'cliente').replace(/[^a-zA-Z0-0]/g, '_');
            pdf.save(`ticket-venta-${ventaActual.idventa}-${clienteNombre}.pdf`);

            contenedorTicketPdf.innerHTML = '';
        } catch (error) {
            console.error("Error al generar PDF del ticket:", error);
            mostrarNotificacion("Error", "No se pudo generar el ticket en PDF.", 4000);
        }
    });

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