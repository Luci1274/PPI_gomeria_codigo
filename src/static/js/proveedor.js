// Captura de elementos
const modal = document.getElementById('modal-proveedor');
const btnNuevo = document.getElementById('btn-nuevo-proveedor');
const btnCerrar = document.getElementById('btn-cerrar-modal');
const btnCancelar = document.getElementById('btn-cancelar-modal');

// Abrir modal al hacer clic en "Nuevo Proveedor"
btnNuevo.addEventListener('click', () => {
modal.classList.add('activo');
});

// Función para cerrar el modal
const cerrarModal = () => {
modal.classList.remove('activo');
};

btnCerrar.addEventListener('click', cerrarModal);
btnCancelar.addEventListener('click', cerrarModal);

// Cerrar al hacer clic
window.addEventListener('click', (e) => {
if (e.target === modal) {
    cerrarModal();
}
});