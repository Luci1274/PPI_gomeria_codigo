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

// Agregar enlace activo a la pantalla en la que nos encontramos
document.addEventListener("DOMContentLoaded", () => {
    const rutaActual = window.location.pathname; 
    const enlaces = document.querySelectorAll(".menu-navegacion .enl-nav");

enlaces.forEach(enlace => {
        enlace.classList.remove("activo");
        const href = enlace.getAttribute("href");

        if(href && href !== "#" && (rutaActual === href || (href !== "/" && rutaActual.startsWith(href)))) {
        enlace.classList.add("activo");
        }
    });
});
