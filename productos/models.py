from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# --- CONSTANTES (CHOICES) ---
FORMATO_CHOICES = (
    ('BLURAY', 'Blu-ray'),
    ('CASSETTE', 'Cassette'),
    ('CD', 'CD'),
    ('DVD', 'DVD'),
    ('VHS', 'VHS'),
    ('VINILO', 'Vinilo'),
)

CONDICION_CHOICES = (
    ('USADO', 'Usado'),
    ('NUEVO', 'Nuevo'),
)

ESTADO_CHOICES = (
    ('BUENO', 'Bueno'),
    ('REGULAR', 'Regular'),
    ('MALO', 'Malo'),
)

EDICION_CHOICES = (
    ('ESTANDAR', 'Estándar'),
    ('ESPECIAL', 'Especial'),
    ('LIMITADA', 'Limitada'),
)

GENERO_1_CHOICES = (
    ('CLASICO', 'Clásico'),
    ('ELECTRONICA', 'Electrónica'),
    ('FOLK', 'Folk'),
    ('HIPHOP', 'Hip-hop'),
    ('JAZZ', 'Jazz'),
    ('POP', 'Pop'),
    ('ROCK', 'Rock'),
)


class Producto(models.Model):
    # --- CAMPOS OBLIGATORIOS ---
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE)
    
    imagen_portada = models.ImageField(
        upload_to='portadas/',
        blank=True,
        null=True
    )

    stock = models.PositiveIntegerField(default=1)

    album = models.CharField(max_length=200)
    artista = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    anio_lanzamiento = models.IntegerField() 

    # Formatos predefinidos: Vinilo, CD, Cassette
    formato = models.CharField(
        max_length = 10, 
        choices = FORMATO_CHOICES
    )
    
    pais_origen = models.CharField(max_length=100)
    
    # Condiciones predefinidas: Usado o Nuevo
    condicion = models.CharField(
        max_length = 10, 
        choices = CONDICION_CHOICES
    )
    
    # Estados predefinidos: Bueno, Regular, Malo
    estado = models.CharField(
        max_length = 10, 
        choices = ESTADO_CHOICES
    )
    
    descripcion = models.TextField(max_length=500) 
    
    
    # --- CAMPOS OPCIONALES ---
    
    edicion = models.CharField(
        max_length=10, 
        choices = EDICION_CHOICES, 
        default = 'ESTANDAR',
        blank = True,
        null = True
    )
        
    sello = models.CharField(
        max_length = 100, 
        blank = True, 
        null = True
    )

    cantidad_discos = models.IntegerField(
        blank = True, 
        null = True
    )
    
    cantidad_canciones = models.IntegerField(
        blank = True, 
        null = True
    )
    
    genero_1 = models.CharField(
        max_length = 50, 
        choices = GENERO_1_CHOICES,
        blank = True, 
        null = True
    )
    
    genero_2 = models.CharField(
        max_length = 50, 
        blank = True, 
        null = True
    )
    
    codigo_barras = models.CharField(
        max_length = 50, 
        blank = True, 
        null = True
    )

    favoritos = models.ManyToManyField(User, related_name='productos_favoritos', blank=True)

    # --- MÉTODO PARA REPRESENTACIÓN EN EL ADMIN
    def __str__(self):
        return f"{self.artista} - {self.album} ({self.formato})"