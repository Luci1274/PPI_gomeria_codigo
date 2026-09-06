// Esperar a que el HTML termine de cargar en el navegador
document.addEventListener('DOMContentLoaded', () => {
    const btnLogin = document.getElementById('btn_pestaña_login');
    const btnRegistro = document.getElementById('btn_pestaña_registro');
    const formLogin = document.getElementById('form_login');
    const formRegistro = document.getElementById('form_registro');
    const tituloDinamico = document.getElementById('titulo_dinamico');

    // Comportamiento al hacer clic en "Crear usuario"
    btnRegistro.addEventListener('click', (e) => {
        e.preventDefault();
        btnRegistro.classList.add('pestana-activa');
        btnLogin.classList.remove('pestana-activa');
        formLogin.classList.add('formulario-oculto');
        formRegistro.classList.remove('formulario-oculto');
        tituloDinamico.textContent = 'Nuevo Usuario';
    });

    // Comportamiento al hacer clic en "Iniciar sesión"
    btnLogin.addEventListener('click', (e) => {
        e.preventDefault();
        btnLogin.classList.add('pestana-activa');
        btnRegistro.classList.remove('pestana-activa');
        formRegistro.classList.add('formulario-oculto');
        formLogin.classList.remove('formulario-oculto');
        tituloDinamico.textContent = '¡Bienvenido!';
    });
});
