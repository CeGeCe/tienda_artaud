from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto

# Create your models here.

class Carrito(models.Model):
    """Representa el carrito de compras de un usuario."""
    # Relación uno a uno con el usuario

    # Si el usuario es eliminado, el carrito también se elimina.
    usuario = models.OneToOneField(User, on_delete=models.CASCADE) 
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

    # Calcular el total del carrito
    def get_total(self):
        # Itera sobre los ítems y suma el precio de cada uno al total
        total = sum(item.get_total() for item in self.items.all())
        return total


class ItemCarrito(models.Model):
    """Representa un producto individual dentro de un carrito."""
    # Relación muchos a uno: muchos ítems pertenecen a un solo carrito.
    
    # related_name='items' permite acceder a ItemCarrito desde Carrito (carrito.items.all())
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items') 
    
    # Relación muchos a uno: muchos ítems apuntan a un solo producto
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE) 
    
    cantidad = models.PositiveIntegerField(default=1)
    
    # Guardar el precio del producto al momento de añadirlo al carrito (para evitar cambios si el vendedor lo sube)
    precio_item = models.DecimalField(max_digits=10, decimal_places=2) 

    def __str__(self):
        return f"{self.cantidad} x {self.producto.album} ({self.producto.artista})"

    # Calcular el costo total de un ítem
    def get_total(self):
        return self.precio_item * self.cantidad