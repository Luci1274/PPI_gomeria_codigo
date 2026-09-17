// Esperar a que el HTML termine de cargar en el navegador
document.addEventListener('DOMContentLoaded', () => {
    const btnLogin = document.getElementById('btn_pestaña_login');
    const btnRegistro = document.getElementById('btn_pestaña_registro');
    const formLogin = document.getElementById('form_login');
    const formRegistro = document.getElementById('form_registro');
    const tituloDinamico = document.getElementById('titulo_dinamico');
    // Manipulacion de botón ojo
    const btnOjo = document.querySelector('.boton-ojo');
    let ojoCerrado = document.querySelector('.eye');
    const passInput = document.getElementById('password_input');

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

    // Mostrar y ocultar la contraseña en le Iniciar sesión
    btnOjo.addEventListener('click', (e) => {
        e.preventDefault();
        
        ojoCerrado.classList.toggle('fa-eye');
        ojoCerrado.classList.toggle('fa-eye-slash');

        if (passInput.type === 'password') {
            passInput.type = 'text';
        } else {
            passInput.type = "password";
        }
    });

    

    // Comportamiento para ver la contraseña

    // --- Petición de Iniciar Sesión ---
    formLogin.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (passInput.type === 'text'){
            passInput.type = 'password';
        }

        const payload = {
            txt_input_nombre: document.getElementById('txt_input_nombre').value,
            password_input: document.getElementById('password_input').value
        };

        try {
            const respuesta = await fetch('/api/iniciar_sesion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const datos = await respuesta.json();

            if (datos.exito) {
                window.location.href = datos.redireccion;
            } else {
                cajaMensaje.style.display = "block";
                cajaMensaje.style.color = "red";
                parrafoMensaje.innerText = datos.mensaje;
            }
        } catch (error) {
            cajaMensaje.style.display = "block";
                cajaMensaje.style.color = "red";
                parrafoMensaje.innerText = "Error al conectar con el servidor";
        }
    });

    // --- Petición de Registro ---
    formRegistro.addEventListener('submit', async (e) => {
        e.preventDefault();

        const password = formRegistro.querySelector('[name="password_registro"]').value;
        const confirmacion = formRegistro.querySelector('[name="password_registro-confirmacion"]').value;

        if (password !== confirmacion) {
        cajaMensaje.style.display = "block";
            cajaMensaje.style.color = "red";
            parrafoMensaje.innerText = "Las constraseñas no coinciden";
            return;
        }

        const payload = {
            input_nombre: formRegistro.querySelector('[name="input_nombre"]').value,
            txt_registro_email: formRegistro.querySelector('[name="txt_registro_email"]').value,
            tel_input: formRegistro.querySelector('[name="tel_input"]').value,
            password_registro: password
        };

        try {
            const respuesta = await fetch('/api/registrarse', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const datos = await respuesta.json();

            if (datos.exito) {
                alert(datos.mensaje);
                window.location.href = datos.redireccion;
            } else {
                cajaMensaje.style.display = "block";
                cajaMensaje.style.color = "red";
                parrafoMensaje.innerText = datos.mensaje;
            }
        } catch (error) {
            cajaMensaje.style.display = "block";
            cajaMensaje.style.color = "red";
            parrafoMensaje.innerText = "Error al conectar con el servidor";
        }
    });
    
});
