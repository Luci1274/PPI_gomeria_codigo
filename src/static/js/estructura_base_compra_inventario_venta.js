// Fecha en la barra lateral derecha
const fecha = document.getElementById('fecha');
fecha.textContent = new Date().toLocaleDateString();


// Barra lateral derecha mobile

const botonCarrito = document.getElementById('boton_carrito');
const barraDerecha = document.getElementById('barra_derecha');
const overlayDerecha = document.getElementById('overlay_derecha');

botonCarrito.addEventListener('click', () => {
    barraDerecha.classList.toggle('abierta_derecha');
    overlayDerecha.classList.toggle('activo_derecha');
    botonCarrito.classList.toggle('oculto_carrito');
});

overlayDerecha.addEventListener('click', () => {
    barraDerecha.classList.remove('abierta_derecha');
    overlayDerecha.classList.remove('activo_derecha');
    botonCarrito.classList.remove('oculto_carrito');
});