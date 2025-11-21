function cambiarOrden(selectElement) {
        // 1. Obtener el valor de ordenación seleccionado (ej. '-id', 'precio_asc')
        const nuevoOrden = selectElement.value;
        
        // 2. Crear un objeto URLSearchParams a partir de la URL actual
        const urlParams = new URLSearchParams(window.location.search);
        
        // 3. Reemplazar o añadir el nuevo parámetro 'orden'
        urlParams.set('orden', nuevoOrden);
        
        // 4. Asegurarse de ir a la primera página después de cambiar la orden (mejor UX)
        if (urlParams.has('page')) {
            urlParams.set('page', '1');
        }

        // 5. Reconstruir la URL y redirigir
        window.location.href = window.location.pathname + '?' + urlParams.toString();
    }