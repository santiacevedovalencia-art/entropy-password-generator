document.addEventListener('DOMContentLoaded', function () {
    try {
        const accepted = localStorage.getItem('privacyAccepted') === '1';
        const overlay = document.getElementById('privacyModalOverlay');
        const acceptBtn = document.getElementById('privacyAcceptBtn');
        const readBtn = document.getElementById('privacyReadBtn');

        function showModal() {
            if (!overlay) return;
            overlay.style.display = 'flex';
            document.body.classList.add('privacy-block');
            // focus accept button for keyboard users
            if (acceptBtn) acceptBtn.focus();
        }

        function hideModal() {
            if (!overlay) return;
            overlay.style.display = 'none';
            document.body.classList.remove('privacy-block');
            // Inform other scripts
            window.dispatchEvent(new CustomEvent('privacyAccepted'));
        }

        if (accepted) {
            // nothing to do
            return;
        }

        // If we don't have modal elements, ensure the user can still accept via link
        if (!overlay || !acceptBtn || !readBtn) {
            // fallback: prompt once
            const ok = confirm('Para usar este sitio debe aceptar la política de privacidad. ¿Desea abrir la política ahora?');
            if (ok) window.open('privacy.html', '_blank');
            return;
        }

        showModal();

        readBtn.addEventListener('click', function (e) {
            e.preventDefault();
            window.open('privacy.html', '_blank');
        });

        acceptBtn.addEventListener('click', function (e) {
            e.preventDefault();
            try {
                localStorage.setItem('privacyAccepted', '1');
            } catch (err) {
                console.warn('No se pudo guardar la preferencia en localStorage.', err);
            }
            hideModal();
        });

        // Allow pressing Enter to accept
        overlay.addEventListener('keydown', function (ev) {
            if (ev.key === 'Enter') {
                ev.preventDefault();
                acceptBtn.click();
            }
        });

    } catch (err) {
        console.error('Error inicializando el consentimiento de privacidad:', err);
    }
});
