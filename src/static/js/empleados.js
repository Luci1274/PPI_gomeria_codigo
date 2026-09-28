document.addEventListener('DOMContentLoaded', () => {
    // --- ESTADO DE LA APLICACIÓN ---
    let paginaActual = 1;
    let totalPaginas = 1;
    let debounceTimer;
    let timerNotificacion;

    // --- ELEMENTOS DEL DOM ---
    const tablaBody = document.getElementById('tabla-empleados-body');
    const valorMetrica = document.getElementById('valor_metrica');
    const inputBusqueda = document.getElementById('input-busqueda');

    // Paginación
    const btnAnterior = document.getElementById('btn-pag-anterior');
    const btnSiguiente = document.getElementById('btn-pag-siguiente');
    const infoPaginacion = document.getElementById('info-paginacion');

    // Modal Nuevo
    const modalNuevoEmpleado = document.getElementById('modal-nuevo-empleado');
    const btnNuevoEmpleado = document.getElementById('btn-nuevo-empleado');
    const btnCerrarModalNuevo = document.getElementById('btn-cerrar-modal-nuevo');
    const btnCancelarModalNuevo = document.getElementById('btn-cancelar-modal-nuevo');
    const formNuevoEmpleado = document.getElementById('form-nuevo-empleado');

    // Modal Editar
    const modalEditarEmpleado = document.getElementById('modal-editar-empleado');
    const btnCerrarModalEditar = document.getElementById('btn-cerrar-modal-editar');
    const btnCancelarModalEditar = document.getElementById('btn-cancelar-modal-editar');
    const formEditarEmpleado = document.getElementById('form-editar-empleado');

    // Cartel Emergente
    const cartelEmergente = document.getElementById('cartel-emergente');
    const cartelTitulo = document.getElementById('cartel-titulo');
    const cartelMensaje = document.getElementById('cartel-mensaje');

    // --- NOTIFICACIONES Y CONFIRMACIONES ---

    function limpiarBotonesCartel() {
        const contenedorBotones = cartelEmergente.querySelector('.cartel-acciones');
        if (contenedorBotones) contenedorBotones.remove();
    }

    function mostrarNotificacion(titulo, mensaje, tiempo = 3000) {
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
        cartelEmergente.style.display = 'none';
        limpiarBotonesCartel();
    }

    function pedirConfirmacion(titulo, mensaje) {
        return new Promise((resolve) => {
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

    // --- CARGA DE DATOS Y RENDERIZADO ---

    async function cargarEmpleados() {
        try {
            const params = new URLSearchParams({
                pagina: paginaActual,
                buscar: inputBusqueda.value.trim()
            });

            const respuesta = await fetch(`/api/empleados?${params.toString()}`);
            const data = await respuesta.json();

            if (!respuesta.ok || !data.exito) {
                mostrarNotificacion('Error', data.mensaje || 'Error al obtener empleados.');
                return;
            }

            if (valorMetrica) valorMetrica.textContent = data.total_items || 0;
            renderizarTabla(data.empleados);

            totalPaginas = data.total_paginas || Math.ceil((data.total_items || 0) / (data.limite || 10)) || 1;
            actualizarPaginacionUI();

        } catch (error) {
            console.error('Error al cargar empleados:', error);
            tablaBody.innerHTML = `<tr><td colspan="5" class="texto-centro">Error de conexión al cargar datos.</td></tr>`;
        }
    }

    function actualizarPaginacionUI() {
        if (infoPaginacion) infoPaginacion.textContent = `Página ${paginaActual} de ${totalPaginas}`;
        if (btnAnterior) btnAnterior.disabled = (paginaActual <= 1);
        if (btnSiguiente) btnSiguiente.disabled = (paginaActual >= totalPaginas);
    }

    function renderizarTabla(empleados) {
        tablaBody.innerHTML = '';

        if (!empleados || empleados.length === 0) {
            tablaBody.innerHTML = `
                <tr>
                    <td colspan="5" class="texto-centro">No se encontraron empleados.</td>
                </tr>`;
            return;
        }

        empleados.forEach(emp => {
            const tr = document.createElement('tr');
            const idEmp = emp.idempleado || emp.id;

            tr.innerHTML = `
                <td><strong>${emp.nombre || '-'}</strong></td>
                <td><a href="mailto:${emp.email || '-'}" target="_blank">${emp.email || '-'}</a></td>
                <td><a href="https://wa.me/${emp.telefono || '-'}" target="_blank">${emp.telefono || '-'}</a></td>
                <td>${emp.rol || '-'}</td>
                <td>
                    <div class="btn-acciones">
                        <button class="btn-accion btn-editar" data-id="${idEmp}">Modificar</button>
                        <button class="btn-accion borrar btn-eliminar" data-id="${idEmp}">Eliminar</button>
                    </div>
                </td>
            `;

            tablaBody.appendChild(tr);
        });
    }

    // --- DELEGACIÓN DE EVENTOS EN LA TABLA ---

    tablaBody.addEventListener('click', async (e) => {
        const btnEliminar = e.target.closest('.btn-eliminar');
        const btnEditar = e.target.closest('.btn-editar');

        if (btnEliminar) {
            const id = btnEliminar.dataset.id;
            const confirmado = await pedirConfirmacion(
                'Desactivar Empleado',
                '¿Estás seguro de que deseas eliminar o desactivar este empleado?'
            );

            if (confirmado) {
                desactivarEmpleado(id);
            }
        }

        if (btnEditar) {
            const id = btnEditar.dataset.id;
            abrirModalEditar(id);
        }
    });

    async function desactivarEmpleado(id) {
        try {
            const respuesta = await fetch(`/api/empleados/${id}/desactivar`, { method: 'POST' });
            const data = await respuesta.json();

            if (respuesta.ok && data.exito) {
                mostrarNotificacion('Empleado desactivado', data.mensaje || 'Operación realizada con éxito.');
                cargarEmpleados();
            } else {
                mostrarNotificacion('Error', data.mensaje || 'Error al desactivar empleado.');
            }
        } catch (error) {
            console.error('Error al desactivar empleado:', error);
            mostrarNotificacion('Error de red', 'Ocurrió un error al intentar desactivar el empleado.');
        }
    }

    // --- MANEJO DE MODAL CREAR ---

    function abrirModalNuevo() {
        modalNuevoEmpleado.classList.add('activo');
        modalNuevoEmpleado.style.display = 'flex';
    }

    function cerrarModalNuevo() {
        modalNuevoEmpleado.classList.remove('activo');
        modalNuevoEmpleado.style.display = 'none';
        formNuevoEmpleado.reset();
    }

    if (btnNuevoEmpleado) btnNuevoEmpleado.addEventListener('click', abrirModalNuevo);
    if (btnCerrarModalNuevo) btnCerrarModalNuevo.addEventListener('click', cerrarModalNuevo);
    if (btnCancelarModalNuevo) btnCancelarModalNuevo.addEventListener('click', cerrarModalNuevo);

    formNuevoEmpleado.addEventListener('submit', async (e) => {
        e.preventDefault();

        const nuevoEmpleado = {
            nombre: document.getElementById('input-nombre').value.trim(),
            email: document.getElementById('input-email').value.trim(),
            telefono: document.getElementById('input-telefono').value.trim(),
            rol: document.getElementById('input-rol').value.trim()
        };

        try {
            const respuesta = await fetch('/api/empleados/crear', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(nuevoEmpleado)
            });

            const data = await respuesta.json();

            if (respuesta.ok && data.exito) {
                mostrarNotificacion('Éxito', 'Empleado registrado correctamente.');
                cerrarModalNuevo();
                cargarEmpleados();
            } else {
                mostrarNotificacion('Error', data.mensaje || 'No se pudo crear el empleado.');
            }
        } catch (error) {
            console.error('Error al crear empleado:', error);
            mostrarNotificacion('Error de red', 'Error de conexión al guardar empleado.');
        }
    });

    // --- MANEJO DE MODAL EDITAR ---

    async function abrirModalEditar(id) {
        formEditarEmpleado.dataset.id = id;
        formEditarEmpleado.reset();

        modalEditarEmpleado.classList.add('activo');
        modalEditarEmpleado.style.display = 'flex';

        await cargarDatosEmpleado(id);
    }

    function cerrarModalEditar() {
        modalEditarEmpleado.classList.remove('activo');
        modalEditarEmpleado.style.display = 'none';
        formEditarEmpleado.reset();
        delete formEditarEmpleado.dataset.id;
    }

    if (btnCerrarModalEditar) btnCerrarModalEditar.addEventListener('click', cerrarModalEditar);
    if (btnCancelarModalEditar) btnCancelarModalEditar.addEventListener('click', cerrarModalEditar);

    async function cargarDatosEmpleado(id) {
        try {
            mostrarNotificacion('Cargando...', 'Obteniendo datos del empleado', 0);

            const respuesta = await fetch(`/api/empleados/${id}/editar`);
            const data = await respuesta.json();

            const emp = data.empleado || data;

            document.getElementById('input-editar-nombre').value = emp.nombre || '';
            document.getElementById('input-editar-email').value = emp.email || '';
            document.getElementById('input-editar-telefono').value = emp.telefono || '';
            document.getElementById('input-editar-rol').value = emp.rol || '';

            ocultarNotificacion();

        } catch (error) {
            console.error('Error al cargar empleado:', error);
            mostrarNotificacion('Error', 'No se pudieron recuperar los datos del empleado.');
        }
    }

    formEditarEmpleado.addEventListener('submit', async (e) => {
        e.preventDefault();

        const id = formEditarEmpleado.dataset.id;
        const empleadoEditado = {
            nombre: document.getElementById('input-editar-nombre').value.trim(),
            email: document.getElementById('input-editar-email').value.trim(),
            telefono: document.getElementById('input-editar-telefono').value.trim(),
            rol: document.getElementById('input-editar-rol').value.trim()
        };

        try {
            const respuesta = await fetch(`/api/empleados/${id}/editar`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(empleadoEditado)
            });

            const data = await respuesta.json();

            if (respuesta.ok && data.exito) {
                mostrarNotificacion('Actualizado', 'Datos actualizados con éxito.');
                cerrarModalEditar();
                cargarEmpleados();
            } else {
                mostrarNotificacion('Error', data.mensaje || 'Error al actualizar empleado.');
            }
        } catch (error) {
            console.error('Error al actualizar empleado:', error);
            mostrarNotificacion('Error de red', 'No se pudo guardar la actualización.');
        }
    });

    // --- EVENTOS DE BÚSQUEDA Y PAGINACIÓN ---

    inputBusqueda.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            paginaActual = 1;
            cargarEmpleados();
        }, 300);
    });

    if (btnAnterior) {
        btnAnterior.addEventListener('click', () => {
            if (paginaActual > 1) {
                paginaActual--;
                cargarEmpleados();
            }
        });
    }

    if (btnSiguiente) {
        btnSiguiente.addEventListener('click', () => {
            if (paginaActual < totalPaginas) {
                paginaActual++;
                cargarEmpleados();
            }
        });
    }

    // Cierre de modales haciendo clic fuera del contenido
    window.addEventListener('click', (e) => {
        if (e.target === modalNuevoEmpleado) cerrarModalNuevo();
        if (e.target === modalEditarEmpleado) cerrarModalEditar();
    });

    // Carga inicial
    cargarEmpleados();
});