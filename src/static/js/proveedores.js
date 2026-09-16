document.addEventListener('DOMContentLoaded', () => {
    // --- ESTADO DE LA APLICACIÓN ---
    let paginaActual = 1;
    let debounceTimer;
    let timerNotificacion;

    // --- ELEMENTOS DEL DOM ---
    const tablaBody = document.getElementById('tabla-proveedor-body');
    const valorMetrica = document.getElementById('valor_metrica');
    
    // Filtros
    const inputBusqueda = document.getElementById('input-busqueda');
    const filtroRubro = document.getElementById('filtro-rubro');
    const filtroEstado = document.getElementById('filtro-estado');
    const filtroCiudad = document.getElementById('filtro-ciudad');

    // Modal Nuevo
    const modalNuevoProveedor = document.getElementById('modal-nuevo-proveedor');
    const btnNuevoProveedor = document.getElementById('btn-nuevo-proveedor');
    const btnCerrarModalNuevo = document.getElementById('btn-cerrar-modal');
    const btnCancelarModalNuevo = document.getElementById('btn-cancelar-modal');
    const formProveedorNuevo = document.querySelector('.modal-cuerpo');

    // Modal Editar
    const formEditarProveedor = document.getElementById('form-editar-proveedor');
    const modalEditarProveedor = document.getElementById('modal-editar-proveedor');
    const btnCerrarModalEditar = document.getElementById('btn-cerrar-modal-editar');
    const btnCancelarModalEditar = document.getElementById('btn-cancelar-modal-editar');

    // Cartel emergente
    const cartelEmergente = document.getElementById('cartel-emergente');
    const cartelTitulo = document.getElementById('cartel-titulo');
    const cartelMensaje = document.getElementById('cartel-mensaje');

    // --- FUNCIONES HELPER DE NOTIFICACIÓN Y CONFIRMACIÓN ---

    function limpiarBotonesCartel() {
        const contenedorBotones = cartelEmergente.querySelector('.cartel-acciones');
        if (contenedorBotones) {
            contenedorBotones.remove();
        }
    }

    function mostrarNotificacion(titulo, mensaje, tiempo = 3000) {
        clearTimeout(timerNotificacion);
        limpiarBotonesCartel(); // Limpiar botones por si venía de un popup de confirmación

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

    /**
     * Muestra el cartel con botones para Aceptar/Cancelar y retorna una Promesa (true/false)
     */
    function pedirConfirmacion(titulo, mensaje) {
        return new Promise((resolve) => {
            clearTimeout(timerNotificacion);
            limpiarBotonesCartel();

            cartelTitulo.textContent = titulo;
            cartelMensaje.textContent = mensaje;

            // Crear contenedor de botones dinámicamente
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

    // --- FUNCIONES PRINCIPALES ---

    async function cargarProveedores() {
        try {
            let estadoValor = '';
            if (filtroEstado.value === 'activo') estadoValor = '1';
            if (filtroEstado.value === 'inactivo') estadoValor = '0';
            if (filtroEstado.value === 'todos') estadoValor = '';

            const params = new URLSearchParams({
                pagina: paginaActual,
                buscar: inputBusqueda.value.trim(),
                rubro: filtroRubro.value !== 'todos' ? filtroRubro.value : '',
                activo: estadoValor,
                ciudad: filtroCiudad.value !== 'todos' ? filtroCiudad.value : ''
            });

            const respuesta = await fetch(`/api/proveedores?${params.toString()}`);
            const data = await respuesta.json();

            if (!respuesta.ok || !data.exito) {
                mostrarNotificacion('Error de datos', data.mensaje || 'Error al obtener los datos.');
                if (data.redireccion) window.location.href = data.redireccion;
                return;
            }

            valorMetrica.textContent = data.total_items;
            renderizarTabla(data.proveedores);
            poblarSelectsFiltro(data.rubros, data.ciudades);

        } catch (error) {
            console.error('Error al cargar proveedores:', error);
            tablaBody.innerHTML = `<tr><td colspan="8" class="texto-centro">Error de conexión al cargar datos.</td></tr>`;
        }
    }

    function renderizarTabla(proveedores) {
        tablaBody.innerHTML = '';

        if (!proveedores || proveedores.length === 0) {
            tablaBody.innerHTML = `
                <tr>
                    <td colspan="8" class="texto-centro">No se encontraron proveedores.</td>
                </tr>`;
            return;
        }

        proveedores.forEach(prov => {
            const tr = document.createElement('tr');
            const esActivo = prov.activo === 1 || prov.activo === true;
            const estadoHTML = `<span class="badge ${esActivo ? 'activo' : 'inactivo'}">${esActivo ? 'Activo' : 'Inactivo'}</span>`;

            tr.innerHTML = `
                <td>${prov.idproveedor}</td>
                <td><strong>${prov.nombre || '-'} - ${prov.rubro || '-'}</strong></td>
                <td>${prov.cuit || '-'}</td>
                <td class="texto-derecha"> ${prov.ciudad} - ${prov.direccion || '-'}</td>
                <td class="texto-derecha"> <a href="https://wa.me/${prov.telefono || '-'}" target="_blank">${prov.telefono || '-'}</a></td>
                <td class="texto-centro"> <a href="mailto:${prov.mail || '-'}" target="_blank">${prov.mail || '-'}</a></td>
                <td class="texto-centro">${estadoHTML}</td>
                <td class="texto-centro">
                    <div class="botones-accion">
                        <button class="btn-accion btn-editar" data-id="${prov.idproveedor}" title="Editar">Modificar</button>
                        <button class="btn-accion borrar btn-eliminar" data-id="${prov.idproveedor}" title="Eliminar">Eliminar</button>
                    </div>
                </td>
            `;

            tablaBody.appendChild(tr);
        });
    }

    async function desactivarProveedor(id) {
        try {
            const respuesta = await fetch(`/proveedores/${id}/desactivar`);
            const data = await respuesta.json();

            if (respuesta.ok && data.exito) {
                mostrarNotificacion('Proveedor desactivado', data.mensaje || 'El proveedor fue desactivado correctamente.');
                cargarProveedores();
            } else {
                mostrarNotificacion('Error', data.mensaje || 'Error al desactivar el proveedor.');
            }
        } catch (error) {
            console.error('Error al desactivar proveedor:', error);
            mostrarNotificacion('Error de conexión', 'Ocurrió un error al intentar desactivar el proveedor.');
        }
    }

    // Delegación de eventos en la tabla (Sincronizado con async/await para la confirmación)
    tablaBody.addEventListener('click', async (e) => {
        const btnEliminar = e.target.closest('.btn-eliminar');
        const btnEditar = e.target.closest('.btn-editar');

        if (btnEliminar) {
            const id = btnEliminar.dataset.id;
            
            const confirmado = await pedirConfirmacion(
                'Desactivar Proveedor',
                '¿Estás seguro de que deseas desactivar este proveedor?'
            );

            if (confirmado) {
                desactivarProveedor(id);
            }
        }

        if (btnEditar) {
            const id = btnEditar.dataset.id;
            abrirModalEditarProveedor(id);
        }
    });

    function poblarSelectsFiltro(rubros, ciudades) {
        if (rubros && filtroRubro.children.length <= 1) {
            rubros.forEach(item => {
                if (item.rubro) {
                    const option = document.createElement('option');
                    option.value = item.rubro;
                    option.textContent = item.rubro;
                    filtroRubro.appendChild(option);
                }
            });
        }

        if (ciudades && filtroCiudad.children.length <= 4) {
            ciudades.forEach(item => {
                if (item.ciudad) {
                    const yaExiste = Array.from(filtroCiudad.options).some(opt => opt.value.toLowerCase() === item.ciudad.toLowerCase());
                    if (!yaExiste) {
                        const option = document.createElement('option');
                        option.value = item.ciudad;
                        option.textContent = item.ciudad;
                        filtroCiudad.appendChild(option);
                    }
                }
            });
        }
    }

    // --- EVENTOS DE FILTROS Y BÚSQUEDA ---

    inputBusqueda.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            paginaActual = 1;
            cargarProveedores();
        }, 300);
    });

    filtroRubro.addEventListener('change', () => { paginaActual = 1; cargarProveedores(); });
    filtroEstado.addEventListener('change', () => { paginaActual = 1; cargarProveedores(); });
    filtroCiudad.addEventListener('change', () => { paginaActual = 1; cargarProveedores(); });

    // --- MANEJO DEL MODAL NUEVO PROVEEDOR ---

    function abrirModal() {
        modalNuevoProveedor.classList.add('activo'); 
        modalNuevoProveedor.style.display = 'flex';
    }

    function cerrarModal() {
        modalNuevoProveedor.classList.remove('activo');
        modalNuevoProveedor.style.display = 'none';
        formProveedorNuevo.reset();
    }

    btnNuevoProveedor.addEventListener('click', abrirModal);
    btnCerrarModalNuevo.addEventListener('click', cerrarModal);
    btnCancelarModalNuevo.addEventListener('click', cerrarModal);

    window.addEventListener('click', (e) => {
        if (e.target === modalNuevoProveedor) cerrarModal();
    });

    formProveedorNuevo.addEventListener('submit', async (e) => {
        e.preventDefault();

        const nuevoProveedor = {
            nombre: document.getElementById('input-proveedor').value.trim(),
            cuit: document.getElementById('input-cuit').value.trim(),
            telefono: document.getElementById('input-telefono').value.trim(),
            mail: document.getElementById('input-email').value.trim(),
            ciudad: document.getElementById('input-ciudad').value.trim(),
            direccion: document.getElementById('input-direccion').value.trim(),
            rubro: document.getElementById('input-rubro').value.trim()
        };

        try {
            const respuesta = await fetch('/api/proveedores', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(nuevoProveedor)
            });

            const data = await respuesta.json();

            if (respuesta.ok && data.exito) {
                mostrarNotificacion('Proveedor guardado', 'El proveedor se ha guardado exitosamente.');
                cerrarModal();
                cargarProveedores();
            } else {
                mostrarNotificacion('Error al guardar', 'No se pudieron guardar los datos del proveedor. Intente nuevamente.');
            }
        } catch (error) {
            console.error('Error al guardar proveedor:', error);
            mostrarNotificacion('Error de red', 'Ocurrió un error en la red al intentar guardar el proveedor.');
        }
    });

    // Carga inicial
    cargarProveedores();

    // --- MANEJO DEL MODAL EDITAR PROVEEDOR ---

    async function abrirModalEditarProveedor(id) {
        formEditarProveedor.dataset.id = id; 
        formEditarProveedor.reset();

        modalEditarProveedor.classList.add('activo'); 
        modalEditarProveedor.style.display = 'flex';

        await cargarDatosProveedor(id);
    }

    function cerrarModalEditar() {
        modalEditarProveedor.classList.remove('activo');
        modalEditarProveedor.style.display = 'none';
        formEditarProveedor.reset();
        delete formEditarProveedor.dataset.id;
    }

    btnCerrarModalEditar.addEventListener('click', cerrarModalEditar);
    btnCancelarModalEditar.addEventListener('click', cerrarModalEditar);

    window.addEventListener('click', (e) => {
        if (e.target === modalEditarProveedor) cerrarModalEditar();
    });

    async function cargarDatosProveedor(id) {
        try {
            mostrarNotificacion('Cargando datos', 'Por favor espere...', 0);

            const respuesta = await fetch(`/proveedores/${id}/editar`);
            const data = await respuesta.json();

            const prov = data.proveedor || data;
            const setValor = (idInput, valor) => {
                const el = document.getElementById(idInput);
                if (el) {
                    el.value = valor || '';
                } else {
                    console.warn(`Elemento con id ${idInput} no encontrado.`);
                }
            };

            setValor('input-editar-proveedor', prov.nombre);
            setValor('input-editar-cuit', prov.cuit);
            setValor('input-editar-telefono', prov.telefono);
            setValor('input-editar-email', prov.mail);
            setValor('input-editar-ciudad', prov.ciudad);
            setValor('input-editar-direccion', prov.direccion);
            setValor('input-editar-rubro', prov.rubro);

            ocultarNotificacion();

        } catch (error) {
            console.error('Error al cargar datos del proveedor:', error);
            mostrarNotificacion('Error al cargar datos', 'No se pudieron obtener los datos del proveedor. Intente nuevamente.');
        }
    }

    formEditarProveedor.addEventListener('submit', async (e) => {
        e.preventDefault();

        const id = formEditarProveedor.dataset.id;
        const proveedorEditado = {
            nombre: document.getElementById('input-editar-proveedor').value.trim(),
            cuit: document.getElementById('input-editar-cuit').value.trim(),
            telefono: document.getElementById('input-editar-telefono').value.trim(),
            mail: document.getElementById('input-editar-email').value.trim(),
            ciudad: document.getElementById('input-editar-ciudad').value.trim(),
            direccion: document.getElementById('input-editar-direccion').value.trim(),
            rubro: document.getElementById('input-editar-rubro').value.trim()
        };

        try {
            const respuesta = await fetch(`/api/proveedores/${id}/editar`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(proveedorEditado)
            });

            const data = await respuesta.json();

            if (respuesta.ok && data.exito) {
                mostrarNotificacion('Proveedor actualizado', 'Los cambios se han guardado correctamente.');
                cerrarModalEditar();
                cargarProveedores();
            } else {
                mostrarNotificacion('Error al actualizar', data.mensaje || 'Error al actualizar el proveedor.');
            }
        } catch (error) {
            console.error('Error al actualizar proveedor:', error);
            mostrarNotificacion('Error de red', 'Ocurrió un error de red al actualizar el proveedor.');
        }
    });
});