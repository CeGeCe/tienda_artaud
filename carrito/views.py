from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Carrito, ItemCarrito
from productos.models import Producto

# Create your views here.

@login_required
def ver_carrito(request):
    """Muestra el carrito del usuario, o crea uno si no existe."""
    try:
        # Intenta obtener el carrito del usuario logueado
        carrito = Carrito.objects.get(usuario=request.user)
    except Carrito.DoesNotExist:
        # Si el usuario no tiene carrito, lo crea
        carrito = Carrito.objects.create(usuario=request.user)
    
    # Renderiza la plantilla, pasando el carrito y sus ítems
    return render(request, 'carrito/carrito_detalle.html', {'carrito': carrito})


@require_POST  # Solo permite el método POST para esta acción
@login_required
def agregar_a_carrito(request, producto_id):
    """Agrega un producto específico al carrito del usuario."""
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    # RESTRICCIÓN: Evitar que el vendedor compre un producto propio
    if producto.vendedor == request.user:
        messages.error(request, f'No podés añadir este artículo al carrito: ¡ES TUYO!')
        return redirect('detalle_producto', pk=producto_id)

    # Obtener o crear el carrito del usuario
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    
    cantidad_a_añadir = 1

    # Intentar obtener el ítem si ya existe en el carrito
    try:
        item = ItemCarrito.objects.get(carrito=carrito, producto=producto)
        nueva_cantidad = item.cantidad + cantidad_a_añadir
        
        # VERIFICACIÓN DE STOCK (EXISTENTE + NUEVA CANTIDAD)
        if nueva_cantidad > producto.stock:
            messages.error(request, f'No hay suficiente stock. Solo quedan {producto.stock} unidades.')
            return redirect('detalle_producto', pk=producto_id)
        # SI HAY STOCK, incrementa la cantidad
        item.cantidad = nueva_cantidad
        item.save()
        messages.success(request, f'Se agregó otra unidad de "{producto.album}" al carrito.')
        
    except ItemCarrito.DoesNotExist:
        # VERIFICACIÓN DE STOCK (ÍTEM NUEVO)
        if cantidad_a_añadir > producto.stock:
            messages.error(request, f'No hay suficiente stock. Solo quedan {producto.stock} unidades.')
            return redirect('detalle_producto', pk=producto_id)
        
        # Si el ítem no existe y hay stock, lo crea
        ItemCarrito.objects.create(
            carrito=carrito,
            producto=producto,
            cantidad=cantidad_a_añadir,
            # GUARDA EL PRECIO ACTUAL del producto
            precio_item=producto.precio 
        )
        messages.success(request, f'"{producto.album}" se agregó al carrito por primera vez.')
        
    # Redirige a la página de detalle del producto o al catálogo
    return redirect('detalle_producto', pk=producto_id)


@require_POST
@login_required
def actualizar_carrito(request, item_id):
    """Actualiza la cantidad de un ItemCarrito específico y maneja el stock."""
    
    item = get_object_or_404(ItemCarrito, id=item_id)
    
    # Seguridad: Verificar que el ítem pertenezca al carrito del usuario actual
    if item.carrito.usuario != request.user:
        messages.error(request, "Error de seguridad: ítem no válido.")
        return redirect('ver_carrito')

    try:
        # Obtener la nueva cantidad del formulario (debe ser un entero positivo)
        nueva_cantidad = int(request.POST.get('cantidad'))
    except (TypeError, ValueError):
        messages.error(request, "La cantidad debe ser un número entero.")
        return redirect('ver_carrito')

    producto = item.producto

    if nueva_cantidad <= 0:
        # Si la cantidad es 0 o menos, eliminamos el ítem
        item.delete()
        messages.warning(request, f'"{producto.album}" eliminado del carrito.')
        
    elif nueva_cantidad > producto.stock:
        # Si la nueva cantidad excede el stock
        messages.error(request, f'No hay suficiente stock. Solo quedan {producto.stock} unidades disponibles.')
        # Redirige, manteniendo la cantidad actual del ítem en la interfaz
        
    else:
        # Si la cantidad es válida y hay stock, se actualiza
        item.cantidad = nueva_cantidad
        item.save()
        messages.success(request, f'Cantidad de "{producto.album}" actualizada a {nueva_cantidad}.')
        
    return redirect('ver_carrito')


# ELIMINAR un ítem del carrito (o reducir la cantidad a 0)
@login_required
def eliminar_de_carrito(request, item_id):
    """Elimina completamente un ItemCarrito según su ID."""
    
    item = get_object_or_404(ItemCarrito, id=item_id)
    
    # Seguridad: Verificar que el ítem pertenezca al carrito del usuario actual
    if item.carrito.usuario != request.user:
        messages.error(request, "Error: El ítem no pertenece a tu carrito.")
        return redirect('ver_carrito')

    album_eliminado = item.producto.album
    # Elimina el objeto ItemCarrito de la base de datos
    item.delete()
    
    messages.warning(request, f'"{album_eliminado}" fue eliminado de tu carrito.')
    return redirect('ver_carrito')