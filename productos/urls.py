from django.urls import path
from . import views

urlpatterns = [
    # 1. Página de INICIO: Muestra los destacados (usa la ruta raíz '')
    path('', views.home, name='home'),

    path('acerca/', views.acerca_de, name='acerca_de'),

    path('catalogo/', views.catalogo, name='catalogo'),
]