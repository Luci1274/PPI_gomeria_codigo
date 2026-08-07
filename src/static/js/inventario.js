// Captura de elementos
const modal = document.getElementById('modal-producto');
const btnNuevo = document.getElementById('btn-nuevo-producto');
const btnCerrar = document.getElementById('btn-cerrar-modal');
const btnCancelar = document.getElementById('btn-cancelar-modal');

// Abrir modal al hacer clic en "Nuevo Producto"
btnNuevo.addEventListener('click', () => {
modal.classList.add('activo');
});

// Función para cerrar el modal
const cerrarModal = () => {
modal.classList.remove('activo');
};

btnCerrar.addEventListener('click', cerrarModal);
btnCancelar.addEventListener('click', cerrarModal);

// Cerrar al hacer clic fuera del recuadro blanco (en la zona oscura)
window.addEventListener('click', (e) => {
if (e.target === modal) {
    cerrarModal();
}
});
