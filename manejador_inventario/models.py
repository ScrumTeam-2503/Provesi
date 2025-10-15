from django.db import models

class Bodega(models.Model):
    """
    Modelo que representa una bodega dentro del sistema WMS Provesi.

    Contiene información sobre la ciudad y la dirección de la bodega.
    """
    ciudad = models.CharField(
        max_length=255,
        help_text="Ciudad donde se encuentra la bodega."
    )

    direccion = models.CharField(
        max_length=255,
        help_text="Dirección de la bodega."
    )

    def __str__(self):
        return f"Bodega en {self.ciudad} - {self.direccion}"
    
    def toJson(self):
        return {
            'id': self.id,
            'ciudad': self.ciudad,
            'direccion': self.direccion,
        }