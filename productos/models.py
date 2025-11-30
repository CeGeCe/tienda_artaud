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
    ('METAL', 'Metal'),
    ('POP', 'Pop'),
    ('RAP', 'Rap'),
    ('REGGAE', 'Reggae'),
    ('ROCK', 'Rock'),
    ('SOUNDTRACK', 'Soundtrack')
)


class Producto(models.Model):
    # --- CAMPOS OBLIGATORIOS ---
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE)
    
    imagen_portada = models.ImageField(
        upload_to='portadas/',
        blank=True,
        null=True
    )

    stock = models.PositiveIntegerField(default=1, verbose_name="Copias disponibles")

    album = models.CharField(max_length=200, verbose_name="Álbum")
    artista = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    anio_lanzamiento = models.IntegerField(verbose_name="Año de lanzamiento")

    # Formatos predefinidos: Vinilo, CD, Cassette
    formato = models.CharField(
        max_length = 10, 
        choices = FORMATO_CHOICES
    )
    
    pais = models.CharField(max_length=100, verbose_name="País")
    
    # Condiciones predefinidas: Usado o Nuevo
    condicion = models.CharField(
        max_length = 10, 
        choices = CONDICION_CHOICES,
        verbose_name= "Condición"
    )
    
    # Estados predefinidos: Bueno, Regular, Malo
    estado = models.CharField(
        max_length = 10, 
        choices = ESTADO_CHOICES
    )
    
    descripcion = models.TextField(max_length=500, verbose_name="Condición")
    
    # --- CAMPOS OPCIONALES ---

    edicion = models.CharField(
        max_length=10, 
        choices = EDICION_CHOICES, 
        default = 'ESTANDAR',
        blank = True,
        null = True,
        verbose_name= "Edición"
    )
        
    sello = models.CharField(
        max_length = 100, 
        blank = True, 
        null = True,
        verbose_name= "Sello discográfico"
    )

    cantidad_discos = models.IntegerField(
        blank = True, 
        null = True,
        verbose_name= "Cantidad de discos"
    )
    
    cantidad_canciones = models.IntegerField(
        blank = True, 
        null = True,
        verbose_name= "Cantidad de canciones"
    )
    
    genero_1 = models.CharField(
        max_length = 50, 
        choices = GENERO_1_CHOICES,
        blank = True, 
        null = True,
        verbose_name= "Género principal"
    )
    
    genero_2 = models.CharField(
        max_length = 50, 
        blank = True, 
        null = True,
        verbose_name= "Género secundario"
    )
    
    codigo_barras = models.CharField(
        max_length = 50, 
        blank = True, 
        null = True,
        verbose_name= "Código de barras"
    )

    # default=False : al crearse, NO es visible hasta que se apruebe
    aprobado = models.BooleanField(default=False, verbose_name="Aprobado por Admin")


class Favorito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mis_favoritos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='favorited_by')
    fecha_agregado = models.DateTimeField(auto_now_add=True) # Ordenar por fecha

    class Meta:
        unique_together = ('usuario', 'producto') # Evita duplicados
        ordering = ['-fecha_agregado']

    def __str__(self):
        return f"{self.usuario.username} -> {self.producto.album}"
    

    # MÉTODO PARA REPRESENTACIÓN EN EL ADMIN
    def __str__(self):
        return f"{self.artista} - {self.album} ({self.formato})"