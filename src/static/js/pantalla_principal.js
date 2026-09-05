document.addEventListener("DOMContentLoaded", () => {
    inicializarFecha();
    obtenerDatosDashboard();

    // Actualizar datos automáticamente cada 10 segundos (10000 ms)
    setInterval(obtenerDatosDashboard, 10000);
});

// 1. Muestra la fecha actual formateada
function inicializarFecha() {
    const contenedorFecha = document.getElementById("fecha-actual");
    const opciones = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const hoy = new Date().toLocaleDateString('es-ES', opciones);
    
    // Capitalizar primera letra de la fecha
    contenedorFecha.textContent = hoy.charAt(0).toUpperCase() + hoy.slice(1);
}

// 2. Consulta la API en Flask y actualiza la pantalla
async function obtenerDatosDashboard() {
    try {
        const respuesta = await fetch('/api/datos-dashboard');
        const resultado = await respuesta.json();

        if (!respuesta.ok || !resultado.exito) {
            mostrarCartelError(resultado.mensaje || "Error en el servidor de base de datos.");
            return;
        }

        // Si la conexión fue exitosa, ocultamos cualquier alerta previa
        ocultarCartelError();

        // Actualizamos los datos del DOM
        actualizarMetricas(resultado);
        actualizarTablaVentas(resultado.ultimas_ventas);
        actualizarTablaStock(resultado.productos_bajos);

    } catch (error) {
        console.error("Error de conexión:", error);
        mostrarCartelError("Error: No se pudo establecer conexión con el servidor.");
    }
}

// Actualiza las tarjetas superiores
function actualizarMetricas(datos) {
    document.getElementById("valor-stock").textContent = datos.total_productos ?? 0;
    document.getElementById("valor-cliente").textContent = datos.total_clientes ?? 0;
    document.getElementById("valor-venta").textContent = datos.ventas_dia ?? 0;
}

// Renderiza dinámicamente la tabla de últimas ventas
function actualizarTablaVentas(ventas) {
    const tbody = document.getElementById("tabla-ultimas-ventas");
    tbody.innerHTML = "";

    if (!ventas || ventas.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;">No hay ventas recientes.</td></tr>`;
        return;
    }

    ventas.forEach(venta => {
        const fila = document.createElement("tr");
        fila.innerHTML = `
            <td>${venta.nombre} ${venta.apellido}</td>
            <td>$${venta.total}</td>
            <td>${venta.forma_pago}</td>
            <td>${venta.estado}</td>
        `;
        tbody.appendChild(fila);
    });
}

// Renderiza dinámicamente la tabla de stock bajo
function actualizarTablaStock(productos) {
    const tbody = document.getElementById("tabla-stock-bajo");
    tbody.innerHTML = "";

    if (!productos || productos.length === 0) {
        tbody.innerHTML = `<tr><td colspan="3" style="text-align:center;">No hay productos con stock bajo.</td></tr>`;
        return;
    }

    productos.forEach(prod => {
        const fila = document.createElement("tr");
        fila.innerHTML = `
            <td>${prod.nombre}</td>
            <td>${prod.cantidad_actual}</td>
            <td><button class="btn-accion">Reponer</button></td>
        `;
        tbody.appendChild(fila);
    });
}

// 3. Funciones para gestionar el cartel de error
function mostrarCartelError(mensaje) {
    const cartel = document.getElementById("cartel-error");
    const texto = document.getElementById("mensaje-error-texto");
    
    texto.textContent = mensaje;
    cartel.style.display = "flex";
}

function ocultarCartelError() {
    const cartel = document.getElementById("cartel-error");
    cartel.style.display = "none";
}