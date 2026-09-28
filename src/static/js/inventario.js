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

    // Modal Editar Producto
    const modalEditarProducto = document.getElementById('modal-editar-producto');
    const formEditarProducto = document.getElementById('form-editar-producto');
    const btnCerrarModalEditar = document.getElementById('btn-cerrar-modal-editar');
    const btnCancelarModalEditar = document.getElementById('btn-cancelar-modal-editar');

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
            
            const esActivo = prod.activo === undefined || prod.activo === 1 || prod.activo === true;
            const estadoHTML = `<span class="badge ${esActivo ? 'activo' : 'inactivo'}">${esActivo ? 'Activo' : 'Inactivo'}</span>`;

            const precioFormateado = prod.precio !== undefined && prod.precio !== null 
                ? `$${parseFloat(prod.precio).toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` 
                : '-';

            tr.innerHTML = `
                <td>${prod.idproducto_servicio}</td>
                <td><strong>${prod.nombre || '-'}</strong> ${prod.medidas ? `<br><small style="color: #666;">${prod.medidas}</small>` : ''}</td>
                <td>${prod.tipo || '-'}</td>
                <td>${prod.marca || '-'}</td>
                <td class="texto-derecha">${precioFormateado}</td>
                <td class="texto-centro"><strong>${prod.cantidad_actual !== undefined ? prod.cantidad_actual : 0} u.</strong></td>
                <td class="texto-centro">${estadoHTML}</td>
                <td class="texto-centro">
                    <div class="botones-accion">
                        <button class="btn-accion btn-editar" data-id="${prod.idproducto_servicio}" title="Editar">Modificar</button>
                        <button class="btn-accion borrar btn-eliminar" data-id="${prod.idproducto_servicio}" title="Eliminar">Eliminar</button>
                    </div>
                </td>
            `;

            tablaBody.appendChild(tr);
        });
    }

    async function desactivarProducto(id) {
        try {
            const respuesta = await fetch(`/api/inventario/${id}/desactivar`);
            const data = await respuesta.json();

            if (respuesta.ok && data.exito) {
                mostrarNotificacion('Producto desactivado', data.mensaje || 'El producto fue desactivado correctamente.');
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
            
            const confirmado = await pedirConfirmacion(
                'Desactivar Producto',
                '¿Estás seguro de que deseas desactivar este producto del inventario?'
            );

            if (confirmado) {
                desactivarProducto(id);
            }
        }

        if (btnEditar) {
            const id = btnEditar.dataset.id;
            abrirModalEditarProducto(id);
        }
    });

    function poblarSelectsFiltro(tipos, marcas) {
        if (tipos && filtroTipo.children.length <= 1) {
            tipos.forEach(item => {
                if (item.tipo) {
                    const option = document.createElement('option');
                    option.value = item.tipo;
                    option.textContent = item.tipo;
                    filtroTipo.appendChild(option);
                }
            });
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

        const formData = new FormData();
        formData.append('nombre', document.getElementById('input-producto').value.trim());
        formData.append('tipo', document.getElementById('input-tipo').value.trim());
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
                mostrarNotificacion('Error al guardar', data.mensaje || 'No se pudieron guardar los datos.');
            }
        } catch (error) {
            console.error('Error al guardar producto:', error);
            mostrarNotificacion('Error de red', 'Ocurrió un error en la red al intentar guardar el producto.');
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

    window.addEventListener('click', (e) => {
        if (e.target === modalEditarProducto) cerrarModalEditar();
    });

    async function cargarDatosProducto(id) {
        try {
            mostrarNotificacion('Cargando datos', 'Por favor espere...', 0);

            const respuesta = await fetch(`/inventario/${id}/modificar`);
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
        formData.append('tipo', document.getElementById('input-editar-tipo').value.trim());
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
            const respuesta = await fetch(`/api/inventario/${id}/modificar`, {
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

    // Carga inicial de datos al ingresar a la página
    cargarProductos();
});