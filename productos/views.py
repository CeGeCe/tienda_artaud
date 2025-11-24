from django.shortcuts import render, get_object_or_404
from django.db.models import Q # Búsquedas OR
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView # CRUD
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin # Proteger las vistas
from .models import Producto, FORMATO_CHOICES, CONDICION_CHOICES, EDICION_CHOICES, GENERO_1_CHOICES
from .forms import ProductoForm
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, Http404

# Create your views here.


def home(request):
    """Muestra la página de inicio con una selección de productos."""
    # Muestra los 12 más recientes (y aprobados) en Carrusel ('ID' como proxy de recientes)
    productos_destacados = Producto.objects.filter(
        aprobado=True,
        stock__gt=0, # Productos con stock > 0
        ).order_by('-id')[:12]

    contexto = {
        'productos': productos_destacados,
        'titulo_pagina': 'Tienda Artaud | Inicio',
    }

    # Renderizar
    return render(request, 'home.html', contexto)


def about(request):
    # render = busca la plantilla en la carpeta templates de la app
    return render(request, 'about.html', {})


@login_required # Pide autenticación
def mis_productos(request):
    """Muestra solo los productos publicados por el usuario logueado."""
    
    # Filtra los productos para que solo muestren los del usuario actual
    productos_del_vendedor = Producto.objects.filter(vendedor=request.user).order_by('-id') 
    
    # Paginación igual a la de la página Catálogo
    paginator = Paginator(productos_del_vendedor, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    contexto = {
        'page_obj': page_obj, 
        'productos': page_obj.object_list, 
        'titulo_pagina': f'Mi Panel de Vendedor : {request.user.username}',
    }
    
    return render(request, 'productos/mis_productos.html', contexto)


def is_valid_filter(filter_list):
    """Devuelve True si la lista no es vacía y contiene al menos un valor no vacío."""
    # Devuelve True si la lista no es None, si no está vacía, y si al menos un elemento no es una cadena vacía.
    return bool(filter_list) and any(f for f in filter_list if f)


def catalogo(request):
    """Catálogo completo, búsqueda y filtros"""

    #Obtener SOLO productos aprobados
    productos = Producto.objects.filter(
        aprobado=True,
        stock__gt=0,
        )

    query = request.GET.get('q') # Búsqueda por texto

    if query:
        # Búsqueda en varios campos con el operador Q para combinar con OR
        productos = productos.filter(
            Q(artista__icontains=query) |
            Q(album__icontains=query) |
            Q(codigo_barras__icontains=query) |
            Q(sello__icontains=query) |
            Q(pais__icontains=query) |
            Q(genero_1__icontains=query) |
            Q(genero_2__icontains=query) 
        ).distinct() # distinct() evitar duplicados si un producto coincide varias veces

    # Filtros de BÚSQUEDA
    formato_filtro = request.GET.getlist('formato')
    condicion_filtro = request.GET.getlist('condicion')
    edicion_filtro = request.GET.getlist('edicion')
    genero_filtro = request.GET.getlist('genero')

    if is_valid_filter(formato_filtro):
        productos = productos.filter(formato__in=formato_filtro)
        
    if is_valid_filter(condicion_filtro):
        productos = productos.filter(condicion__in=condicion_filtro)
        
    if is_valid_filter(edicion_filtro):
        productos = productos.filter(edicion__in=edicion_filtro)

    if is_valid_filter(genero_filtro):
        productos = productos.filter(genero_1__in=genero_filtro)

    # ORDEN / SORT
    # Por defecto, los más nuevos (descendente por ID)
    orden = request.GET.get('orden', '-id')

    vista = request.GET.get('vista', 'cuadricula') # Default: cuadricula
    
    if orden == 'precio':
        productos = productos.order_by('precio')
    elif orden == '-precio':
        productos = productos.order_by('-precio')
    elif orden == '-id': # Más Nuevos (Publicación más reciente)
        productos = productos.order_by('-id')
    elif orden == 'id': # Más Viejos (Publicación más antigua)
        productos = productos.order_by('id')
    elif orden == 'artista': #
        productos = productos.order_by('artista', 'album')    
    else:
        # Si el usuario no especificó orden, se usa el valor por defecto: los más nuevos
        productos = productos.order_by('-id')

    # Mostrar x productos p/ página
    por_pagina = request.GET.get('por_pagina', 12)

    try:
        por_pagina = int(por_pagina)
        if por_pagina not in [12, 24, 36]:
            por_pagina = 12
    except ValueError:
        por_pagina = 12

    # Para que no desaparezca el ordenamiento elegido
    productos_list = productos

    # Paginación (obtiene número de página)
    paginator = Paginator(productos_list, por_pagina) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    # Diccionario de contexto para la plantilla
    contexto = {
        'page_obj': page_obj,
        'productos': page_obj.object_list, #Los productos de la página actual
        'titulo_pagina': 'Catálogo de la Tienda',
        'query_actual': query,
        'orden_actual': orden, # Pasa el valor exacto usado por Django ('-id', 'id', 'precio_asc', etc.)
        'vista_actual': vista,
        'por_pagina_actual': por_pagina,
        
        # Opciones para el filtro lateral
        'formato_choices': FORMATO_CHOICES,
        'condicion_choices': CONDICION_CHOICES,
        'edicion_choices': EDICION_CHOICES,
        'genero_choices': GENERO_1_CHOICES,
        
        # Filtros seleccionados actualmente (para mantener el estado en la interfaz)
        'formato_seleccionado': formato_filtro,
        'condicion_seleccionada': condicion_filtro,
        'edicion_seleccionada': edicion_filtro,
        'genero_seleccionado': genero_filtro,


        'opciones_orden': [
            ('-id', 'Más Recientes'),
            ('id', 'Más Antiguos'),
            ('precio', 'Precio (Menor a Mayor)'),
            ('-precio', 'Precio (Mayor a Menor)'),
            ('artista', 'Artista (A-Z)'),
        ],
            
        'opciones_por_pagina': [12, 24, 36],
    }
    
    return render(request, 'productos/catalogo.html', contexto)


def detalle_producto(request, pk):
    """Muestra todos los detalles de un producto individual."""
    # get_object_or_404 = Devuelve una página de NO ENCONTRADO si coso
    producto = get_object_or_404(Producto, pk=pk)

    contexto = {
        'producto': producto,
        'titulo_pagina': f'{producto.artista} - {producto.album}',
    }

    # SEGURIDAD / MODERACIÓN
    if not producto.aprobado:
        # Si el usuario NO es el vendedor ni es admin
        if request.user != producto.vendedor and not request.user.is_staff:
            # Da error 404, no "Prohibido" porque no revela que el producto existe
            raise Http404("Este producto no está disponible o no existe.")

    # Renderizar
    return render(request, 'productos/detalle_producto.html', contexto)


# CREAR un Producto
class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('mis_productos') # Redirige al panel del vendedor
    
    def form_valid(self, form):
        # Asignar el usuario actual como vendedor
        form.instance.vendedor = self.request.user 
        
        # AUTO-APROBACIÓN PARA admin
        if self.request.user.is_superuser or self.request.user.is_staff:
            form.instance.aprobado = True
        else:
            form.instance.aprobado = False
            
        return super().form_valid(form)


# EDITAR un Producto
class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('mis_productos')
    
    # Asegurarse de que solo el vendedor pueda editar su producto
    def get_queryset(self):
        # Filtra el queryset para que solo muestre los productos del usuario actual
        return self.model.objects.filter(vendedor=self.request.user)


# ELIMINAR un Producto
class ProductoDeleteView(LoginRequiredMixin, DeleteView):
    model = Producto
    template_name = 'productos/producto_confirm_delete.html' 
    success_url = reverse_lazy('mis_productos') # Redirige al panel después de eliminar
    
    # Seguridad: Aseguramos que solo el vendedor pueda eliminar su producto
    def get_queryset(self):
        # Filtra el queryset para que solo muestre los productos del usuario actual
        return self.model.objects.filter(vendedor=self.request.user)


@login_required
@require_POST # Asegura que la vista solo acepte peticiones POST
def toggle_favorito(request, producto_id):
    """
    Añade o quita un producto de la lista de favoritos del usuario.
    """
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Usa la lista de favoritos
    if producto.favoritos.filter(id=request.user.id).exists():
        # Si el producto ya está en favoritos, se quita
        producto.favoritos.remove(request.user)
    else:
        # Si no está en favoritos, se agrega
        producto.favoritos.add(request.user)
        
    # Redirige al usuario a la página de donde vino
    # (Catálogo || Detalle)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('home')))


@login_required
def ver_favoritos(request):
    """ Muestra una página con todos los productos marcados como Favoritos """
    productos_favoritos = request.user.productos_favoritos.all()
    
    contexto = {
        'productos': productos_favoritos,
        'titulo_pagina': 'Mis Favoritos ❤️'
    }
    
    return render(request, 'productos/favoritos.html', contexto)