from django.urls import path
from . import views

urlpatterns = [
    path('', views.ver_carrito, name='ver_carrito'),
    
    # Añadir un producto (usa POST)
    path('agregar/<int:producto_id>/', views.agregar_a_carrito, name='agregar_a_carrito'),
    
    # Eliminar un ítem (usa el ID del ItemCarrito, no el del Producto)
    path('eliminar/<int:item_id>/', views.eliminar_de_carrito, name='eliminar_de_carrito'),

    # Actualizar la cantidad de un ítem
    path('actualizar/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),

    path('presupuesto/pdf/', views.generar_presupuesto_pdf, name='generar_presupuesto'),

    path('presupuesto/opciones/', views.opciones_presupuesto, name='opciones_presupuesto'),
    path('presupuesto/procesar/', views.procesar_presupuesto, name='procesar_presupuesto'),
]