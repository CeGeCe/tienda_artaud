document.addEventListener('DOMContentLoaded', () => {
    const productImage = document.getElementById('detalle-main-image');
    const zoomButton = document.getElementById('zoom-button');
    const modal = document.getElementById('image-zoom-modal');
    const modalImage = document.getElementById('modal-zoomed-image');
    const closeButton = document.querySelector('.close-button');

    if (productImage && zoomButton && modal && modalImage && closeButton) {

        // Abrir el modal al hacer clic en la imagen o en el botón de zoom
        [productImage, zoomButton].forEach(element => {
            element.addEventListener('click', () => {
                modal.style.display = 'flex';
                modalImage.src = productImage.src; // Carga la imagen original en el modal
            });
        });

        // Cerrar el modal al hacer clic en la 'x'
        closeButton.addEventListener('click', () => {
            modal.style.display = 'none';
        });

        // Cerrar el modal al hacer clic fuera de la imagen
        window.addEventListener('click', (event) => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
});