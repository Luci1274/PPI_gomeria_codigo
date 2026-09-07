const botonMenu = document.getElementById("btn-hamburguesa");
const menuLateral = document.getElementById("menu-lateral");
const overlay = document.getElementById("overlay_nav");

// Abrir el menú y ocultar el botón hamburguesa
botonMenu.addEventListener("click", () => {
    menuLateral.classList.add("abierto");
    overlay.classList.add("activo");
    botonMenu.classList.add("oculto");
});

// Cerrar el menú haciendo clic afuera y volver a mostrar el botón
overlay.addEventListener("click", () => {
    menuLateral.classList.remove("abierto");
    overlay.classList.remove("activo");
    botonMenu.classList.remove("oculto");
});