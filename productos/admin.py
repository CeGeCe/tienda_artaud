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


# Campos para el formulario de edición
    fields = (
        'vendedor', 'album', 'artista', 'precio', 'anio_lanzamiento', 
        'formato', 'pais_origen', 'condicion', 'estado', 'descripcion',
        'edicion', 'cantidad_discos', 'sello', 'cantidad_canciones',
        'genero_1', 'genero_2', 'codigo_barras'
    )

    # El vendedor es de solo lectura para evitar que se cambie por accidente
    readonly_fields = ('vendedor',) 

    # Sobrescribe el método save_model para asignar el usuario automáticamente
    def save_model(self, request, obj, form, change):
        if not change: # Si el objeto se está creando por primera vez
            obj.vendedor = request.user # Asigna el usuario logueado como vendedor
        super().save_model(request, obj, form, change)


# Registra el modelo con la clase de configuración
admin.site.register(Producto, ProductoAdmin)