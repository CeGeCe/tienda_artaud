document.addEventListener('DOMContentLoaded', () => {
    const carousel = document.getElementById('product-carousel');
    
    // 1. Verificar si el carrusel existe
    if (!carousel) return; 

    // --- VARIABLES DE ALCANCE GLOBAL ---
    // ⚠️ CAMBIO SOLICITADO: 5000 milisegundos (5 segundos)
    const autoScrollTime = 5000; 
    let autoplayInterval;
    const itemsPerView = 4; // 4 productos por vista
    
    const prevBtn = document.querySelector('.carousel-nav-btn.prev');
    const nextBtn = document.querySelector('.carousel-nav-btn.next');

    // 2. Cálculo del ancho
    const firstCard = carousel.querySelector('.carousel-item-card');
    // Usamos 20px de gap. 
    const itemWidthWithGap = firstCard ? (firstCard.offsetWidth + 20) : 0; 
    
    if (!firstCard) return;


    // -----------------------------------------------------------------
    // A) FUNCIONES DE CONTROL DE AUTOPLAY 
    // -----------------------------------------------------------------
    function stopAutoplay() {
        clearInterval(autoplayInterval);
    }

    function startAutoplay() {
        stopAutoplay(); 
        autoplayInterval = setInterval(() => {
            scrollCarousel(1); // Mover hacia la derecha
        }, autoScrollTime);
    }
    
    // -----------------------------------------------------------------
    // B) FUNCIÓN PRINCIPAL DE SCROLL (CÍCLICO CORREGIDO)
    // -----------------------------------------------------------------
    function scrollCarousel(direction) {
        const currentScroll = carousel.scrollLeft;
        const viewWidth = itemWidthWithGap * itemsPerView;
        const maxScroll = carousel.scrollWidth - carousel.clientWidth;

        let targetScroll;

        if (direction === 1) { // Siguiente (Derecha)
            targetScroll = currentScroll + viewWidth;

            if (targetScroll >= maxScroll) {
                // ⚠️ CORRECCIÓN CLAVE: Solo hacemos el salto instantáneo (auto) a 0.
                // El temporizador (setInterval) esperará 5 segundos en esta posición
                // antes de hacer el scroll suave a la Página 2.
                carousel.scrollTo({ left: 0, behavior: 'auto' });
                return; 
            }
        } else { // Anterior (Izquierda)
            targetScroll = currentScroll - viewWidth;

            if (targetScroll < 0) {
                // Al presionar atrás desde la Página 1, hacemos el salto instantáneo (auto) al final.
                carousel.scrollTo({ left: maxScroll, behavior: 'auto' });
                return;
            }
        }

        // Scroll normal (aplicado solo si no hay salto cíclico)
        carousel.scrollTo({
            left: targetScroll,
            behavior: 'smooth'
        });
    }


    // -----------------------------------------------------------------
    // C) INICIALIZACIÓN Y EVENTOS
    // -----------------------------------------------------------------
    
    // 1. Asignar funciones a los botones de flecha
    if (prevBtn) prevBtn.onclick = () => {
        stopAutoplay(); // Detener al hacer clic
        scrollCarousel(-1);
        startAutoplay(); // Reanudar
    };
    if (nextBtn) nextBtn.onclick = () => {
        stopAutoplay(); // Detener al hacer clic
        scrollCarousel(1);
        startAutoplay(); // Reanudar
    };

    // 2. Control de Autoplay al pasar el mouse
    carousel.addEventListener('mouseover', stopAutoplay);
    carousel.addEventListener('mouseleave', startAutoplay);
    
    // 3. Iniciar el carrusel automáticamente
    startAutoplay();
});