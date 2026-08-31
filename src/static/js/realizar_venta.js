document.addEventListener("DOMContentLoaded", () => {
    // Estado global del carrito en la vista actual
    let carrito = [];

    // Captura de elementos del DOM
    const contenedorProductos = document.querySelector(".contenedor_grilla_productos");
    const listaCarrito = document.getElementById("lista_carrito");
    const totalVentaSpan = document.getElementById("total_venta");
    const btnConfirmarVenta = document.getElementById("btn_confirmar_venta");
    const btnRestablecer = document.getElementById("btn_restablecer") || document.querySelector(".restablecer");
    const inputBusqueda = document.querySelector('input[name="busqueda"]');
    const botonesTipo = document.querySelectorAll(".btn_tipo");

    // ------------------------------------------
    // 1. Añadir Producto al Carrito             #
    // ------------------------------------------
    if (contenedorProductos) {
        contenedorProductos.addEventListener("click", (e) => {
            const btn = e.target.closest(".btn_agregar_carrito");
            if (!btn) return;

            const idproducto = parseInt(btn.dataset.id);
            const nombre = btn.dataset.nombre;
            const precio = parseFloat(btn.dataset.precio);

            agregarAlCarrito(idproducto, nombre, precio);
        });
    }

    function agregarAlCarrito(idproducto, nombre, precio) {
        const itemExistente = carrito.find(item => item.idproducto === idproducto);

        if (itemExistente) {
            itemExistente.cantidad += 1;
        } else {
            carrito.push({
                idproducto: idproducto,
                nombre: nombre,
                precio: precio,
                cantidad: 1
            });
        }
        actualizarVistaCarrito();
    }

    // ------------------------------------------
    // 2. Dibujar / Renderizar el Carrito       #
    // ------------------------------------------
    function actualizarVistaCarrito() {
        if (!listaCarrito) return;

        if (carrito.length === 0) {
            listaCarrito.innerHTML = '<p class="carrito_vacio">No hay productos agregados a la venta.</p>';
            if (totalVentaSpan) totalVentaSpan.textContent = "0.00";
            return;
        }

        listaCarrito.innerHTML = "";
        let total = 0;

        carrito.forEach((item, index) => {
            const subtotal = item.precio * item.cantidad;
            total += subtotal;

            const itemDiv = document.createElement("div");
            itemDiv.className = "item_carrito";
            itemDiv.innerHTML = `
                <div class="info_item_carrito">
                    <p class="nombre_item"><strong>${item.nombre}</strong></p>
                    <p class="subtotal_item">$${item.precio.toFixed(2)} x ${item.cantidad} = <strong>$${subtotal.toFixed(2)}</strong></p>
                </div>
                <div class="acciones_item_carrito">
                    <button type="button" class="btn_restar" data-index="${index}">-</button>
                    <span class="cant_item">${item.cantidad}</span>
                    <button type="button" class="btn_sumar" data-index="${index}">+</button>
                    <button type="button" class="btn_eliminar" data-index="${index}">
                        <ion-icon name="trash-outline"></ion-icon>
                    </button>
                </div>
            `;
            listaCarrito.appendChild(itemDiv);
        });

        if (totalVentaSpan) totalVentaSpan.textContent = total.toFixed(2);
    }

    // ------------------------------------------
    // 3. Modificar Cantidades o Eliminar Items #
    // ------------------------------------------
    if (listaCarrito) {
        listaCarrito.addEventListener("click", (e) => {
            const btn = e.target.closest("button");
            if (!btn) return;

            const index = parseInt(btn.dataset.index);

            if (btn.classList.contains("btn_sumar")) {
                carrito[index].cantidad += 1;
            } else if (btn.classList.contains("btn_restar")) {
                carrito[index].cantidad -= 1;
                if (carrito[index].cantidad <= 0) {
                    carrito.splice(index, 1);
                }
            } else if (btn.classList.contains("btn_eliminar")) {
                carrito.splice(index, 1);
            }

            actualizarVistaCarrito();
        });
    }

    // ------------------------------------------
    // 4. Vaciar Carrito (Botón Restablecer)    #
    // ------------------------------------------
    if (btnRestablecer) {
        btnRestablecer.addEventListener("click", () => {
            carrito = [];
            actualizarVistaCarrito();
        });
    }

    // ------------------------------------------
    // 5. Enviar Transacción (POST al Backend)  #
    // ------------------------------------------
    if (btnConfirmarVenta) {
        btnConfirmarVenta.addEventListener("click", async () => {
            if (carrito.length === 0) {
                alert("El carrito de compra está vacío.");
                return;
            }

            btnConfirmarVenta.disabled = true;
            btnConfirmarVenta.textContent = "Procesando...";

            const payload = {
                carrito: carrito,
                id_cliente: null, // Puedes vincularlo a un <select> de clientes si agregas uno
                descuento: 0.0,
                numero_factura: `FAC-${Date.now()}`
            };

            try {
                const respuesta = await fetch("/api/ventas/realizar", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                const resultado = await respuesta.json();

                if (respuesta.ok && resultado.exito) {
                    alert(resultado.mensaje);
                    carrito = [];
                    actualizarVistaCarrito();
                    if (resultado.redireccion) {
                        window.location.href = resultado.redireccion;
                    }
                } else {
                    alert(`Error: ${resultado.mensaje || "No se pudo procesar la venta."}`);
                    if (resultado.redireccion) {
                        window.location.href = resultado.redireccion;
                    }
                }
            } catch (error) {
                console.error("Error al enviar la venta:", error);
                alert("Ocurrió un error de conexión al intentar enviar la venta.");
            } finally {
                btnConfirmarVenta.disabled = false;
                btnConfirmarVenta.textContent = "Confirmar Venta";
            }
        });
    }

    // Captura del elemento select
    const selectCliente = document.getElementById("select_cliente");

    if (btnConfirmarVenta) {
        btnConfirmarVenta.addEventListener("click", async () => {
            if (carrito.length === 0) {
                alert("El carrito de compra está vacío.");
                return;
            }

            // Si hay un ID seleccionado lo convierte a número; si es cadena vacía, asigna null
            const idClienteSeleccionado = (selectCliente && selectCliente.value) 
                ? parseInt(selectCliente.value, 10) 
                : null;

            btnConfirmarVenta.disabled = true;
            btnConfirmarVenta.textContent = "Procesando...";

            const payload = {
                carrito: carrito,
                id_cliente: idClienteSeleccionado, // Se envía null o el ID del cliente seleccionado
                descuento: 0.0,
                numero_factura: `FAC-${Date.now()}`
            };

            try {
                const respuesta = await fetch("/api/ventas/realizar", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const resultado = await respuesta.json();

                if (respuesta.ok && resultado.exito) {
                    alert(resultado.mensaje);
                    carrito = [];
                    actualizarVistaCarrito();
                    
                    // Limpia el selector de cliente al reiniciar el carrito
                    if (selectCliente) selectCliente.value = "";

                    if (resultado.redireccion) {
                        window.location.href = resultado.redireccion;
                    }
                } else {
                    alert(`Error: ${resultado.mensaje || "No se pudo procesar la venta."}`);
                }
            } catch (error) {
                console.error("Error al registrar venta:", error);
                alert("Ocurrió un error de conexión al enviar la venta.");
            } finally {
                btnConfirmarVenta.disabled = false;
                btnConfirmarVenta.textContent = "Confirmar Venta";
            }
        });
    }

    // ------------------------------------------
    // 6. Filtrado Dinámico Instantáneo (Frontend)
    // ------------------------------------------
    if (inputBusqueda && contenedorProductos) {
        inputBusqueda.addEventListener("input", (e) => {
            const termino = e.target.value.toLowerCase().trim();
            const tarjetas = contenedorProductos.querySelectorAll(".tarjeta_producto");

            tarjetas.forEach(tarjeta => {
                const texto = tarjeta.textContent.toLowerCase();
                tarjeta.style.display = texto.includes(termino) ? "" : "none";
            });
        });
    }

    if (botonesTipo.length > 0 && contenedorProductos) {
        botonesTipo.forEach(btn => {
            btn.addEventListener("click", () => {
                botonesTipo.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");

                const tipoSeleccionado = btn.dataset.tipo;
                const tarjetas = contenedorProductos.querySelectorAll(".tarjeta_producto");

                tarjetas.forEach(tarjeta => {
                    if (tipoSeleccionado === "todos" || !tipoSeleccionado) {
                        tarjeta.style.display = "";
                    } else {
                        // Compara con un atributo data-tipo en la tarjeta si lo incluyes
                        const tipoTarjeta = tarjeta.dataset.tipo;
                        tarjeta.style.display = (tipoTarjeta === tipoSeleccionado) ? "" : "none";
                    }
                });
            });
        });
    }
});