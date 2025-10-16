from django.db import models
from manejador_inventario.models import Producto

class Pedido(models.Model):
    """
    Modelo que representa un pedido dentro del sistema WMS Provesi.

    Contiene información sobre el estado del pedido, método de pago 
    y fechas relevantes de creación y actualización.
    """

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
    ]

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='pendiente',
        help_text="Estado actual del pedido."
    )

    metodo_pago = models.CharField(
        max_length=20,
        choices=METODOS_PAGO,
        default='efectivo',
        help_text="Método de pago seleccionado para el pedido."
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se creó el pedido."
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        help_text="Fecha y hora de la última actualización del pedido."
    )

    def __str__(self):
        return f"Pedido {self.id} - {self.estado}"
    
    def toJson(self):
        return {
            'id': self.id,
            'estado': self.estado,
            'metodo_pago': self.metodo_pago,
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion,
        }

class Item(models.Model):
    """
    Modelo que representa un ítem dentro de un pedido en el sistema WMS Provesi.

    Contiene información sobre el producto, cantidad y precio asociado al ítem.
    """

    pedido = models.ForeignKey(
        Pedido,
        related_name='items',
        on_delete=models.CASCADE,
        help_text="Pedido al que pertenece este ítem."
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        help_text="Producto asociado al ítem."
    )

    cantidad = models.PositiveIntegerField(
        help_text="Cantidad del producto en el ítem."
    )

    def __str__(self):
        return f"Item {self.id} - {self.producto} (x{self.cantidad})"
    
    def toJson(self):
        return {
            'id': self.id,
            'pedido_id': self.pedido.id,
            'producto': self.producto,
            'cantidad': self.cantidad,
        }