function applyTheme(isDark) {
    const body = document.body;
    const toggleButton = document.getElementById('dark-mode-toggle');

    if (isDark) {
        body.classList.add('dark-mode');
        // Cambia el ícono a la luna si está en modo oscuro
        if (toggleButton) toggleButton.innerHTML = '🌙'; 
    } else {
        body.classList.remove('dark-mode');
        // Cambia el ícono al sol si está en modo claro
        if (toggleButton) toggleButton.innerHTML = '☀️'; 
    }
}

// Función para alternar el modo oscuro (desde el botón)
function toggleDarkMode() {
    const isDark = document.body.classList.contains('dark-mode');
    // Guardamos el nuevo estado en localStorage y lo aplicamos
    localStorage.setItem('theme', isDark ? 'light' : 'dark');
    applyTheme(!isDark);
}

// Inicializar: Comprobar el localStorage al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');

    if (savedTheme === 'dark') {
        applyTheme(true);
    } else if (savedTheme === 'light') {
        applyTheme(false);
    } else {
        // Opción: Detectar la preferencia del sistema operativo
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        applyTheme(prefersDark);
    }
});