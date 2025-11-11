from django.shortcuts import render, get_object_or_404
from django.db.models import Q # Búsquedas OR
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView # CRUD
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin # Proteger las vistas
from .models import Producto, FORMATO_CHOICES, CONDICION_CHOICES, EDICION_CHOICES, GENERO_1_CHOICES #Se importa choices
from .forms import ProductoForm

# Create your views here.


def home(request):
    """Muestra la página de inicio con una selección de productos."""
    # Recuperamos los 6 productos más recientes (usando el ID como proxy de reciente)
    productos_destacados = Producto.objects.all().order_by('-id')[:6]

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


def catalogo(request):
    """Catálogo completo, búsqueda y filtros"""

    #Obtener todos los productos y el Query
    productos = Producto.objects.all()
    query = request.GET.get('q') # Búsqueda por texto

    if query:
        # Búsqueda en múltiples campos usando el operador Q para combinar con OR
        productos = productos.filter(
            Q(artista__icontains=query) |
            Q(album__icontains=query) |
            Q(codigo_barras__icontains=query) |
            Q(sello__icontains=query) |
            Q(genero_1__icontains=query) |
            Q(genero_2__icontains=query) 
        ).distinct() # distinct() evitar duplicados si un producto coincide varias veces
    

    # Filtros de BÚSQUEDA

    formato_filtro = request.GET.get('formato')
    if formato_filtro:
        productos = productos.filter(formato=formato_filtro)

    condicion_filtro = request.GET.get('condicion')
    if condicion_filtro:
        productos = productos.filter(condicion=condicion_filtro)

    edicion_filtro = request.GET.get('edicion')
    if edicion_filtro:
        productos = productos.filter(edicion=edicion_filtro)

    genero_filtro = request.GET.get('genero')
    if genero_filtro:
        productos = productos.filter(genero_1=genero_filtro)

    # ORDEN / SORT
    
    orden = request.GET.get('orden', 'artista') # Orden por defecto es x ARTISTA
    if orden == 'precio_asc':
        productos = productos.order_by('precio')
    elif orden == 'precio_desc':
        productos = productos.order_by('-precio')
    # Si no es precio se mantiene el orden por artista/título o el inicial
    else: 
        productos = productos.order_by('artista', 'album')

    paginator = Paginator(productos, 12)  # Mostrar 12 productos por página

    # Obtener el número de página de la URL, si no está, usa la página 1
    page_number = request.GET.get('page')
    
    # Obtener el objeto de página
    page_obj = paginator.get_page(page_number)


    # Diccionario de contexto para la plantilla
    contexto = {
        'page_obj': page_obj,
        'productos': page_obj.object_list, #Los productos de la página actual
        'titulo_pagina': 'Catálogo Completo y Resultados de Búsqueda',
        'query_actual': query,
        'orden_actual': orden,
        
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

    # Renderizar
    return render(request, 'productos/detalle_producto.html', contexto)


# CREAR un Producto
class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('mis_productos') # Redirige al panel del vendedor
    
    # Sobrescribir el método para asignar el usuario logueado como vendedor
    def form_valid(self, form):
        form.instance.vendedor = self.request.user # Asigna el usuario actual
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