# productos/forms.py
from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    # Agregar estilos CSS o validaciones específicas de ser necesario
    
    class Meta:
        model = Producto

        # Excluye el 'vendedor' porque lo asigna la vista,
        # 'aprobado' porque depende del admin
        # y 'favoritos' porque no da
        exclude = ('vendedor', 'aprobado', 'favoritos')

        # Para especificar qué incluir, usar 'fields':
        # fields = [
        #     'imagen_portada', 'stock', 'album', 'artista', 'precio', 'anio_lanzamiento', 
        #     'formato', 'pais', 'condicion', 'estado', 'descripcion',
        #     'edicion', 'cantidad_discos', 'sello', 'cantidad_canciones',
        #     'genero_1', 'genero_2', 'codigo_barras'
        # ]

        help_texts = {
            'album': 'Preferentemente sin signos de puntuación',
            'artista': 'Si son unos cuantos, usá "Various Artists."',
            'precio': 'Precio en PESOS (No pidas deliradas; pensá en vender)',
            'pais': 'País donde se EDITÓ el material. NO de donde es la banda/artista',
            'anio_lanzamiento': 'Año de EDICIÓN del disco.',
            'condicion': 'Nuevo: Sellado de fábrica. Usado: Abierto. Sencillo, ¿no?',
            'estado': 'Sé honesto. Aclará en la descripción para evitar reclamos.',
            'imagen_portada': 'Se recomienda una imagen clara de al menos 500x500px.',
            'cantidad_discos': 'O cassettes'
        }