from carrito.models import Carrito
from productos.models import Favorito

def navbar_data(request):
    """
    Injecta datos globales para el navbar (Favoritos y Carrito) en todas las plantillas.
    """
    contexto = {
        'navbar_favs': [],
        'navbar_cart_items': [],
        'navbar_cart_count': 0
    }

    if request.user.is_authenticated:
        # Obtener últimos 5 favoritos
        favs_query = Favorito.objects.filter(usuario=request.user).order_by('-fecha_agregado')[:5]
        contexto['navbar_favs'] = [f.producto for f in favs_query]

        # Obtener datos del carrito
        try:
            carrito = Carrito.objects.get(usuario=request.user)
            contexto['navbar_cart_items'] = carrito.items.all().order_by('-id')[:5]
            contexto['navbar_cart_count'] = carrito.items.count()
        except Carrito.DoesNotExist:
            pass
            
    return contexto