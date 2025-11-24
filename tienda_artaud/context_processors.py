from carrito.models import Carrito

def navbar_data(request):
    """
    Injecta datos globales para el navbar (Favoritos y Carrito)
    en todas las plantillas.
    """
    context = {
        'navbar_favs': [],
        'navbar_cart_items': [],
        'navbar_cart_count': 0
    }

    if request.user.is_authenticated:
        # Obtener últimos 5 favoritos
        context['navbar_favs'] = request.user.productos_favoritos.all().order_by('-id')[:5]

        # Obtener datos del carrito
        try:
            carrito = Carrito.objects.get(usuario=request.user)
            context['navbar_cart_items'] = carrito.items.all().order_by('-id')[:5]
            context['navbar_cart_count'] = carrito.items.count()
        except Carrito.DoesNotExist:
            pass
            
    return context