document.addEventListener('DOMContentLoaded', () => {
    // Elementos de la interfaz
    const tablaBody = document.getElementById('tabla-ventas-body');
    const inputBusqueda = document.getElementById('input-busqueda');
    const selectFiltroFecha = document.getElementById('select-filtro-fecha');
    const metricaTotalVentas = document.getElementById('metrica-total-ventas');
    const metricaTotalProductos = document.getElementById('metrica-total-productos');

    // Elementos del Modal
    const modal = document.getElementById('modal-overlay');
    const btnCerrarModal = document.getElementById('btn-cerrar-modal');
    const btnCerrarModalAlt = document.getElementById('btn-cerrar-modal-alt');
    const modalNumVenta = document.getElementById('modal-num-venta');
    const modalFecha = document.getElementById('modal-fecha');
    const modalCliente = document.getElementById('modal-cliente');
    const modalTablaBody = document.getElementById('modal-tabla-body');
    const modalTotalMonto = document.getElementById('modal-total-monto');

    let debounceTimer;

    // 1. Cargar listado dinámico desde la API
    async function cargarVentas() {
        const busqueda = inputBusqueda.value.trim();
        const filtroFecha = selectFiltroFecha.value;

        const url = `/api/ventas?busqueda=${encodeURIComponent(busqueda)}&filtro_fecha=${filtroFecha}`;

        try {
            const response = await fetch(url);
            const data = await response.json();

            if (data.resumen) {
                metricaTotalVentas.textContent = data.resumen.total_ventas || 0;
                metricaTotalProductos.textContent = data.resumen.total_productos || 0;
            }

            renderizarTabla(data.ventas || []);
        } catch (error) {
            console.error("Error al cargar ventas:", error);
            tablaBody.innerHTML = `<tr><td colspan="6" style="text-align:center;">Error al cargar los datos</td></tr>`;
        }
    }

    // 2. Renderizar filas de la tabla
    function renderizarTabla(ventas) {
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

    // 3. Delegación de eventos para los botones de las filas
    tablaBody.addEventListener('click', (e) => {
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

    // 4. Ver Resumen (Obtiene datos de /venta/<id>/detalle)
    async function verResumenVenta(idVenta) {
        try {
            const response = await fetch(`/venta/${idVenta}/detalle`);
            const respuesta = await response.json();

            if (!response.ok || !respuesta.exito) {
                alert(respuesta.mensaje || "Error al obtener el detalle de la venta");
                return;
            }

            const detalle = respuesta.data;
            
            // Poblar Modal
            modalNumVenta.textContent = detalle.idventa;
            modalFecha.textContent = detalle.fecha;
            modalCliente.textContent = detalle.cliente;
            modalTotalMonto.textContent = `$${Number(detalle.precio_total).toLocaleString()}`;

            modalTablaBody.innerHTML = '';
            detalle.productos.forEach(prod => {
                modalTablaBody.innerHTML += `
                    <tr>
                        <td>${prod.nombre}</td>
                        <td>${prod.cantidad} unidades</td>
                        <td>$${Number(prod.precio_unitario).toLocaleString()}</td>
                    </tr>
                `;
            });

            abrirModal();
        } catch (error) {
            console.error("Error al obtener detalle:", error);
            alert("Ocurrió un error al conectar con el servidor.");
        }
    }

    // 5. Anular / Eliminar Venta
    async function anularVenta(idVenta) {
        if (!confirm(`¿Está seguro de que desea anular la venta #${idVenta}?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/ventas/anular/${idVenta}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();

            if (response.ok && data.exito) {
                cargarVentas(); // Recarga la tabla con los datos actualizados
            } else {
                alert(data.mensaje || "No se pudo anular la venta.");
            }
        } catch (error) {
            console.error("Error al anular venta:", error);
            alert("Error al intentar anular la venta.");
        }
    }

    // 6. Control del Modal
    function abrirModal() { modal.classList.add('activo'); }
    function cerrarModal() { modal.classList.remove('activo'); }

    btnCerrarModal?.addEventListener('click', cerrarModal);
    btnCerrarModalAlt?.addEventListener('click', cerrarModal);
    window.addEventListener('click', (e) => { if (e.target === modal) cerrarModal(); });

    // 7. Eventos de los filtros
    inputBusqueda.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(cargarVentas, 300);
    });

    selectFiltroFecha.addEventListener('change', cargarVentas);

    // Carga inicial
    cargarVentas();
});