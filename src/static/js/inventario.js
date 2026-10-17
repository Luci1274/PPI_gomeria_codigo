document.addEventListener('DOMContentLoaded', () => {
    // --- ESTADO DE LA APLICACIÓN ---
    let paginaActual = 1;
    let totalPaginas = 1; // 👈 AGREGADO: Guardamos el total de páginas
    let debounceTimer;
    let timerNotificacion;

    // --- ELEMENTOS DEL DOM ---
    const tablaBody = document.getElementById('tabla-inventario-body');
    const valorMetrica = document.getElementById('valor_metrica');

    // Paginación 👈 AGREGADO
    const btnAnterior = document.getElementById('btn-pag-anterior');
    const btnSiguiente = document.getElementById('btn-pag-siguiente');
    const infoPaginacion = document.getElementById('info-paginacion');

    // Filtros
    const inputBusqueda = document.getElementById('input-busqueda');
    const filtroTipo = document.getElementById('filtro-tipo');
    const filtroMarca = document.getElementById('filtro-marca');
    const filtroEstado = document.getElementById('filtro-estado');

    // Modal Nuevo Producto
    const modalNuevoProducto = document.getElementById('modal-nuevo-producto');
    const btnNuevoProducto = document.getElementById('btn-nuevo-producto');
    const btnCerrarModalNuevo = document.getElementById('btn-cerrar-modal');
    const btnCancelarModalNuevo = document.getElementById('btn-cancelar-modal');
    const formNuevoProducto = document.getElementById('form-nuevo-producto');
    const selectTipoProducto = document.getElementById('select-tipo-producto');
    const inputTipoProducto = document.getElementById('input-tipo');

    // Modal Nuevo Servicio
    const modalNuevoServicio = document.getElementById('modal-nuevo-servicio');
    const btnNuevoServicio = document.getElementById('btn-nuevo-servicio');
    const formNuevoServicio = document.getElementById('form-nuevo-servicio');
    const selectTipoServicio = document.getElementById('select-tipo-servicio');
    const inputTipoServicio = document.getElementById('input-tipo-servicio');

    // Modal Editar Producto
    const modalEditarProducto = document.getElementById('modal-editar-producto');
    const formEditarProducto = document.getElementById('form-editar-producto');
    const btnCerrarModalEditar = document.getElementById('btn-cerrar-modal-editar');
    const btnCancelarModalEditar = document.getElementById('btn-cancelar-modal-editar');
    const selectEditarTipo = document.getElementById('select-editar-tipo');
    const inputEditarTipo = document.getElementById('input-editar-tipo');

    // Modal Editar Servicio
    const modalEditarServicio = document.getElementById('modal-editar-servicio');
    const formEditarServicio = document.getElementById('form-editar-servicio');
    const selectEditarTipoServicio = document.getElementById('select-editar-tipo-servicio');
    const inputEditarTipoServicio = document.getElementById('input-editar-tipo-servicio');

    // Cartel Emergente / Notificaciones
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

    // --- FUNCIONES PRINCIPALES Y PAGINACIÓN ---

    async function cargarProductos() {
        try {
            let estadoValor = '';
            if (filtroEstado.value === 'activo') estadoValor = '1';
            if (filtroEstado.value === 'inactivo') estadoValor = '0';
            if (filtroEstado.value === 'todos') estadoValor = '';

            const params = new URLSearchParams({
                pagina: paginaActual,
                buscar: inputBusqueda.value.trim(),
                tipo: filtroTipo.value !== 'todos' ? filtroTipo.value : '',
                marca: filtroMarca.value !== 'todos' ? filtroMarca.value : '',
                estado: estadoValor
            });

            const respuesta = await fetch(`/api/inventario?${params.toString()}`, {
                method: 'POST'
            });
            const data = await respuesta.json();

            if (!respuesta.ok || !data.exito) {
                mostrarNotificacion('Error de datos', data.mensaje || 'Error al obtener los datos del inventario.');
                if (data.redireccion) window.location.href = data.redireccion;
                return;
            }

            valorMetrica.textContent = data.total_items;
            renderizarTabla(data.productos);
            poblarSelectsFiltro(data.tipos, data.marcas);

            // 👈 CALCULAR Y ACTUALIZAR PAGINACIÓN
            // Toma total_paginas de la API o lo calcula según los items (por defecto asume límite de 10)
            totalPaginas = data.total_paginas || Math.ceil((data.total_items || 0) / (data.limite || 10)) || 1;
            actualizarPaginacionUI();

        } catch (error) {
            console.error('Error al cargar productos:', error);
            tablaBody.innerHTML = `<tr><td colspan="8" class="texto-centro">Error de conexión al cargar datos.</td></tr>`;
        }
    }

    // 👈 FUNCIÓN PARA ACTUALIZAR ESTADO DE LOS BOTONES Y TEXTO
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

    function renderizarTabla(productos) {
        tablaBody.innerHTML = '';

        if (!productos || productos.length === 0) {
            tablaBody.innerHTML = `
                <tr>
                    <td colspan="8" class="texto-centro">No se encontraron productos en el inventario.</td>
                </tr>`;
            return;
        }

        productos.forEach(prod => {
            const tr = document.createElement('tr');
            if (prod.activo === 0 || prod.activo === '0' || prod.activo === false) {
                tr.classList.add('desactivado');
            }
            
            const esActivo = prod.activo === undefined
                || ![0, '0', false].includes(prod.activo);
            const precioFormateado = prod.precio !== undefined && prod.precio !== null 
                ? `$${parseFloat(prod.precio).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` 
                : '-';
            const esServicio = prod.tipo_item === 'servicio';
            const tipoItem = esServicio ? 'servicio' : 'producto';

            const crearCelda = (contenido, className = '') => {
                const td = document.createElement('td');
                td.className = className;
                td.textContent = contenido;
                return td;
            };
            tr.appendChild(crearCelda(prod.idproducto_servicio));

            const celdaNombre = document.createElement('td');
            const nombre = document.createElement('strong');
            nombre.textContent = prod.nombre || '-';
            celdaNombre.appendChild(nombre);
            if (prod.medidas) {
                celdaNombre.appendChild(document.createElement('br'));
                const medidas = document.createElement('small');
                medidas.style.color = '#666';
                medidas.textContent = prod.medidas;
                celdaNombre.appendChild(medidas);
            }
            tr.appendChild(celdaNombre);

            const celdaTipo = document.createElement('td');
            celdaTipo.append(document.createTextNode(prod.tipo || '-'), ' ');
            const etiquetaTipo = document.createElement('small');
            etiquetaTipo.textContent = `(${esServicio ? 'Servicio' : 'Producto'})`;
            celdaTipo.appendChild(etiquetaTipo);
            tr.appendChild(celdaTipo);
            tr.appendChild(crearCelda(prod.marca || '-'));
            tr.appendChild(crearCelda(precioFormateado, 'texto-derecha'));
            const stock = document.createElement('strong');
            stock.textContent = esServicio ? 'No aplica' : `${prod.cantidad_actual ?? 0} u.`;
            const celdaStock = crearCelda('');
            celdaStock.classList.add('texto-centro');
            celdaStock.appendChild(stock);
            tr.appendChild(celdaStock);

            const estado = document.createElement('span');
            estado.className = `badge ${esActivo ? 'activo' : 'inactivo'}`;
            estado.textContent = esActivo ? 'Activo' : 'Inactivo';
            const celdaEstado = crearCelda('');
            celdaEstado.classList.add('texto-centro');
            celdaEstado.appendChild(estado);
            tr.appendChild(celdaEstado);

            const acciones = document.createElement('div');
            acciones.className = 'botones-accion';
            const btnEditar = document.createElement('button');
            btnEditar.className = 'btn-accion btn-editar';
            btnEditar.dataset.id = prod.idproducto_servicio;
            btnEditar.dataset.tipoItem = tipoItem;
            btnEditar.title = 'Editar';
            btnEditar.textContent = 'Modificar';
            const btnEliminar = document.createElement('button');
            btnEliminar.className = 'btn-accion borrar btn-eliminar';
            btnEliminar.dataset.id = prod.idproducto_servicio;
            btnEliminar.dataset.tipoItem = tipoItem;
            btnEliminar.title = 'Eliminar';
            btnEliminar.textContent = 'Eliminar';
            acciones.append(btnEditar, btnEliminar);
            const celdaAcciones = crearCelda('');
            celdaAcciones.classList.add('texto-centro');
            celdaAcciones.appendChild(acciones);
            tr.appendChild(celdaAcciones);

            tablaBody.appendChild(tr);
        });
    }

    async function desactivarProducto(id, tipoItem) {
        try {
            const params = new URLSearchParams({ tipo_item: tipoItem });
            const respuesta = await fetch(`/api/inventario/${id}/desactivar?${params}`);
            const data = await respuesta.json();

            if (respuesta.ok && data.exito) {
                mostrarNotificacion('Artículo desactivado', data.mensaje || 'El artículo fue desactivado correctamente.');
                cargarProductos();
            } else {
                mostrarNotificacion('Error', data.mensaje || 'Error al desactivar el producto.');
            }
        } catch (error) {
            console.error('Error al desactivar producto:', error);
            mostrarNotificacion('Error de conexión', 'Ocurrió un error al intentar desactivar el producto.');
        }
    }

    // Delegación de eventos en la tabla
    tablaBody.addEventListener('click', async (e) => {
        const btnEliminar = e.target.closest('.btn-eliminar');
        const btnEditar = e.target.closest('.btn-editar');

        if (btnEliminar) {
            const id = btnEliminar.dataset.id;
            const tipoItem = btnEliminar.dataset.tipoItem;
            
            const confirmado = await pedirConfirmacion(
                `Desactivar ${tipoItem === 'servicio' ? 'Servicio' : 'Producto'}`,
                `¿Estás seguro de que deseas desactivar este ${tipoItem} del inventario?`
            );

            if (confirmado) {
                desactivarProducto(id, tipoItem);
            }
        }

        if (btnEditar) {
            const id = btnEditar.dataset.id;
            if (btnEditar.dataset.tipoItem === 'servicio') {
                abrirModalEditarServicio(id);
            } else {
                abrirModalEditarProducto(id);
            }
        }
    });

    function poblarSelectTipos(select, tipos) {
        if (!select || !tipos) return;
        const seleccionado = select.value;
        select.replaceChildren(new Option('Seleccionar tipo existente', ''));
        tipos.forEach(item => {
            if (item.tipo) select.add(new Option(item.tipo, item.tipo));
        });
        if ([...select.options].some(option => option.value === seleccionado)) {
            select.value = seleccionado;
        }
    }

    function poblarSelectsFiltro(tipos, marcas) {
        if (tipos) {
            const filtroSeleccionado = filtroTipo.value;
            filtroTipo.replaceChildren(new Option('Tipo: Todos', 'todos'));
            tipos.forEach(item => {
                if (item.tipo) filtroTipo.add(new Option(item.tipo, item.tipo));
            });
            if ([...filtroTipo.options].some(option => option.value === filtroSeleccionado)) {
                filtroTipo.value = filtroSeleccionado;
            }
            [selectTipoProducto, selectTipoServicio, selectEditarTipo, selectEditarTipoServicio]
                .forEach(select => poblarSelectTipos(select, tipos));
        }

        if (marcas && filtroMarca.children.length <= 1) {
            marcas.forEach(item => {
                if (item.marca) {
                    const option = document.createElement('option');
                    option.value = item.marca;
                    option.textContent = item.marca;
                    filtroMarca.appendChild(option);
                }
            });
        }
    }

    // --- EVENTOS DE PAGINACIÓN 👈 AGREGADO ---

    if (btnAnterior) {
        btnAnterior.addEventListener('click', () => {
            if (paginaActual > 1) {
                paginaActual--;
                cargarProductos();
            }
        });
    }

    if (btnSiguiente) {
        btnSiguiente.addEventListener('click', () => {
            if (paginaActual < totalPaginas) {
                paginaActual++;
                cargarProductos();
            }
        });
    }

    // --- EVENTOS DE FILTROS Y BÚSQUEDA ---

    inputBusqueda.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            paginaActual = 1; // Al buscar, reseteamos a la pág 1
            cargarProductos();
        }, 300);
    });

    filtroTipo.addEventListener('change', () => { paginaActual = 1; cargarProductos(); });
    filtroMarca.addEventListener('change', () => { paginaActual = 1; cargarProductos(); });
    filtroEstado.addEventListener('change', () => { paginaActual = 1; cargarProductos(); });

    // --- MANEJO DEL MODAL NUEVO PRODUCTO ---

    function abrirModalNuevo() {
        modalNuevoProducto.classList.add('activo');
        modalNuevoProducto.style.display = 'flex';
    }

    function cerrarModalNuevo() {
        modalNuevoProducto.classList.remove('activo');
        modalNuevoProducto.style.display = 'none';
        formNuevoProducto.reset();
    }

    btnNuevoProducto.addEventListener('click', abrirModalNuevo);
    btnCerrarModalNuevo.addEventListener('click', cerrarModalNuevo);
    btnCancelarModalNuevo.addEventListener('click', cerrarModalNuevo);

    window.addEventListener('click', (e) => {
        if (e.target === modalNuevoProducto) cerrarModalNuevo();
    });

    formNuevoProducto.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btnGuardarProducto = formNuevoProducto.querySelector('button[type="submit"]');
        if (btnGuardarProducto?.disabled) return;
        if (btnGuardarProducto) btnGuardarProducto.disabled = true;

        const formData = new FormData();
        formData.append('nombre', document.getElementById('input-producto').value.trim());
        const tipo = inputTipoProducto.value.trim() || selectTipoProducto.value;
        if (!tipo) {
            mostrarNotificacion('Tipo requerido', 'Selecciona un tipo existente o ingresa uno nuevo.');
            if (btnGuardarProducto) btnGuardarProducto.disabled = false;
            return;
        }
        formData.append('tipo', tipo);
        formData.append('marca', document.getElementById('input-marca').value.trim());
        formData.append('medidas', document.getElementById('input-medidas').value.trim());
        formData.append('cantidad', parseInt(document.getElementById('input-cant-producto').value) || 0);
        formData.append('minimo', parseInt(document.getElementById('input-cant-minima').value) || 0);
        formData.append('precio', parseFloat(document.getElementById('input-precio-venta').value) || 0.0);

        const inputImagen = document.getElementById('input-imagen-producto');
        if (inputImagen && inputImagen.files.length > 0) {
            formData.append('imagen_producto', inputImagen.files[0]);
        }

        try {
            const respuesta = await fetch('/api/inventario/crear', {
                method: 'POST',
                body: formData
            });

            const data = await respuesta.json();

            if (respuesta.ok && data.exito) {
                mostrarNotificacion('Producto guardado', 'El producto se ha guardado exitosamente.');
                cerrarModalNuevo();
                cargarProductos();
            } else {
                mostrarNotificacion(
                    respuesta.status === 409 ? 'Producto duplicado' : 'Error al guardar',
                    data.mensaje || 'No se pudieron guardar los datos.'
                );
            }
        } catch (error) {
            console.error('Error al guardar producto:', error);
            mostrarNotificacion('Error de red', 'Ocurrió un error en la red al intentar guardar el producto.');
        } finally {
            if (btnGuardarProducto) btnGuardarProducto.disabled = false;
        }
    });

    // --- MANEJO DEL MODAL EDITAR PRODUCTO ---

    async function abrirModalEditarProducto(id) {
        formEditarProducto.dataset.id = id;
        formEditarProducto.reset();

        modalEditarProducto.classList.add('activo');
        modalEditarProducto.style.display = 'flex';

        await cargarDatosProducto(id);
    }

    function cerrarModalEditar() {
        modalEditarProducto.classList.remove('activo');
        modalEditarProducto.style.display = 'none';
        formEditarProducto.reset();
        delete formEditarProducto.dataset.id;
    }

    btnCerrarModalEditar.addEventListener('click', cerrarModalEditar);
    btnCancelarModalEditar.addEventListener('click', cerrarModalEditar);

    function resolverTipo(select, input) {
        return input.value.trim() || select.value;
    }

    [selectTipoProducto, selectTipoServicio, selectEditarTipo, selectEditarTipoServicio]
        .forEach(select => select?.addEventListener('change', () => {
            const inputPorSelect = new Map([
                [selectTipoProducto, inputTipoProducto],
                [selectTipoServicio, inputTipoServicio],
                [selectEditarTipo, inputEditarTipo],
                [selectEditarTipoServicio, inputEditarTipoServicio]
            ]);
            const input = inputPorSelect.get(select);
            if (input && select.value) input.value = select.value;
        }));

    function abrirModalServicio() {
        modalNuevoServicio.classList.add('activo');
        modalNuevoServicio.style.display = 'flex';
    }

    function cerrarModalServicio() {
        modalNuevoServicio.classList.remove('activo');
        modalNuevoServicio.style.display = 'none';
        formNuevoServicio.reset();
    }

    btnNuevoServicio?.addEventListener('click', abrirModalServicio);
    document.getElementById('btn-cerrar-modal-servicio')?.addEventListener('click', cerrarModalServicio);
    document.getElementById('btn-cancelar-modal-servicio')?.addEventListener('click', cerrarModalServicio);
    modalNuevoServicio?.addEventListener('click', e => {
        if (e.target === modalNuevoServicio) cerrarModalServicio();
    });

    formNuevoServicio?.addEventListener('submit', async e => {
        e.preventDefault();
        const tipo = resolverTipo(selectTipoServicio, inputTipoServicio);
        if (!tipo) {
            mostrarNotificacion('Tipo requerido', 'Selecciona un tipo existente o ingresa uno nuevo.');
            return;
        }

        const btnGuardar = formNuevoServicio.querySelector('button[type="submit"]');
        btnGuardar.disabled = true;
        try {
            const respuesta = await fetch('/api/inventario/servicios', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    nombre: document.getElementById('input-servicio').value.trim(),
                    tipo,
                    precio: Number(document.getElementById('input-precio-servicio').value)
                })
            });
            const data = await respuesta.json();
            if (!respuesta.ok || !data.exito) {
                mostrarNotificacion(respuesta.status === 409 ? 'Servicio duplicado' : 'Error', data.mensaje || 'No se pudo guardar el servicio.');
                return;
            }
            mostrarNotificacion('Servicio guardado', data.mensaje);
            cerrarModalServicio();
            await cargarProductos();
        } catch (error) {
            console.error('Error al guardar servicio:', error);
            mostrarNotificacion('Error de red', 'No se pudo guardar el servicio.');
        } finally {
            btnGuardar.disabled = false;
        }
    });

    window.addEventListener('click', (e) => {
        if (e.target === modalEditarProducto) cerrarModalEditar();
    });

    async function cargarDatosProducto(id) {
        try {
            mostrarNotificacion('Cargando datos', 'Por favor espere...', 0);

            const respuesta = await fetch(`/inventario/${id}/modificar?tipo_item=producto`);
            const data = await respuesta.json();

            if (!respuesta.ok || !data.exito) {
                mostrarNotificacion('Error', data.mensaje || 'No se pudo obtener el producto.');
                cerrarModalEditar();
                return;
            }

            const prod = data.producto;
            
            const setValor = (idInput, valor) => {
                const el = document.getElementById(idInput);
                if (el) {
                    el.value = valor !== undefined && valor !== null ? valor : '';
                } else {
                    console.warn(`Elemento con id ${idInput} no encontrado.`);
                }
            };

            setValor('input-editar-producto', prod.nombre);
            selectEditarTipo.value = [...selectEditarTipo.options].some(option => option.value === prod.tipo) ? prod.tipo : '';
            setValor('input-editar-tipo', prod.tipo);
            setValor('input-editar-marca', prod.marca);
            setValor('input-editar-medidas', prod.medidas);
            setValor('input-editar-cant-producto', prod.cantidad_actual);
            setValor('input-editar-cant-minima', prod.cantidad_minima);
            setValor('input-editar-precio-venta', prod.precio);

            ocultarNotificacion();

        } catch (error) {
            console.error('Error al cargar datos del producto:', error);
            mostrarNotificacion('Error al cargar datos', 'No se pudieron obtener los datos del producto.');
        }
    }

    formEditarProducto.addEventListener('submit', async (e) => {
        e.preventDefault();

        const id = formEditarProducto.dataset.id;
        const formData = new FormData();

        formData.append('nombre', document.getElementById('input-editar-producto').value.trim());
        formData.append('tipo', resolverTipo(selectEditarTipo, inputEditarTipo));
        formData.append('marca', document.getElementById('input-editar-marca').value.trim());
        formData.append('medidas', document.getElementById('input-editar-medidas').value.trim());
        formData.append('cantidad', parseInt(document.getElementById('input-editar-cant-producto').value) || 0);
        formData.append('minimo', parseInt(document.getElementById('input-editar-cant-minima').value) || 0);
        formData.append('precio', parseFloat(document.getElementById('input-editar-precio-venta').value) || 0.0);

        const inputImagen = document.getElementById('input-editar-imagen');
        if (inputImagen && inputImagen.files.length > 0) {
            formData.append('imagen_producto', inputImagen.files[0]);
        }

        try {
            const respuesta = await fetch(`/api/inventario/${id}/modificar?tipo_item=producto`, {
                method: 'POST',
                body: formData
            });
            const data = await respuesta.json();

            if (respuesta.ok && data.exito) {
                mostrarNotificacion('Producto actualizado', 'Los cambios se han guardado correctamente.');
                cerrarModalEditar();
                cargarProductos();
            } else {
                mostrarNotificacion('Error al actualizar', data.mensaje || 'Error al actualizar el producto.');
            }
        } catch (error) {
            console.error('Error al actualizar producto:', error);
            mostrarNotificacion('Error de red', 'Ocurrió un error de red al actualizar el producto.');
        }
    });

    async function abrirModalEditarServicio(id) {
        formEditarServicio.dataset.id = id;
        formEditarServicio.reset();
        modalEditarServicio.classList.add('activo');
        modalEditarServicio.style.display = 'flex';
        try {
            const respuesta = await fetch(`/inventario/${id}/modificar?tipo_item=servicio`);
            const data = await respuesta.json();
            if (!respuesta.ok || !data.exito) {
                throw new Error(data.mensaje || 'No se pudo cargar el servicio.');
            }
            const servicio = data.producto;
            document.getElementById('input-editar-servicio').value = servicio.nombre || '';
            selectEditarTipoServicio.value = [...selectEditarTipoServicio.options]
                .some(option => option.value === servicio.tipo) ? servicio.tipo : '';
            inputEditarTipoServicio.value = servicio.tipo || '';
            document.getElementById('input-editar-precio-servicio').value = servicio.precio ?? '';
        } catch (error) {
            console.error('Error al cargar el servicio:', error);
            mostrarNotificacion('Error', error.message);
            cerrarModalEditarServicio();
        }
    }

    function cerrarModalEditarServicio() {
        modalEditarServicio.classList.remove('activo');
        modalEditarServicio.style.display = 'none';
        formEditarServicio.reset();
        delete formEditarServicio.dataset.id;
    }

    document.getElementById('btn-cerrar-modal-editar-servicio')
        ?.addEventListener('click', cerrarModalEditarServicio);
    document.getElementById('btn-cancelar-modal-editar-servicio')
        ?.addEventListener('click', cerrarModalEditarServicio);
    modalEditarServicio?.addEventListener('click', e => {
        if (e.target === modalEditarServicio) cerrarModalEditarServicio();
    });

    formEditarServicio?.addEventListener('submit', async e => {
        e.preventDefault();
        const id = formEditarServicio.dataset.id;
        const tipo = resolverTipo(selectEditarTipoServicio, inputEditarTipoServicio);
        if (!tipo) {
            mostrarNotificacion('Tipo requerido', 'Selecciona un tipo existente o ingresa uno nuevo.');
            return;
        }
        const formData = new FormData();
        formData.append('nombre', document.getElementById('input-editar-servicio').value.trim());
        formData.append('tipo', tipo);
        formData.append('precio', document.getElementById('input-editar-precio-servicio').value);
        try {
            const respuesta = await fetch(`/api/inventario/${id}/modificar?tipo_item=servicio`, {
                method: 'POST',
                body: formData
            });
            const data = await respuesta.json();
            if (!respuesta.ok || !data.exito) {
                mostrarNotificacion('Error', data.mensaje || 'No se pudo actualizar el servicio.');
                return;
            }
            cerrarModalEditarServicio();
            mostrarNotificacion('Servicio actualizado', data.mensaje);
            await cargarProductos();
        } catch (error) {
            console.error('Error al actualizar el servicio:', error);
            mostrarNotificacion('Error de red', 'No se pudo actualizar el servicio.');
        }
    });

    // Carga inicial de datos al ingresar a la página
    cargarProductos();
});