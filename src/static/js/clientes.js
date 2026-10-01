document.addEventListener('DOMContentLoaded', () => {
    // --- ESTADO DE LA APLICACIÓN ---
    let paginaActual = 1;
    let totalPaginas = 1;
    let debounceTimer;
    let timerNotificacion;

    // --- ELEMENTOS DEL DOM ---
    const tablaBody = document.querySelector('.tabla-datos tbody');
    const valorMetrica = document.querySelector('.valor-metrica');

    // Paginación
    const btnAnterior = document.getElementById('btn-pag-anterior');
    const btnSiguiente = document.getElementById('btn-pag-siguiente');
    const infoPaginacion = document.getElementById('info-paginacion');

    // Filtros
    const inputBusqueda = document.getElementById('input-busqueda');
    const filtroEstado = document.getElementById('filtro-estado');
    const filtroCiudad = document.getElementById('select-ciudad-filtro'); // Opcional si agregas filtro por ciudad

    // Modal Nuevo Cliente
    const modalNuevoCliente = document.getElementById('modal-overlay');
    const btnNuevoCliente = document.getElementById('btn-open-modal');
    const btnCerrarModalNuevo = document.getElementById('btn-cerrar-modal');
    const btnCancelarModalNuevo = document.getElementById('btn-cancelar-modal');
    const formClienteNuevo = document.querySelector('#modal-overlay .modal-cuerpo');

    // Modal Editar Cliente
    const modalEditarCliente = document.getElementById('modal-editar-overlay');
    const formEditarCliente = document.querySelector('#modal-editar-overlay .modal-cuerpo');
    const btnCerrarModalEditar = document.getElementById('btn-cerrar-modal-editar');
    const btnCancelarModalEditar = document.getElementById('btn-cancelar-modal-editar');

    // Cartel emergente / Notificaciones
    const cartelEmergente = document.getElementById('cartel-emergente');
    const cartelTitulo = document.getElementById('cartel-titulo');
    const cartelMensaje = document.getElementById('cartel-mensaje');

    // --- FUNCIONES HELPER DE NOTIFICACIÓN Y CONFIRMACIÓN ---

    function limpiarBotonesCartel() {
        if (!cartelEmergente) return;
        const contenedorBotones = cartelEmergente.querySelector('.cartel-acciones');
        if (contenedorBotones) {
            contenedorBotones.remove();
        }
    }

    function mostrarNotificacion(titulo, mensaje, tiempo = 3000) {
        if (!cartelEmergente) {
            alert(`${titulo}: ${mensaje}`);
            return;
        }
        clearTimeout(timerNotificacion);
        limpiarBotonesCartel();

        if (cartelTitulo) cartelTitulo.textContent = titulo;
        if (cartelMensaje) cartelMensaje.textContent = mensaje;
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
            if (!cartelEmergente) {
                resolve(confirm(`${titulo}\n${mensaje}`));
                return;
            }

            clearTimeout(timerNotificacion);
            limpiarBotonesCartel();

            if (cartelTitulo) cartelTitulo.textContent = titulo;
            if (cartelMensaje) cartelMensaje.textContent = mensaje;

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

            const btnConfirmar = document.getElementById('btn-confirmar-cartel');
            const btnCancelar = document.getElementById('btn-cancelar-cartel');

            btnConfirmar.onclick = () => {
                ocultarNotificacion();
                resolve(true);
            };

            btnCancelar.onclick = () => {
                ocultarNotificacion();
                resolve(false);
            };
        });
    }

    // --- CARGA DE DATOS Y RENDERIZADO DE TABLA ---

    async function cargarClientes() {
        try {
            let estadoValor = '1';
            if (filtroEstado) {
                if (filtroEstado.value === 'activo') estadoValor = '1';
                if (filtroEstado.value === 'inactivo') estadoValor = '0';
                if (filtroEstado.value === 'todos') estadoValor = '';
            }

            const params = new URLSearchParams({
                pagina: paginaActual,
                buscar: inputBusqueda ? inputBusqueda.value.trim() : '',
                activo: estadoValor,
                ciudad: (filtroCiudad && filtroCiudad.value !== 'todos') ? filtroCiudad.value : ''
            });

            const respuesta = await fetch(`/api/clientes?${params.toString()}`);
            const data = await respuesta.json();

            if (!respuesta.ok || !data.exito) {
                mostrarNotificacion('Error de datos', data.mensaje || 'Error al obtener los clientes.');
                if (data.redireccion) window.location.href = data.redireccion;
                return;
            }

            if (valorMetrica) {
                valorMetrica.textContent = data.total_items;
            }

            renderizarTabla(data.clientes);
            poblarSelectsCiudad(data.ciudades);

            totalPaginas = data.total_paginas || Math.ceil((data.total_items || 0) / 10) || 1;
            actualizarPaginacionUI();

        } catch (error) {
            console.error('Error al cargar clientes:', error);
            if (tablaBody) {
                tablaBody.innerHTML = `<tr><td colspan="7" class="texto-centro">Error de conexión al cargar datos.</td></tr>`;
            }
        }
    }

    function actualizarPaginacionUI() {
        if (infoPaginacion) {
            infoPaginacion.textContent = `Página ${paginaActual} de ${totalPaginas}`;
        }
        if (btnAnterior) {
            btnAnterior.disabled = (paginaActual <= 1);
        }
        if (btnSiguiente) {
            btnSiguiente.disabled = (paginaActual >= totalPaginas);
        }
    }

    function renderizarTabla(clientes) {
        if (!tablaBody) return;
        tablaBody.innerHTML = '';

        if (!clientes || clientes.length === 0) {
            tablaBody.innerHTML = `
                <tr>
                    <td colspan="7" class="texto-centro">No se encontraron clientes.</td>
                </tr>`;
            return;
        }

        clientes.forEach(cli => {
            const tr = document.createElement('tr');
            const idCliente = cli.idcliente || cli.id_cliente || cli.id;
            const esActivo = cli.activo === 1 || cli.activo === true || cli.activo === '1';
            const estadoHTML = `<span class="estado-badge ${esActivo ? 'activo' : 'inactivo'}">${esActivo ? 'Activo' : 'No Activo'}</span>`;

            // Formatear nombre completo
            const nombreCompleto = cli.apellido ? `${cli.nombre || ''} ${cli.apellido}`.trim() : (cli.nombre || '-');
            const contactoInfo = cli.numero_tel || cli.telefono || cli.mail || '-';

            tr.innerHTML = `
                <td><strong>${nombreCompleto}</strong></td>
                <td>${cli.cuit || cli.dni || '-'}</td>
                <td>${contactoInfo}</td>
                <td>${cli.ciudad || '-'}</td>
                <td>${cli.direccion || '-'}</td>
                <td>${estadoHTML}</td>
                <td>
                    <div class="btn-acciones">
                        <button class="btn-accion editar btn-editar" data-id="${idCliente}" title="Editar">Modificar</button>
                        <button class="btn-accion eliminar btn-eliminar" data-id="${idCliente}" title="Eliminar">Eliminar</button>
                    </div>
                </td>
            `;

            tablaBody.appendChild(tr);
        });
    }

    function poblarSelectsCiudad(ciudades) {
        if (!ciudades || !filtroCiudad) return;
        ciudades.forEach(item => {
            const nombreCiudad = typeof item === 'string' ? item : item.ciudad;
            if (nombreCiudad) {
                const yaExiste = Array.from(filtroCiudad.options).some(opt => opt.value.toLowerCase() === nombreCiudad.toLowerCase());
                if (!yaExiste) {
                    const option = document.createElement('option');
                    option.value = nombreCiudad;
                    option.textContent = nombreCiudad;
                    filtroCiudad.appendChild(option);
                }
            }
        });
    }

    // --- ACCIÓN DESACTIVAR CLIENTE ---

    async function desactivarCliente(id) {
        try {
            const respuesta = await fetch(`/clientes/${id}/desactivar`);
            const data = await respuesta.json();

            if (respuesta.ok && data.exito) {
                mostrarNotificacion('Cliente desactivado', data.mensaje || 'El cliente fue desactivado correctamente.');
                cargarClientes();
            } else {
                mostrarNotificacion('Error', data.mensaje || 'Error al desactivar el cliente.');
            }
        } catch (error) {
            console.error('Error al desactivar cliente:', error);
            mostrarNotificacion('Error de conexión', 'Ocurrió un error al intentar desactivar el cliente.');
        }
    }

    // Delegación de eventos en la tabla (Editar / Eliminar)
    if (tablaBody) {
        tablaBody.addEventListener('click', async (e) => {
            const btnEliminar = e.target.closest('.btn-eliminar');
            const btnEditar = e.target.closest('.btn-editar');

            if (btnEliminar) {
                const id = btnEliminar.dataset.id;
                const confirmado = await pedirConfirmacion(
                    'Desactivar Cliente',
                    '¿Estás seguro de que deseas desactivar este cliente?'
                );

                if (confirmado) {
                    desactivarCliente(id);
                }
            }

            if (btnEditar) {
                const id = btnEditar.dataset.id;
                abrirModalEditarCliente(id);
            }
        });
    }

    // --- EVENTOS DE FILTROS Y BÚSQUEDA ---

    if (inputBusqueda) {
        inputBusqueda.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                paginaActual = 1;
                cargarClientes();
            }, 300);
        });
    }

    if (filtroEstado) {
        filtroEstado.addEventListener('change', () => {
            paginaActual = 1;
            cargarClientes();
        });
    }

    if (filtroCiudad) {
        filtroCiudad.addEventListener('change', () => {
            paginaActual = 1;
            cargarClientes();
        });
    }

    // --- EVENTOS DE PAGINACIÓN ---

    if (btnAnterior) {
        btnAnterior.addEventListener('click', () => {
            if (paginaActual > 1) {
                paginaActual--;
                cargarClientes();
            }
        });
    }

    if (btnSiguiente) {
        btnSiguiente.addEventListener('click', () => {
            if (paginaActual < totalPaginas) {
                paginaActual++;
                cargarClientes();
            }
        });
    }

    // --- MANEJO DEL MODAL NUEVO CLIENTE ---

    function abrirModalNuevo() {
        if (!modalNuevoCliente) return;
        modalNuevoCliente.classList.add('activo');
        modalNuevoCliente.style.display = 'flex';
    }

    function cerrarModalNuevo() {
        if (!modalNuevoCliente) return;
        modalNuevoCliente.classList.remove('activo');
        modalNuevoCliente.style.display = 'none';
        if (formClienteNuevo) formClienteNuevo.reset();
    }

    if (btnNuevoCliente) btnNuevoCliente.addEventListener('click', abrirModalNuevo);
    if (btnCerrarModalNuevo) btnCerrarModalNuevo.addEventListener('click', cerrarModalNuevo);
    if (btnCancelarModalNuevo) btnCancelarModalNuevo.addEventListener('click', cerrarModalNuevo);

    if (formClienteNuevo) {
        formClienteNuevo.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Desglosamos nombre si se ingresó nombre completo en el input
            const nombreInput = document.getElementById('input-cliente')?.value.trim() || '';
            const partesNombre = nombreInput.split(' ');
            const nombre = partesNombre[0] || '';
            const apellido = partesNombre.slice(1).join(' ') || '';

            const nuevoCliente = {
                nombre: nombre,
                apellido: apellido,
                cuit: document.getElementById('input-cuit')?.value.trim() || '',
                numero_tel: document.getElementById('input-telefono')?.value.trim() || '',
                ciudad: document.getElementById('select-ciudad')?.value || '',
                direccion: document.getElementById('input-direccion')?.value.trim() || '',
                mail: ''
            };

            try {
                const respuesta = await fetch('/api/clientes/crear', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(nuevoCliente)
                });

                const data = await respuesta.json();

                if (respuesta.ok && data.exito) {
                    mostrarNotificacion('Cliente creado', 'El cliente se ha registrado exitosamente.');
                    cerrarModalNuevo();
                    cargarClientes();
                } else {
                    mostrarNotificacion('Error al guardar', data.mensaje || 'No se pudieron guardar los datos del cliente.');
                }
            } catch (error) {
                console.error('Error al guardar cliente:', error);
                mostrarNotificacion('Error de red', 'Ocurrió un error en la red al intentar guardar el cliente.');
            }
        });
    }

    // --- MANEJO DEL MODAL EDITAR CLIENTE ---

    async function abrirModalEditarCliente(id) {
        if (!modalEditarCliente || !formEditarCliente) return;
        
        formEditarCliente.dataset.id = id;
        formEditarCliente.reset();

        modalEditarCliente.classList.add('activo');
        modalEditarCliente.style.display = 'flex';

        await cargarDatosCliente(id);
    }

    function cerrarModalEditar() {
        if (!modalEditarCliente) return;
        modalEditarCliente.classList.remove('activo');
        modalEditarCliente.style.display = 'none';
        if (formEditarCliente) {
            formEditarCliente.reset();
            delete formEditarCliente.dataset.id;
        }
    }

    if (btnCerrarModalEditar) btnCerrarModalEditar.addEventListener('click', cerrarModalEditar);
    if (btnCancelarModalEditar) btnCancelarModalEditar.addEventListener('click', cerrarModalEditar);

    async function cargarDatosCliente(id) {
        try {
            mostrarNotificacion('Cargando datos', 'Por favor espere...', 0);

            const respuesta = await fetch(`/clientes/${id}/editar`);
            const data = await respuesta.json();

            if (!respuesta.ok || !data.exito) {
                mostrarNotificacion('Error', data.mensaje || 'No se pudo obtener el cliente.');
                cerrarModalEditar();
                return;
            }

            const cli = data.cliente;

            const setValor = (idInput, valor) => {
                const el = document.getElementById(idInput);
                if (el) el.value = valor || '';
            };

            const nombreMostrar = cli.apellido ? `${cli.nombre || ''} ${cli.apellido}`.trim() : (cli.nombre || '');
            setValor('input-editar-cliente', nombreMostrar);
            setValor('input-editar-cuit', cli.cuit || cli.dni);
            setValor('input-editar-telefono', cli.numero_tel || cli.telefono);
            setValor('select-editar-ciudad', (cli.ciudad || '').toLowerCase());
            setValor('input-editar-direccion', cli.direccion);
            setValor('select-editar-estado', (cli.activo === 1 || cli.activo === true) ? 'activo' : 'inactivo');

            ocultarNotificacion();

        } catch (error) {
            console.error('Error al cargar datos del cliente:', error);
            mostrarNotificacion('Error al cargar datos', 'No se pudieron obtener los datos del cliente.');
        }
    }

    if (formEditarCliente) {
        formEditarCliente.addEventListener('submit', async (e) => {
            e.preventDefault();

            const id = formEditarCliente.dataset.id;
            const nombreInput = document.getElementById('input-editar-cliente')?.value.trim() || '';
            const partesNombre = nombreInput.split(' ');
            const nombre = partesNombre[0] || '';
            const apellido = partesNombre.slice(1).join(' ') || '';

            const clienteEditado = {
                nombre: nombre,
                apellido: apellido,
                cuit: document.getElementById('input-editar-cuit')?.value.trim() || '',
                numero_tel: document.getElementById('input-editar-telefono')?.value.trim() || '',
                ciudad: document.getElementById('select-editar-ciudad')?.value || '',
                direccion: document.getElementById('input-editar-direccion')?.value.trim() || '',
                mail: ''
            };

            try {
                const respuesta = await fetch(`/api/clientes/${id}/editar`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(clienteEditado)
                });

                const data = await respuesta.json();

                if (respuesta.ok && data.exito) {
                    mostrarNotificacion('Cliente actualizado', 'Los cambios se han guardado correctamente.');
                    cerrarModalEditar();
                    cargarClientes();
                } else {
                    mostrarNotificacion('Error al actualizar', data.mensaje || 'Error al actualizar el cliente.');
                }
            } catch (error) {
                console.error('Error al actualizar cliente:', error);
                mostrarNotificacion('Error de red', 'Ocurrió un error de red al actualizar el cliente.');
            }
        });
    }

    // Cierre de modales al hacer clic fuera
    window.addEventListener('click', (e) => {
        if (e.target === modalNuevoCliente) cerrarModalNuevo();
        if (e.target === modalEditarCliente) cerrarModalEditar();
    });

    // Carga inicial
    cargarClientes();
});