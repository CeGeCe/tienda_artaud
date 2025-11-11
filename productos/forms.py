# productos/forms.py
from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    # Agregar estilos CSS o validaciones específicas de ser necesario
    
    class Meta:
        model = Producto
        # Excluye el 'vendedor' porque lo asigna la vista,
        # también el 'codigo_barras' para simplificar la entrada manual inicial.
        exclude = ('vendedor',) 
        # Para especificar qué incluir, usar 'fields':
        # fields = [
        #     'imagen_portada', 'stock', 'album', 'artista', 'precio', 'anio_lanzamiento', 
        #     'formato', 'pais_origen', 'condicion', 'estado', 'descripcion',
        #     'edicion', 'cantidad_discos', 'sello', 'cantidad_canciones',
        #     'genero_1', 'genero_2', 'codigo_barras'
        # ]