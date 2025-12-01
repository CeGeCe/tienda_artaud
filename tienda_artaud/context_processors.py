from carrito.models import Carrito
from productos.models import Favorito

def navbar_data(request):
    """
    Inyecta datos globales para el navbar (Favoritos y Carrito) en todas las plantillas.
    """
    contexto = {
        'navbar_favs': [],
        'navbar_favs_count': 0,
        'navbar_cart_items': [],
        'navbar_cart_count': 0
    }

    if request.user.is_authenticated:
        # Obtener número de favoritos
        qs_favoritos = Favorito.objects.filter(usuario=request.user)

        contexto['navbar_favs_count'] = qs_favoritos.count()


        # Obtener datos del carrito
        try:
            carrito = Carrito.objects.get(usuario=request.user)
            contexto['navbar_cart_count'] = carrito.items.count()
        except Carrito.DoesNotExist:
            pass
            
    return contexto