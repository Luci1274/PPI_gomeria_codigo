document.addEventListener('DOMContentLoaded', () => {
    // Elementos de la interfaz
    const tablaBody = document.getElementById('tabla-compras-body');
    const inputBusqueda = document.getElementById('input-busqueda');
    const selectFiltroFecha = document.getElementById('select-filtro-fecha');
    const selectFiltroEstado = document.getElementById('select-filtro-estado');
    const metricaTotalCompras = document.getElementById('metrica-total-compras');
    const metricaTotalProductos = document.getElementById('metrica-total-productos');

    // Elementos del Modal
    const modal = document.getElementById('modal-overlay');
    const btnCerrarModal = document.getElementById('btn-cerrar-modal');
    const btnCerrarModalAlt = document.getElementById('btn-cerrar-modal-alt');
    const modalNumCompra = document.getElementById('modal-num-compra');
    const modalFecha = document.getElementById('modal-fecha');
    const modalProveedor = document.getElementById('modal-proveedor');
    const modalTablaBody = document.getElementById('modal-tabla-body');
    const modalTotalMonto = document.getElementById('modal-total-monto');

    let debounceTimer;

    // 1. Cargar listado dinámico desde la API
    async function cargarCompras() {
        const busqueda = inputBusqueda?.value.trim() || '';
        const filtroFecha = selectFiltroFecha?.value || 'todos';
        const filtroEstado = selectFiltroEstado?.value || '1';

        const url = `/api/compras?busqueda=${encodeURIComponent(busqueda)}&filtro_fecha=${filtroFecha}&estado=${filtroEstado}`;

        try {
            const response = await fetch(url);
            const data = await response.json();

            if (data.resumen) {
                if (metricaTotalCompras) metricaTotalCompras.textContent = data.resumen.total_compras || 0;
                if (metricaTotalProductos) metricaTotalProductos.textContent = data.resumen.total_productos || 0;
            }

            renderizarTabla(data.compras || []);
        } catch (error) {
            console.error("Error al cargar compras:", error);
            if (tablaBody) {
                tablaBody.innerHTML = `<tr><td colspan="6" style="text-align:center;">Error al cargar los datos</td></tr>`;
            }
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

    // 4. Ver Resumen (Obtiene datos de /api/compras/<id>/detalle o /compra/<id>/detalle)
    async function verResumenCompra(idCompra) {
        try {
            const response = await fetch(`/api/compras/${idCompra}/detalle`);
            const data = await response.json();

            if (!response.ok || !data.exito) {
                alert(data.mensaje || "Ocurrió un error al obtener el detalle de la compra.");
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
            alert("No se pudo cargar la información de la compra.");
        }
    }

    // 5. Anular / Eliminar Orden de Compra
    async function anularCompra(idCompra) {
        if (!confirm(`¿Está seguro de que desea anular la orden de compra #${idCompra}?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/compras/anular/${idCompra}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();

            if (response.ok && data.exito) {
                cargarCompras();
            } else {
                alert(data.mensaje || "No se pudo anular la orden de compra.");
            }
        } catch (error) {
            console.error("Error al anular compra:", error);
            alert("Error al intentar anular la orden de compra.");
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
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(cargarCompras, 300);
    });

    selectFiltroFecha?.addEventListener('change', cargarCompras);
    selectFiltroEstado?.addEventListener('change', cargarCompras);

    // Carga inicial
    cargarCompras();
});