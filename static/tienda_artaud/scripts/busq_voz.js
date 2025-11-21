document.addEventListener('DOMContentLoaded', () => {
    // Verificar compatibilidad del navegador
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        console.warn("Búsqueda por voz no soportada en este navegador.");
        // Opcional: Ocultar el botón si no es compatible
        const voiceButton = document.getElementById('voice-search-button');
        if(voiceButton) voiceButton.style.display = 'none';
        return;
    }

    // Obtener referencias a los elementos
    const voiceButton = document.getElementById('voice-search-button');
    const searchInput = document.querySelector('.search-input'); // Usamos la clase del input

    // Crear la instancia de reconocimiento
    const recognition = new SpeechRecognition();
    recognition.lang = 'es-AR'; // ¡Importante! Configurar el idioma (Español Argentina)
    recognition.interimResults = false; // No queremos resultados parciales
    recognition.maxAlternatives = 1; // Solo la mejor transcripción

    // Configurar el clic del botón
    voiceButton.addEventListener('click', () => {
        try {
            recognition.start();
            voiceButton.innerHTML = '🎧'; // Cambia el ícono a "Escuchando"
            voiceButton.classList.add('listening');
        } catch(e) {
            console.error("Error al iniciar el reconocimiento de voz:", e);
            alert("No se pudo iniciar el reconocimiento de voz. ¿Ya diste permiso?");
        }
    });

    // Cuando el reconocimiento termina
    recognition.onend = () => {
        voiceButton.innerHTML = '🎤'; // Vuelve al ícono original
        voiceButton.classList.remove('listening');
    };

    // Cuando se obtiene un resultado (la transcripción)
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;

        // Pone el texto transcripto en la barra de búsqueda
        searchInput.value = transcript;

        // Opcional: Enviar el formulario automáticamente
        // searchInput.form.submit();
    };

    // Manejo de errores
    recognition.onerror = (event) => {
        if (event.error === 'no-speech') {
            alert("No se detectó voz. Intentá otra vez.");
        } else if (event.error === 'audio-capture') {
            alert("Error al capturar el audio. ¿El micrófono funciona?");
        } else if (event.error === 'not-allowed') {
            alert("Permiso denegado para el micrófono. Habilitalo en la configuración del navegador.");
        }
    };

});