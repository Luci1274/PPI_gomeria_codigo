const botonMenu = document.getElementById("boton_menu");

const barraNavegacion = document.getElementById("barra_navegacion");

const overlay = document.getElementById("overlay_nav");


botonMenu.addEventListener("click", () => {

    barraNavegacion.classList.toggle("abierto");

    overlay.classList.toggle("activo");

    botonMenu.classList.toggle("oculto_menu");

});



overlay.addEventListener("click", () => {

    barraNavegacion.classList.remove("abierto");

    overlay.classList.remove("activo");

    botonMenu.classList.remove("oculto_menu");

});