from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from .models import Pedido, ItemPedido, ESTADO_CHOICES
from carrito.models import Carrito, ItemCarrito
from productos.models import Producto
from itertools import groupby # AGRUPAR
from django.views.decorators.http import require_POST
import mercadopago
from django.conf import settings
from django.urls import reverse

from .models import Pedido, ItemPedido
from carrito.models import Carrito, ItemCarrito
from django.db.models import Sum, Count, F
from django.db.models.functions import ExtractHour

# Create your views here.


@login_required
@transaction.atomic # Si algo falla, se deshacen todos los cambios de DB
def checkout_proceso(request):
    """
    1. Crea el Pedido (Pendiente).
    2. Genera la preferencia en Mercado Pago.
    3. Redirige al usuario a pagar.
    """

    # Obtener carrito
    try:
        carrito = Carrito.objects.get(usuario=request.user)
        items_carrito = ItemCarrito.objects.filter(carrito=carrito)
    except Carrito.DoesNotExist:
        return redirect('ver_carrito')

    if not items_carrito.exists():
        return redirect('catalogo')

    # Validación de Stock
    productos_agotados = []
    for item_c in items_carrito:
        if item_c.cantidad > item_c.producto.stock:
            productos_agotados.append(item_c.producto.album)
    
    if productos_agotados:
        messages.error(request, f"Stock insuficiente para: {', '.join(productos_agotados)}")
        return redirect('ver_carrito')

    # Crea el Pedido como PENDIENTE
    pedido = Pedido.objects.create(
        comprador=request.user,
        monto_total=carrito.get_total(),
        estado='PENDIENTE'
    )

    # Preparar datos para Mercado Pago y Crear ItemPedido
    items_mp = []
    
    for item_c in items_carrito:
        producto = item_c.producto
        
        # Guardar ItemPedido en la BB.DD
        ItemPedido.objects.create(
            pedido=pedido,
            producto=producto,
            vendedor=producto.vendedor,
            album_comprado=producto.album,
            artista_comprado=producto.artista,
            precio_unitario=item_c.precio_item,
            cantidad=item_c.cantidad,
            estado='PENDIENTE'
        )
        
        # Descontar stock (Reserva)
        producto.stock -= item_c.cantidad
        producto.save()
        
        # Estructura del ítem para Mercado Pago
        items_mp.append({
            "title": f"{producto.artista} - {producto.album}",
            "quantity": int(item_c.cantidad),
            "currency_id": "ARS",
            "unit_price": float(item_c.precio_item)
        })

    # Configurar el SDK de Mercado Pago
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    
    # Crear las URLs de retorno
    # 'build_absolute_uri' para que MP sepa volver a la tienda
    url_exito = request.build_absolute_uri(reverse('pago_exitoso', args=[pedido.id]))
    url_fallo = request.build_absolute_uri(reverse('pago_fallido'))

    preference_data = {
        "items": items_mp,
        "payer": {
            "email": request.user.email
        },
        "back_urls": {
            "success": url_exito,
            "failure": url_fallo,
            "pending": url_fallo
        },
        # "auto_return": "approved", # Vuelve SI se aprueba el pago
        "external_reference": str(pedido.id),
    }

    # ⚠️ AGREGA ESTAS LÍNEAS DE DEPURACIÓN AQUÍ:
    print("--- DATOS A ENVIAR A MP ---")
    print(preference_data)
    print("---------------------------")

    # Crea la Preferencia
    preference_response = sdk.preference().create(preference_data)
    preference = preference_response.get("response", {})

    # ⚠️ DIAGNÓSTICO: Verificamos si existe el init_point
    if "init_point" not in preference:
        # Si falla, imprimimos el error real en la consola
        print("❌ ERROR DE MERCADO PAGO:", preference_response)
        
        messages.error(request, "Hubo un error al generar el pago. Intenta nuevamente.")
        # Borramos el pedido pendiente para no dejar basura
        pedido.delete() 
        return redirect('ver_carrito')

    # Vaciar el carrito local (porque ya está hecho el pedido)
    items_carrito.delete()
    carrito.delete() # Borra el carrito / lo deja vacío

    # Redirigir a Mercado Pago
    return redirect(preference["init_point"])


# Vista simple para ver los pedidos del comprador
@login_required
def ver_pedidos(request):
    pedidos = Pedido.objects.filter(comprador=request.user)
    return render(request, 'pedidos/pedidos_lista.html', {'pedidos': pedidos})


