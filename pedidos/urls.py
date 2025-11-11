# pedidos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout_proceso, name='checkout'),
    
    # Lista de Pedidos
    path('mis-pedidos/', views.ver_pedidos, name='ver_pedidos'),

    path('panel-ventas/', views.panel_ventas, name='panel_ventas'),
]