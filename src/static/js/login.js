// Esperar a que el HTML termine de cargar en el navegador
document.addEventListener('DOMContentLoaded', () => {
    let timerNotificacion;

    const btnLogin = document.getElementById('btn_pestaña_login');
    const btnRegistro = document.getElementById('btn_pestaña_registro');
    const formLogin = document.getElementById('form_login');
    const formRegistro = document.getElementById('form_registro');
    const tituloDinamico = document.getElementById('titulo_dinamico');
    // Manipulacion de botón ojo
    const btnOjo = document.querySelector('.boton-ojo');
    let ojoCerrado = document.querySelector('.eye');
    const passInput = document.getElementById('password_input');
    // Mensaje de avisos
    const cartelEmergente = document.getElementById('cartel-emergente');
    const cartelMensaje = document.getElementById('cartel-mensaje');
    const cartelTitulo = document.getElementById('cartel-titulo');

    // --- LÓGICA DE RECUPERACIÓN DE CONTRASEÑA ---
    const btnOlvidastePass = document.querySelector('.recuperar_contraseña');
    const modalRecuperar = document.getElementById('modal_recuperar');
    const btnCerrarModal = document.getElementById('btn_cerrar_modal');

    const paso1 = document.getElementById('paso_recuperar_1');
    const paso2 = document.getElementById('paso_recuperar_2');
    const paso3 = document.getElementById('paso_recuperar_3');

    let idUsuarioRecuperacion = null;
    let tokenValidado = null;

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

    function mostrarNotificacion(titulo, mensaje, tiempo = 1000) {
        clearTimeout(timerNotificacion);

        cartelTitulo.textContent = titulo;
        cartelMensaje.textContent = mensaje;
        cartelEmergente.style.display = 'block';

        if (tiempo > 0) {
            timerNotificacion = setTimeout(() => {
                ocultarNotificacion();
            }, tiempo);
        }
    };

    function ocultarNotificacion() {
        cartelEmergente.style.display = 'none';
    }

    

    // Comportamiento para ver la contraseña

    // --- Petición de Iniciar Sesión ---
    formLogin.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (passInput.type === 'text'){
            passInput.type = 'password';
        }

        const payload = {
            txt_input_nombre: document.getElementById('txt_input_nombre').value,
            password_input: document.getElementById('password_input').value,
            checkbox_recordar: document.getElementById('checkbox_recordar').checked
        };

        try {
            const respuesta = await fetch('/api/iniciar_sesion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const datos = await respuesta.json();

            if (datos.exito) {
                mostrarNotificacion('Inicio exitoso', 'Ingresando...', 1500);
                setTimeout(() => {
                    window.location.href = datos.redireccion;
                }, 1000);
            } else {
                mostrarNotificacion('Intente nuevamente', datos.mensaje, 2000);
            }
        } catch (error) {
            mostrarNotificacion('Error', 'Error al conectar con el servidor', 2000);
        }
    });

    // --- Petición de Registro ---
    formRegistro.addEventListener('submit', async (e) => {
        e.preventDefault();

        const password = formRegistro.querySelector('[name="password_registro"]').value;
        const confirmacion = formRegistro.querySelector('[name="password_registro-confirmacion"]').value;

        if (password !== confirmacion) {
            mostrarNotificacion('Error', 'Las contraseñas no coinciden', 2000);
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
                mostrarNotificacion('Registro exitoso', datos.mensaje, 1500);
                setTimeout(() => {
                    window.location.href = datos.redireccion;
                }, 1000);
            } else {
                mostrarNotificacion('Error', datos.mensaje, 1000);
            }
        } catch (error) {
            mostrarNotificacion('Error', 'Error al conectar con el servidor', 1000);
        }
    });

    // Abrir Modal
    btnOlvidastePass.addEventListener('click', (e) => {
        e.preventDefault();
        paso1.style.display = 'block';
        paso2.style.display = 'none';
        paso3.style.display = 'none';
        modalRecuperar.style.display = 'flex';
    });

    // Cerrar Modal
    btnCerrarModal.addEventListener('click', () => {
        modalRecuperar.style.display = 'none';
    });

    // PASO 1: Solicitar Código
    document.getElementById('btn_solicitar_codigo').addEventListener('click', async () => {
        const nombre_usuario = document.getElementById('rec_usuario').value.trim();
        const contacto = document.getElementById('rec_contacto').value.trim();

        if (!nombre_usuario || !contacto) {
            mostrarNotificacion('Error', 'Completa ambos campos', 2000);
            return;
        }

        try {
            const resp = await fetch('/api/recuperar/solicitar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nombre_usuario, contacto })
            });
            const data = await resp.json();

            if (data.exito) {
                idUsuarioRecuperacion = data.id_usuario;
                mostrarNotificacion('Aviso', data.mensaje, 2500);
                paso1.style.display = 'none';
                paso2.style.display = 'block';
            } else {
                mostrarNotificacion('Error', data.mensaje, 2000);
            }
        } catch (error) {
            mostrarNotificacion('Error', 'Error al conectar con el servidor', 2000);
        }
    });

    // PASO 2: Validar Código
    document.getElementById('btn_validar_codigo').addEventListener('click', async () => {
        const token = document.getElementById('rec_token').value.trim();

        if (!token) {
            mostrarNotificacion('Error', 'Ingresa el código', 2000);
            return;
        }

        try {
            const resp = await fetch('/api/recuperar/validar_token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id_usuario: idUsuarioRecuperacion, token })
            });
            const data = await resp.json();

            if (data.exito) {
                tokenValidado = token;
                mostrarNotificacion('Éxito', data.mensaje, 1500);
                paso2.style.display = 'none';
                paso3.style.display = 'block';
            } else {
                mostrarNotificacion('Error', data.mensaje, 2000);
            }
        } catch (error) {
            mostrarNotificacion('Error', 'Error al conectar con el servidor', 2000);
        }
    });

    // PASO 3: Cambiar Contraseña
    document.getElementById('btn_cambiar_pass').addEventListener('click', async () => {
        const nueva_contrasena = document.getElementById('rec_nueva_pass').value;
        const confirmacion = document.getElementById('rec_confirmar_pass').value;

        if (!nueva_contrasena || nueva_contrasena !== confirmacion) {
            mostrarNotificacion('Error', 'Las contraseñas no coinciden', 2000);
            return;
        }

        try {
            const resp = await fetch('/api/recuperar/restablecer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id_usuario: idUsuarioRecuperacion,
                    token: tokenValidado,
                    nueva_contrasena
                })
            });
            const data = await resp.json();

            if (data.exito) {
                mostrarNotificacion('Éxito', data.mensaje, 2000);
                modalRecuperar.style.display = 'none';
            } else {
                mostrarNotificacion('Error', data.mensaje, 2000);
            }
        } catch (error) {
            mostrarNotificacion('Error', 'Error al conectar con el servidor', 2000);
        }
    });
    
});
