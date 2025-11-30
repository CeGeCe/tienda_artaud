from django.urls import path
from . import views

urlpatterns = [
    path('libros/', views.buscar_libros, name='scraper_libros'),

    path('jeds/', views.buscar_discos, name='scraper_jeds'),
]