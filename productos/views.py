from django.shortcuts import render
from .models import Producto

# Create your views here.


def home(request):
    """Muestra la página de inicio con una selección de productos."""
    # Recuperamos los 6 productos más recientes (usando el ID como proxy de reciente)
    productos_destacados = Producto.objects.all().order_by('-id')[:6]

    contexto = {
        'productos': productos_destacados,
        'titulo_pagina': 'Tienda Artaud | Inicio',
    }

    # Renderizamos la nueva plantilla 'home.html'
    return render(request, 'productos/home.html', contexto)


def catalogo(request):
    """Recupera y muestra una lista de todos los productos disponibles."""
    # objects.all() trae todos los registros de la tabla Producto.
    productos = Producto.objects.all().order_by('artista', 'album')

    # Crear un diccionario (contexto) para pasar los datos a la plantilla
    contexto = {
        'productos': productos,
        'titulo_pagina': 'Catálogo Completo',
    }

    # Renderiza la plantilla con los datos.
    return render(request, 'productos/catalogo.html', contexto)


def acerca_de(request):
    """Muestra la página de información sobre el sitio (About)."""
    # render = busca la plantilla en la carpeta templates de la app
    return render(request, 'productos/acerca_de.html', {})