@require_POST
@login_required
def actualizar_estado_venta(request, item_id):
    """Permite al vendedor actualizar el estado de un ItemPedido específico."""
    
    item = get_object_or_404(ItemPedido, id=item_id)
    
    # Seguridad: Solo el vendedor
    if item.vendedor != request.user:
        messages.error(request, "No tienes permiso.")
        return redirect('panel_ventas')
        
    nuevo_estado = request.POST.get('nuevo_estado')
    estado_anterior = item.estado
    
    # --- VALIDACIONES DE FLUJO ---
    
    # No permitir volver a 'PENDIENTE' bajo ninguna circunstancia
    if nuevo_estado == 'PENDIENTE':
        messages.error(request, "No se puede volver al estado 'Pendiente' manualmente.")
        return redirect('panel_ventas')

    # Si ya está enviado o entregado, no volver a 'PAGADO' (opcional)
    if estado_anterior in ['ENVIADO', 'ENTREGADO'] and nuevo_estado == 'PAGADO':
        messages.warning(request, "El pedido ya estaba avanzado. Verifica si es correcto volver a 'Pagado'.")
        # (Aquí permitimos el cambio pero avisamos, o podría bloquearse con un return)

    # --- LÓGICA DE STOCK (CANCELACIÓN) ---
    
    if item.producto: # Verificamos que el producto original siga existiendo
        
        # Si se CANCELA la venta -> Devolver Stock
        if nuevo_estado == 'CANCELADO' and estado_anterior != 'CANCELADO':
            item.producto.stock += item.cantidad
            item.producto.save()
            messages.info(request, f"Venta cancelada. Se han repuesto {item.cantidad} unidades al stock.")

        # Si se REACTIVA una venta cancelada -> Restar Stock (si hay disponible)
        elif estado_anterior == 'CANCELADO' and nuevo_estado != 'CANCELADO':
            if item.producto.stock >= item.cantidad:
                item.producto.stock -= item.cantidad
                item.producto.save()
            else:
                messages.error(request, "No hay suficiente stock para reactivar esta venta cancelada.")
                return redirect('panel_ventas')

    # --- GUARDADO ---
    
    item.estado = nuevo_estado
    item.save()
    messages.success(request, f'Estado actualizado a {item.get_estado_display()}.')

    return redirect('panel_ventas')


@login_required
def detalle_pedido(request, pedido_id):
    """
    Muestra los detalles de un pedido específico, 
    asegurándose de que pertenezca al comprador logueado.
    """
    # Intentam obtener el pedido por ID, solo si el comprador es el usuario actual.
    pedido = get_object_or_404(Pedido, id=pedido_id, comprador=request.user)
    
    return render(request, 'pedidos/pedido_detalle.html', {'pedido': pedido})


def pago_exitoso(request, pedido_id):
    """Cuando desde MP confirma el pago exitoso."""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Verificar usuario
    if request.user != pedido.comprador:
        return redirect('home')

    # Actualizar estado del Pedido
    pedido.estado = 'PAGADO'
    pedido.save()
    
    # Actualizar estado de los ítems individuales
    pedido.items.all().update(estado='PAGADO')

    messages.success(request, f"¡Pago Acreditado! Tu pedido #{pedido.id} está confirmado.")
    return redirect('detalle_pedido', pedido_id=pedido.id)

def pago_fallido(request):
    """Si el usuario cancela o el pago falla."""
    messages.error(request, "El proceso de pago fue cancelado o rechazado.")
    return redirect('catalogo')


