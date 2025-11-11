from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto

# Create your models here.

# --- CONSTANTES ---
ESTADO_CHOICES = (
    ('PENDIENTE', 'Pendiente de Pago'),
    ('PAGADO', 'Pagado / En Preparación'),
    ('ENVIADO', 'Enviado'),
    ('ENTREGADO', 'Entregado'),
    ('CANCELADO', 'Cancelado'),
)

class Pedido(models.Model):
    """Encabezado de la transacción: datos del comprador y total."""
    
    comprador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    
    direccion_envio = models.TextField(blank=True, null=True) 

    class Meta:
        ordering = ['-fecha_pedido'] # Ordenar por más reciente

    def __str__(self):
        return f"Pedido {self.id} de {self.comprador.username}"

class ItemPedido(models.Model):
    """Detalle de la transacción: un ítem específico que fue comprado."""
    
    # Relación con el Pedido y el Producto
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True) # SET_NULL si el producto original es eliminado
    
    # Información del Vendedor
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ventas')
    
    # Datos de la Compra
    album_comprado = models.CharField(max_length=200) # Guardamos el nombre por si el producto original se borra
    artista_comprado = models.CharField(max_length=200)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1)

    def get_subtotal(self):
        return self.precio_unitario * self.cantidad
    
    def __str__(self):
        return f"{self.cantidad} x {self.album_comprado} vendido por {self.vendedor.username}"