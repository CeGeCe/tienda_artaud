from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Perfil(models.Model):
    # Relación 1 a 1 con el modelo User estándar
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    
    # Campos extra
    avatar = models.ImageField(upload_to='avatares/', null=True, blank=True, verbose_name="Foto de Perfil")
    telefono = models.CharField(max_length=20, null=True, blank=True, verbose_name="Teléfono de contacto")
    direccion = models.TextField(null=True, blank=True, verbose_name="Dirección de envío")
    biografia = models.TextField(null=True, blank=True, verbose_name="Sobre mí", help_text="Contanos un poco sobre vos")
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"
    

# --- SEÑALES (SIGNALS) ---
# Asegura que se cree/actualice el Perfil automáticamente cuando se crea/actualiza un User

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    instance.perfil.save()