from django.contrib import admin
from .models import Producto

# Register your models here.

class ProductoAdmin(admin.ModelAdmin):
    # Campos en la lista de productos (en la tabla principal)
    list_display = ('album', 'artista', 'formato', 'precio', 'condicion', 'estado')
    
    # Filtros laterales para buscar rápidamente
    list_filter = ('formato', 'condicion', 'estado', 'genero_1', 'anio_lanzamiento')
    
    # Campos por los que se puede buscar
    search_fields = ('album', 'artista', 'sello', 'codigo_barras')
    
    # Orden por defecto
    ordering = ('artista', 'album')

# Registra el modelo con la clase de configuración
admin.site.register(Producto, ProductoAdmin)