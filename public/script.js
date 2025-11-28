document.addEventListener('DOMContentLoaded', function() {
    // Length input functionality
    const lengthInput = document.getElementById('length');
    const lengthError = document.getElementById('length-error');
    
    lengthInput.addEventListener('input', function() {
        validateLength();
    });
    
    function validateLength() {
        const value = parseInt(lengthInput.value, 10);
        
        if (isNaN(value) || lengthInput.value === '') {
            lengthError.textContent = 'Por favor, ingrese un número válido';
            lengthError.style.display = 'block';
            return false;
        } else if (value < 4) {
            lengthError.textContent = 'La contraseña debe tener al menos 4 caracteres';
            lengthError.style.display = 'block';
            return false;
        } else if (value > 30) {
            lengthError.textContent = 'La contraseña no puede ser tan larga (máximo 30 caracteres)';
            lengthError.style.display = 'block';
            return false;
        } else {
            lengthError.style.display = 'none';
            return true;
        }
    }
    
    // Copy button functionality (conectado al backend Python vía Flask)
const copyBtn = document.querySelector('.copy-btn');
const passwordOutput = document.getElementById('password-output');

if (copyBtn) {
    copyBtn.addEventListener('click', async function () {
        if (!validateLength()) {
            alert('Por favor, corrija el valor de la longitud antes de generar la contraseña');
            return;
        }
        const length = parseInt(lengthInput.value, 10);

        // Mostrar mensaje de carga
        const originalBtnText = copyBtn.textContent;
        copyBtn.textContent = 'Generando...';
        copyBtn.disabled = true;
        copyBtn.style.opacity = '0.7';
        copyBtn.style.cursor = 'not-allowed';
        
        if (passwordOutput) {
            passwordOutput.value = 'Capturando desde la cámara...';
            passwordOutput.style.color = '#f39c12';
        }

        try {
            // Llamada al backend Flask
            const response = await fetch(`/api/password?length=${length}`);

            if (!response.ok) {
                let msg = 'Error en el servidor';
                try {
                    const errData = await response.json();
                    if (errData && errData.error) {
                        msg = errData.error;
                    }
                } catch (e) {
                    // ignorar error al parsear JSON
                }
                
                // Restaurar estado del botón
                copyBtn.textContent = originalBtnText;
                copyBtn.disabled = false;
                copyBtn.style.opacity = '1';
                copyBtn.style.cursor = 'pointer';
                
                if (passwordOutput) {
                    passwordOutput.value = '';
                    passwordOutput.style.color = '';
                }
                
                alert('No se pudo generar la contraseña: ' + msg);
                return;
            }

            const data = await response.json();
            const password = data.password;

            // Mostrar la contraseña en el input
            if (passwordOutput) {
                passwordOutput.value = password;
                passwordOutput.style.color = '';
            }

            // Copiar al portapapeles si está disponible
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(password);
            }

            // Feedback visual en el botón
            copyBtn.textContent = 'Copiado!';
            copyBtn.style.backgroundColor = '#27ae60';
            copyBtn.disabled = false;
            copyBtn.style.opacity = '1';
            copyBtn.style.cursor = 'pointer';

            setTimeout(() => {
                copyBtn.textContent = originalBtnText;
                copyBtn.style.backgroundColor = '';
            }, 2000);
        } catch (error) {
            console.error('Error al generar/copiar la contraseña:', error);
            
            // Restaurar estado del botón en caso de error
            copyBtn.textContent = originalBtnText;
            copyBtn.disabled = false;
            copyBtn.style.opacity = '1';
            copyBtn.style.cursor = 'pointer';
            
            if (passwordOutput) {
                passwordOutput.value = '';
                passwordOutput.style.color = '';
            }
            
            alert('Error inesperado al generar la contraseña. Revisa la consola del navegador.');
        }
    });
}


    
    // Navigation tabs functionality
    const navItems = document.querySelectorAll('nav ul li');
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            // Solo actualiza la clase activa si no es un enlace a otra página
            const link = this.querySelector('a');
            if (link && !link.getAttribute('href').includes('index.html')) {
                navItems.forEach(i => i.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });
    

});