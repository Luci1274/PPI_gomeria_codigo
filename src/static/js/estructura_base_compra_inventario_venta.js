// Fecha en la barra lateral derecha
const fecha = document.getElementById('fecha');
fecha.textContent = new Date().toLocaleDateString();


// Barra lateral derecha mobile

const botonCarrito = document.getElementById('boton_carrito');
const barraDerecha = document.getElementById('barra_derecha');

botonCarrito.addEventListener('click', () => {
    barraDerecha.classList.toggle('abierta_derecha');
});