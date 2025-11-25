# pedidos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout_proceso, name='checkout'),
    
    # Lista de Pedidos
    path('mis-pedidos/', views.ver_pedidos, name='ver_pedidos'),

    path('panel-ventas/', views.panel_ventas, name='panel_ventas'),

    # ACTUALIZAR el estado de un ItemPedido (venta individual)
    path('actualizar-estado/<int:item_id>/', views.actualizar_estado_venta, name='actualizar_estado_venta'),

    path('<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),

    path('pago-exitoso/<int:pedido_id>/', views.pago_exitoso, name='pago_exitoso'),
    path('pago-fallido/', views.pago_fallido, name='pago_fallido'),

    path('pagar-pendiente/<int:pedido_id>/', views.pagar_pedido_pendiente, name='pagar_pedido_pendiente'),

    path('admin/ventas-globales/', views.admin_resumen_ventas, name='admin_ventas_globales'),

    path('dashboard/', views.dashboard_analytics, name='dashboard_analytics'),
]