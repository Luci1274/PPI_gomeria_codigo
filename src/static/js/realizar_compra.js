document.addEventListener('DOMContentLoaded', () => {
    const cartelEmergente = document.getElementById('cartel-emergente');
    const cartelTitulo = document.getElementById('cartel-titulo');
    const cartelMensaje = document.getElementById('cartel-mensaje');
    const inputBuscar = document.getElementById('buscar-producto');
    const selectCategoria = document.getElementById('select-categoria');
    const selectProveedor = document.getElementById('select-proveedor');
    const contenedorResumen = document.getElementById('lista-resumen');
    const cantidadTotal = document.getElementById('cantidad-total');
    const modal = document.getElementById('modal-overlay');
    const modalFecha = document.getElementById('modal-fecha');
    const modalProveedor = document.getElementById('modal-proveedor');
    const modalTablaBody = document.getElementById('modal-tabla-body');
    const modalTotalProductos = document.getElementById('modal-total-productos');
    const btnRegistrarCompra = document.getElementById('btn-confirmar-compra');
    const btnProveedores = document.getElementById('btn-proveedores');
    const claveCarrito = 'ordenCompraCarrito';
    let timerNotificacion;
    let carrito = [];

    const fechaHoy = new Date().toLocaleDateString('es-AR');
    const spanFecha = document.getElementById('fecha-actual');
    if (spanFecha) spanFecha.textContent = fechaHoy;

    function mostrarNotificacion(titulo, mensaje, tiempo = 3000) {
        if (!cartelEmergente || !cartelTitulo || !cartelMensaje) {
            console.warn(`[${titulo}] ${mensaje}`);
            return;
        }

        clearTimeout(timerNotificacion);
        cartelTitulo.textContent = titulo;
        cartelMensaje.textContent = mensaje;
        cartelEmergente.style.display = 'block';

        if (tiempo > 0) {
            timerNotificacion = setTimeout(() => {
                cartelEmergente.style.display = 'none';
            }, tiempo);
        }
    }

    function obtenerTotalProductos() {
        return carrito.reduce((total, item) => total + item.cantidad, 0);
    }

    function restaurarCarrito() {
        let carritoGuardado;
        try {
            const datosGuardados = localStorage.getItem(claveCarrito);
            if (!datosGuardados) return;
            carritoGuardado = JSON.parse(datosGuardados);
        } catch (error) {
            console.error('No se pudo leer el carrito guardado:', error);
            mostrarNotificacion('Aviso', 'No se pudo recuperar el pedido guardado.');
            return;
        }

        if (!Array.isArray(carritoGuardado)) {
            mostrarNotificacion('Aviso', 'El pedido guardado no tiene un formato válido.');
            return;
        }

        const tarjetasPorId = new Map(
            Array.from(document.querySelectorAll('.tarjeta-producto'))
                .map((tarjeta) => [Number(tarjeta.dataset.id), tarjeta])
        );

        carrito = carritoGuardado.reduce((items, guardado) => {
            const id = Number(guardado?.idproducto_servicio);
            const cantidad = Number(guardado?.cantidad);
            const tarjeta = tarjetasPorId.get(id);

            if (!tarjeta || !Number.isSafeInteger(cantidad) || cantidad <= 0) return items;

            items.push({
                idproducto_servicio: id,
                nombre: tarjeta.dataset.nombre || 'Producto',
                tipo: tarjeta.dataset.tipo || 'Sin tipo',
                imagen: tarjeta.dataset.imagen || '',
                cantidad
            });
            return items;
        }, []);

        if (carrito.length !== carritoGuardado.length) {
            mostrarNotificacion('Aviso', 'Se restauraron los productos válidos del pedido guardado.');
        }
    }

    function actualizarResumen() {
        if (!contenedorResumen) return;
        contenedorResumen.replaceChildren();

        if (carrito.length === 0) {
            const vacio = document.createElement('p');
            vacio.className = 'resumen-vacio';
            vacio.textContent = 'Todavía no agregaste productos.';
            contenedorResumen.appendChild(vacio);
        }

        carrito.forEach((item, indice) => {
            const fila = document.createElement('div');
            fila.className = 'item-pedido';

            const imagen = document.createElement('img');
            imagen.className = 'img-item';
            imagen.src = item.imagen;
            imagen.alt = '';

            const detalles = document.createElement('div');
            detalles.className = 'detalles-item';

            const nombre = document.createElement('strong');
            nombre.textContent = item.nombre;

            const tipo = document.createElement('span');
            tipo.className = 'cant-item';
            tipo.textContent = item.tipo;

            const cantidad = document.createElement('span');
            cantidad.className = 'cant-item';
            cantidad.textContent = `Cantidad: ${item.cantidad}`;

            const btnEliminar = document.createElement('button');
            btnEliminar.type = 'button';
            btnEliminar.className = 'eliminar-producto';
            btnEliminar.dataset.indice = String(indice);
            btnEliminar.setAttribute('aria-label', `Quitar ${item.nombre} del pedido`);
            btnEliminar.textContent = '×';

            detalles.append(nombre, tipo, cantidad);
            fila.append(imagen, detalles, btnEliminar);
            contenedorResumen.appendChild(fila);
        });

        if (cantidadTotal) cantidadTotal.textContent = String(obtenerTotalProductos());
    }

    document.querySelectorAll('.tarjeta-producto').forEach((tarjeta) => {
        tarjeta.addEventListener('click', () => {
            const id = Number(tarjeta.dataset.id);
            if (!Number.isInteger(id) || id <= 0) {
                mostrarNotificacion('Error', 'No se pudo identificar el producto.');
                return;
            }

            const existente = carrito.find((item) => item.idproducto_servicio === id);
            if (existente) {
                existente.cantidad += 1;
            } else {
                carrito.push({
                    idproducto_servicio: id,
                    nombre: tarjeta.dataset.nombre || 'Producto',
                    tipo: tarjeta.dataset.tipo || 'Sin tipo',
                    imagen: tarjeta.dataset.imagen || '',
                    cantidad: 1
                });
            }

            actualizarResumen();
            mostrarNotificacion('¡Añadido!', 'Producto agregado al pedido.', 2000);
        });
    });

    function filtrarProductos() {
        const texto = inputBuscar?.value.trim().toLocaleLowerCase('es') || '';
        const tipoSeleccionado = selectCategoria?.value.toLocaleLowerCase('es') || 'todos';

        document.querySelectorAll('.tarjeta-producto').forEach((tarjeta) => {
            const nombre = (tarjeta.dataset.nombre || '').toLocaleLowerCase('es');
            const tipo = (tarjeta.dataset.tipo || '').toLocaleLowerCase('es');
            tarjeta.style.display = nombre.includes(texto)
                && (tipoSeleccionado === 'todos' || tipo === tipoSeleccionado)
                ? 'flex'
                : 'none';
        });
    }

    inputBuscar?.addEventListener('input', filtrarProductos);
    selectCategoria?.addEventListener('change', filtrarProductos);

    contenedorResumen?.addEventListener('click', (event) => {
        const boton = event.target.closest('.eliminar-producto');
        if (!boton) return;

        carrito.splice(Number(boton.dataset.indice), 1);
        actualizarResumen();
    });

    function abrirModal() {
        if (carrito.length === 0) {
            mostrarNotificacion('Pedido vacío', 'Agrega productos antes de continuar.');
            return;
        }

        if (!selectProveedor?.value) {
            mostrarNotificacion('Proveedor requerido', 'Selecciona un proveedor antes de continuar.');
            selectProveedor?.focus();
            return;
        }

        if (modalFecha) modalFecha.textContent = fechaHoy;
        if (modalProveedor) {
            modalProveedor.textContent = selectProveedor.options[selectProveedor.selectedIndex].text;
        }

        if (modalTablaBody) {
            modalTablaBody.replaceChildren();
            carrito.forEach((item) => {
                const fila = document.createElement('tr');
                [item.nombre, item.tipo, String(item.cantidad)].forEach((valor) => {
                    const celda = document.createElement('td');
                    celda.textContent = valor;
                    fila.appendChild(celda);
                });
                modalTablaBody.appendChild(fila);
            });
        }

        if (modalTotalProductos) {
            modalTotalProductos.textContent = String(obtenerTotalProductos());
        }
        modal?.classList.add('activo');
        btnRegistrarCompra?.focus();
    }

    function cerrarModal() {
        modal?.classList.remove('activo');
    }

    document.getElementById('btn-open-modal')?.addEventListener('click', abrirModal);
    document.getElementById('btn-cerrar-modal')?.addEventListener('click', cerrarModal);
    modal?.addEventListener('click', (event) => {
        if (event.target === modal) cerrarModal();
    });
    window.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && modal?.classList.contains('activo')) cerrarModal();
    });
    document.getElementById('btn-cancelar')?.addEventListener('click', () => {
        window.location.href = '/compras';
    });

    btnProveedores?.addEventListener('click', () => {
        try {
            localStorage.setItem(claveCarrito, JSON.stringify(
                carrito.map(({ idproducto_servicio, cantidad }) => ({
                    idproducto_servicio,
                    cantidad
                }))
            ));
            window.location.href = '/proveedores';
        } catch (error) {
            console.error('No se pudo guardar el pedido antes de abrir proveedores:', error);
            mostrarNotificacion('Error', 'No se pudo guardar el pedido. No se abrió la página de proveedores.', 4000);
        }
    });

    btnRegistrarCompra?.addEventListener('click', async () => {
        const idProveedor = Number(selectProveedor?.value);
        if (!Number.isInteger(idProveedor) || idProveedor <= 0 || carrito.length === 0) {
            cerrarModal();
            mostrarNotificacion('Datos incompletos', 'Selecciona un proveedor y agrega al menos un producto.');
            return;
        }

        btnRegistrarCompra.disabled = true;
        btnRegistrarCompra.textContent = 'Registrando...';

        try {
            const respuesta = await fetch('/api/compras/realizar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id_proveedor: idProveedor,
                    carrito: carrito.map(({ idproducto_servicio, cantidad }) => ({
                        idproducto_servicio,
                        cantidad
                    }))
                })
            });
            const resultado = await respuesta.json();

            if (!respuesta.ok || !resultado.exito) {
                mostrarNotificacion('Error', resultado.mensaje || resultado.error || 'No se pudo registrar la compra.', 4000);
                btnRegistrarCompra.disabled = false;
                btnRegistrarCompra.textContent = 'Registrar Compra';
                return;
            }

            try {
                localStorage.removeItem(claveCarrito);
            } catch (error) {
                console.error('No se pudo borrar el carrito guardado después de registrar la compra:', error);
                mostrarNotificacion('Compra registrada', 'La compra se registró, pero no se pudo borrar el pedido guardado.', 4000);
                setTimeout(() => {
                    window.location.href = resultado.redireccion || '/compras';
                }, 3500);
                return;
            }

            mostrarNotificacion('Compra registrada', resultado.mensaje || 'La compra se registró con éxito.', 2000);
            setTimeout(() => {
                window.location.href = resultado.redireccion || '/compras';
            }, 1800);
        } catch (error) {
            console.error('Error al registrar la compra:', error);
            mostrarNotificacion('Error de conexión', 'Ocurrió un error al enviar la compra.', 4000);
            btnRegistrarCompra.disabled = false;
            btnRegistrarCompra.textContent = 'Registrar Compra';
        }
    });

    restaurarCarrito();
    actualizarResumen();
    if (document.body.dataset.errorDb === 'true') {
        mostrarNotificacion('Error', 'No se pudieron cargar los datos de productos y proveedores.', 5000);
    }
});