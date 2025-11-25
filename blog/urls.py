from django.urls import path
from . import views


urlpatterns = [
    path('', views.lista_articulos, name='blog_lista'),

    path('articulo/<int:pk>/', views.detalle_articulo, name='blog_detalle'),
    
    path('nuevo/', views.CrearArticuloView.as_view(), name='blog_crear'),
    path('articulo/<int:pk>/eliminar/', views.EliminarArticuloView.as_view(), name='blog_eliminar'),
]