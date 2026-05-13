const botonMenu = document.getElementById("boton_menu");

const barraNavegacion = document.getElementById("barra_navegacion");

const overlay = document.getElementById("overlay_nav");


botonMenu.addEventListener("click", () => {

    barraNavegacion.classList.toggle("abierto");

    overlay.classList.toggle("activo");

});



overlay.addEventListener("click", () => {

    barraNavegacion.classList.remove("abierto");

    overlay.classList.remove("activo");

});