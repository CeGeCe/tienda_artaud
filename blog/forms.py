from django import forms
from .models import Articulo

class ArticuloForm(forms.ModelForm):
    class Meta:
        model = Articulo
        fields = ['titulo', 'categoria', 'cuerpo']
        
        widgets = {
            'cuerpo': forms.Textarea(attrs={'rows': 10, 'placeholder': 'Escribí tu artículo acá...'}),
        }
        
        help_texts = {
            'categoria': 'Elegí el tipo de artículo que mejor describa tu contenido.',
        }