@login_required
def pagar_pedido_pendiente(request, pedido_id):
    """Regenera la preferencia de MP para un pedido existente y redirige."""
    pedido = get_object_or_404(Pedido, id=pedido_id, comprador=request.user)

    # Solo permitir si está pendiente
    if pedido.estado != 'PENDIENTE':
        messages.info(request, "Este pedido ya no está pendiente de pago.")
        return redirect('detalle_pedido', pedido_id=pedido.id)

    # Reconstruir la lista de ítems para MP
    items_mp = []
    for item in pedido.items.all():
        items_mp.append({
            "title": f"{item.producto.artista} - {item.album_comprado}",
            "quantity": int(item.cantidad),
            "currency_id": "ARS",
            "unit_price": float(item.precio_unitario)
        })

    # Configurar SDK
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    url_exito = request.build_absolute_uri(reverse('pago_exitoso', args=[pedido.id]))
    url_fallo = request.build_absolute_uri(reverse('pago_fallido'))

    preference_data = {
        "items": items_mp,
        "payer": {"email": request.user.email},
        "back_urls": {
            "success": url_exito,
            "failure": url_fallo,
            "pending": url_fallo
        },
        # "auto_return": "approved", # Descomentar en producción
        "external_reference": str(pedido.id),
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response.get("response", {})

    if "init_point" not in preference:
        messages.error(request, "Error al conectar con Mercado Pago.")
        return redirect('detalle_pedido', pedido_id=pedido.id)

    return redirect(preference["init_point"])


def calcular_estadisticas(items_queryset):
    """
    Función auxiliar que recibe un QuerySet de ItemPedido   
    y devuelve un diccionario con KPIs y datos para gráficos.
    """
    # 1. KPIs (Key Performance Indicators)
    kpis = items_queryset.aggregate(
        total_plata=Sum(F('precio_unitario') * F('cantidad')),
        total_items=Sum('cantidad')
    )

    # 2. Gráfico Formatos
    formatos_stats = items_queryset.values('producto__formato').annotate(total=Sum('cantidad')).order_by('-total')
    formatos_data = {
        'labels': [item['producto__formato'] for item in formatos_stats],
        'data': [item['total'] for item in formatos_stats]
    }

    # 3. Gráfico Horas
    horas_stats = items_queryset.annotate(hora=ExtractHour('pedido__fecha_pedido')).values('hora').annotate(total=Count('id')).order_by('hora')
    horas_array = [0] * 24
    for h in horas_stats:
        if h['hora'] is not None:
            horas_array[h['hora']] = h['total']
    
    horas_data = {
        'labels': [f"{i}:00" for i in range(24)],
        'data': horas_array
    }

    return {
        'kpis': kpis,
        'formatos': formatos_data,
        'horas': horas_data,
    }


@login_required
def panel_ventas(request):
    """Muestra un panel con Las 3 ventas más reciente; y un Dashboard personal """
    
    # Obtener los Items del Vendedor y ordenar por Fecha
    ventas_items = ItemPedido.objects.filter(vendedor=request.user).order_by('-pedido__fecha_pedido')
    
    # Calcular Estadísticas (Para la parte inferior)
    stats = calcular_estadisticas(ventas_items)
    
    # Agrupar Ventas (Para la parte superior)
    pedidos_agrupados = []
    # Agrupar por ID de pedido
    for pedido_id, group in groupby(ventas_items, key=lambda x: x.pedido.id):
        items_del_pedido = list(group)
        pedido = items_del_pedido[0].pedido 
        total_venta = sum(item.get_subtotal() for item in items_del_pedido)
        
        pedidos_agrupados.append({
            'encabezado': pedido,
            'items': items_del_pedido,
            'total_venta': total_venta,
        })
    
    # LIMITAR A LOS 3 MÁS RECIENTES
    ultimas_ventas = pedidos_agrupados[:3]
    
    context = {
        'ultimas_ventas': ultimas_ventas,
        'stats': stats,
        'titulo_pagina': 'Mi Panel de Ventas',
    }
    return render(request, 'pedidos/panel_ventas.html', context)


# --- DASHBOARD GLOBAL (ADMIN) ---
@login_required
def admin_dashboard(request):
    """Vista principal para Admins: KPIs Globales y acceso al listado."""
    if not request.user.is_staff:
        return redirect('home')

    items_global = ItemPedido.objects.all()
    stats = calcular_estadisticas(items_global)
    
    # Top Vendedores
    vendedores_stats = items_global.values('vendedor__username').annotate(total=Sum('cantidad')).order_by('-total')[:5]
    top_vendedores = {
        'labels': [item['vendedor__username'] for item in vendedores_stats],
        'data': [item['total'] for item in vendedores_stats]
    }

    context = {
        'stats': stats,
        'top_vendedores': top_vendedores,
        'titulo_pagina': 'Dashboard Global'
    }
    return render(request, 'pedidos/admin_dashboard.html', context)


# --- LISTADO COMPLETO (ADMIN - previously RESUMEN)
@login_required
def admin_lista_ventas(request):
    """Listado detallado de todas las ventas (accedido desde el Dashboard)."""
    if not request.user.is_staff: return redirect('home')
    
    ventas_items = ItemPedido.objects.all().order_by('-pedido__fecha_pedido')
    ventas_globales = []
    
    for pedido_id, group in groupby(ventas_items, key=lambda x: x.pedido.id):
        items_del_pedido = list(group)
        ventas_globales.append({
            'encabezado': items_del_pedido[0].pedido,
            'items': items_del_pedido,
            'total_venta': sum(i.get_subtotal() for i in items_del_pedido),
        })
        
    return render(request, 'pedidos/admin_ventas.html', {'ventas_globales': ventas_globales})