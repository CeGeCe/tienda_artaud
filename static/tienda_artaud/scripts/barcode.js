document.addEventListener('DOMContentLoaded', () => {
    
    const scannerModal = document.getElementById('scanner-modal');
    const closeBtn = document.querySelector('.close-scanner');
    const btnNavbar = document.getElementById('barcode-search-btn');
    let html5QrcodeScanner = null;

    // --- 1. FUNCIÓN DE CIERRE FORZADO (INFALIBLE) ---
    function forceCloseModal() {
        // 1. Ocultar visualmente de inmediato
        if (scannerModal) {
            scannerModal.style.display = 'none';
        }

        // 2. Intentar limpiar la cámara en segundo plano (si estaba prendida)
        if (html5QrcodeScanner) {
            try {
                html5QrcodeScanner.stop().then(() => {
                    html5QrcodeScanner.clear();
                }).catch(err => {
                    // Si falla al detenerse (porque nunca arrancó), no importa.
                    console.warn("Aviso: El escáner no estaba activo.", err);
                    html5QrcodeScanner.clear();
                });
            } catch (e) {
                console.log("Error limpiando scanner:", e);
            }
        }
    }

    // --- 2. ASIGNAR EL CLIC A LA CRUZ ---
    if (closeBtn) {
        closeBtn.onclick = function(e) {
            e.preventDefault();
            console.log("Cerrando modal...");
            forceCloseModal(); // Llamamos a la función que cierra sí o sí
        };
    }

    // Cerrar clicando afuera
    if (scannerModal) {
        scannerModal.addEventListener('click', (event) => {
            if (event.target === scannerModal) {
                forceCloseModal();
            }
        });
    }

    // --- 3. INICIAR ESCÁNER ---
    function startScanner(callback) {
        if (!scannerModal) return;
        scannerModal.style.display = 'flex';

        // Si no hay div 'reader', salimos
        if (!document.getElementById('reader')) return;

        html5QrcodeScanner = new Html5Qrcode("reader");
        
        const config = { fps: 10, qrbox: { width: 250, height: 250 } };
        
        html5QrcodeScanner.start({ facingMode: "environment" }, config, 
            (decodedText, decodedResult) => {
                // ÉXITO
                console.log(`Código: ${decodedText}`);
                forceCloseModal();
                callback(decodedText); 
            },
            (errorMessage) => {
                // Error de lectura continuo (normal)
            }
        ).catch(err => {
            // ERROR CRÍTICO (Ej: No hay cámara)
            console.error("No se pudo iniciar la cámara:", err);
            
            // Mostramos mensaje de error en el modal
            const readerDiv = document.getElementById('reader');
            readerDiv.innerHTML = `<p style="color: red; padding: 20px; font-weight: bold;">
                                    ⚠️ No se detectó ninguna cámara.<br>
                                    <small>Verifica tu dispositivo.</small>
                                   </p>`;
            
            // NO cerramos automático para que leas el error, 
            // pero la X funcionará gracias a forceCloseModal()
        });
    }

    // --- 4. EVENTOS DE LOS BOTONES DE APERTURA ---
    
    // Navbar
    if (btnNavbar) {
        btnNavbar.addEventListener('click', (e) => {
            e.preventDefault();
            startScanner((codigo) => {
                window.location.href = `/catalogo/?q=${codigo}`;
            });
        });
    }

    // Formulario (Función Global)
    window.iniciarEscaneoFormulario = function(inputField) {
        startScanner((codigo) => {
            inputField.value = codigo;
            inputField.style.backgroundColor = "#d4edda";
        });
    };
});