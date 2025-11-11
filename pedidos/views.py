from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from .models import Pedido, ItemPedido
from carrito.models import Carrito, ItemCarrito
from productos.models import Producto
from itertools import groupby # AGRUPAR

# Create your views here.


@login_required
@transaction.atomic # Si algo falla, se deshacen todos los cambios de DB
def checkout_proceso(request):
    """
    Procesa la compra: Mueve ítems del Carrito a Pedido, actualiza el stock y vacía el carrito.
    """
    try:
        carrito = Carrito.objects.get(usuario=request.user)
        items_carrito = ItemCarrito.objects.filter(carrito=carrito)
    except Carrito.DoesNotExist:
        messages.error(request, "Tu carrito está vacío o no existe.")
        return redirect('ver_carrito')

    if not items_carrito.exists():
        messages.error(request, "Tu carrito está vacío. Añade productos para comprar.")
        return redirect('catalogo')

    # VERIFICACIÓN FINAL de Stock
    productos_agotados = []
    for item_carrito in items_carrito:
        producto = item_carrito.producto
        if item_carrito.cantidad > producto.stock:
            productos_agotados.append(f"{producto.album} ({producto.stock} disponibles)")
    
    if productos_agotados:
        messages.error(request, f"No hay suficiente stock para los siguientes ítems: {', '.join(productos_agotados)}. Ajusta la cantidad.")
        return redirect('ver_carrito')

    # Encabezado del Pedido
    nuevo_pedido = Pedido.objects.create(
        comprador=request.user,
        monto_total=carrito.get_total(),
        # En una implementación real acá iría la dirección
        direccion_envio="Dirección de prueba", 
        estado='PAGADO' # Asumimos pago exitoso para la prueba
    )

    # Mover Ítems del Carrito al Pedido y Actualizar Stock ---
    for item_carrito in items_carrito:
        producto = item_carrito.producto
        
        # Crear ItemPedido (el registro de la venta)
        ItemPedido.objects.create(
            pedido=nuevo_pedido,
            producto=producto,
            vendedor=producto.vendedor, # Asignamos el vendedor del producto original
            album_comprado=producto.album,
            artista_comprado=producto.artista,
            precio_unitario=item_carrito.precio_item,
            cantidad=item_carrito.cantidad
        )
        
        # Actualizar el stock
        producto.stock -= item_carrito.cantidad
        producto.save()
        
        # Eliminar el ítem del carrito
        item_carrito.delete()
        
    messages.success(request, f"¡Compra realizada con éxito! Tu pedido {nuevo_pedido.id} fue creado.")
    
    # Eliminar el carrito (si quedó vacío, aunque los ítems ya se eliminaron)
    carrito.delete()
    
    return redirect('ver_pedidos') # Redirigir al comprador a ver sus pedidos


# Vista simple para ver los pedidos del comprador
@login_required
def ver_pedidos(request):
    pedidos = Pedido.objects.filter(comprador=request.user)
    return render(request, 'pedidos/pedidos_lista.html', {'pedidos': pedidos})


@login_required
def panel_ventas(request):
    """Muestra un panel con todas las ventas que el usuario logueado ha realizado."""
    
    # Obtener todos los ItemPedido donde el usuario actual es el vendedor
    # Ordenar por ID del pedido para que agarre 'groupby'
    ventas_items = ItemPedido.objects.filter(vendedor=request.user).order_by('pedido__id')
    
    # Lista para almacenar los pedidos agrupados por venta
    pedidos_del_vendedor = []
    
    # Agrupar los ItemPedido por el Pedido (Order) al que pertenecen.
    # La clave de agrupación es el ID del pedido: x.pedido.id
    for pedido_id, group in groupby(ventas_items, key=lambda x: x.pedido.id):
        items_del_pedido = list(group)
        # Encabezado del pedido principal
        pedido = items_del_pedido[0].pedido 
        
        # Calcular el total que le corresponde al vendedor dentro de este pedido
        total_venta = sum(item.get_subtotal() for item in items_del_pedido)
        
        pedidos_del_vendedor.append({
            'encabezado': pedido,       # Objeto Pedido principal
            'items': items_del_pedido,  # Lista de ItemPedido de este vendedor
            'total_venta': total_venta, # El total que vendió en esta transacción individual
        })
        
    return render(request, 'pedidos/panel_ventas.html', {'pedidos_del_vendedor': pedidos_del_vendedor})