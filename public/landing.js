document.addEventListener('DOMContentLoaded', function () {
    const loginBtn = document.querySelector('.login-btn');
    const signupBtn = document.querySelector('.signup-btn');
    const loginModal = document.getElementById('loginModal');
    const signupModal = document.getElementById('signupModal');
    const closeButtons = document.querySelectorAll('.modal .close-modal');
    const switchToSignup = document.getElementById('switchToSignup');
    const switchToLogin = document.getElementById('switchToLogin');

    function openModal(modal) {
        if (modal) {
            modal.style.display = 'block';
        }
    }

    function closeModal(modal) {
        if (modal) {
            modal.style.display = 'none';
        }
    }

    if (loginBtn && loginModal) {
        loginBtn.addEventListener('click', function () {
            openModal(loginModal);
        });
    }

    if (signupBtn && signupModal) {
        signupBtn.addEventListener('click', function () {
            openModal(signupModal);
        });
    }

    closeButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const modal = this.closest('.modal');
            closeModal(modal);
        });
    });

    if (switchToSignup) {
        switchToSignup.addEventListener('click', function (e) {
            e.preventDefault();
            closeModal(loginModal);
            openModal(signupModal);
        });
    }

    if (switchToLogin) {
        switchToLogin.addEventListener('click', function (e) {
            e.preventDefault();
            closeModal(signupModal);
            openModal(loginModal);
        });
    }

    // Cerrar modal haciendo clic fuera del contenido
    window.addEventListener('click', function (event) {
        if (event.target === loginModal) {
            closeModal(loginModal);
        }
        if (event.target === signupModal) {
            closeModal(signupModal);
        }
    });
});

// Funciones del demo del generador
function generateDemoPassword() {
    const demoSection = document.getElementById('demoSection');
    const demoPassword = document.getElementById('demoPassword');
    const demoStatus = document.getElementById('demoStatus');
    const lengthSlider = document.getElementById('demoLength');
    
    // Mostrar la sección demo
    demoSection.style.display = 'block';
    demoPassword.value = 'Generando...';
    demoStatus.textContent = 'Conectando con la cámara...';
    
    const length = lengthSlider.value;
    
    // Llamar a la API
    fetch(`/api/password?length=${length}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                demoPassword.value = 'Error al generar';
                demoStatus.textContent = `Error: ${data.error}`;
                demoStatus.style.color = '#e74c3c';
            } else {
                demoPassword.value = data.password;
                demoStatus.textContent = `Contraseña generada usando ${data.frames_used} frames de cámara`;
                demoStatus.style.color = 'var(--accent-color)';
            }
        })
        .catch(error => {
            demoPassword.value = 'Error de conexión';
            demoStatus.textContent = 'No se pudo conectar con el servidor';
            demoStatus.style.color = '#e74c3c';
            console.error('Error:', error);
        });
}

function updateLength(value) {
    document.getElementById('lengthValue').textContent = value;
}

function copyDemoPassword() {
    const demoPassword = document.getElementById('demoPassword');
    const copyBtn = document.querySelector('.copy-demo-btn');
    
    if (demoPassword.value && demoPassword.value !== 'Generando...' && demoPassword.value !== 'Error al generar') {
        navigator.clipboard.writeText(demoPassword.value).then(() => {
            const originalText = copyBtn.textContent;
            copyBtn.textContent = '✓';
            copyBtn.style.backgroundColor = '#27ae60';
            
            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.style.backgroundColor = 'var(--accent-color)';
            }, 2000);
        }).catch(err => {
            console.error('Error al copiar:', err);
        });
    }
}

function showComingSoon() {
    alert('Esta funcionalidad estará disponible próximamente. Por ahora puedes usar el generador básico.');
}