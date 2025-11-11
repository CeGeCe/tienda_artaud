from django.urls import path
from . import views
from .views import ProductoCreateView, ProductoUpdateView, ProductoDeleteView


urlpatterns = [
    # 1. Página de INICIO: Muestra los destacados (usa la ruta raíz '')
    path('', views.home, name='home'),

    path('about/', views.about, name='about'),

    path('catalogo/', views.catalogo, name='catalogo'),

    path('producto/<int:pk>', views.detalle_producto, name='detalle_producto'),

    path('mis-productos/', views.mis_productos, name='mis_productos'),

    path('mis-productos/publicar/', ProductoCreateView.as_view(), name='publicar_producto'),

    path('mis-productos/editar/<int:pk>/', ProductoUpdateView.as_view(), name='editar_producto'),

    path('mis-productos/eliminar/<int:pk>/', ProductoDeleteView.as_view(), name='eliminar_producto')
]