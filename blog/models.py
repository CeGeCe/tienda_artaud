from django.db import models
from django.contrib.auth.models import User

# Create your models here.


# Opciones de Categoría
CATEGORIA_CHOICES = (
    ('OPINION', 'Opinión'),
    ('RESEÑA', 'Reseña'),
    ('RECOMENDACION', 'Recomendación'),
    ('NOTICIA', 'Noticia'),
    ('OTRO', 'Otro'),
)

class Articulo(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    cuerpo = models.TextField(verbose_name="Contenido")
    
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articulos', verbose_name="Autor")
    
    categoria = models.CharField(
        max_length=20, 
        choices=CATEGORIA_CHOICES, 
        default='OTRO',
        verbose_name="Categoría"
    )
    
    fecha_publicacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Publicación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    # Sistema de Moderación (Igual que productos)
    aprobado = models.BooleanField(default=False, verbose_name="Aprobado por Admin")

    class Meta:
        ordering = ['-fecha_publicacion'] # Los más nuevos primero

    def __str__(self):
        return f"{self.titulo} - por {self.autor.username}"