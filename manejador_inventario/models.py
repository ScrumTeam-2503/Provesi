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
    
class Estanteria(models.Model):
    """
    Modelo que representa una estantería dentro de una bodega en el sistema WMS Provesi.

    Contiene información sobre el código, la bodega a la que pertenece, la zona y los niveles de la estantería.
    """
    bodega = models.ForeignKey(
        Bodega,
        on_delete=models.CASCADE,
        related_name='estanterias',
        help_text="Bodega a la que pertenece la estantería."
    )

    zona = models.CharField(
        max_length=1,
        help_text="Zona dentro de la bodega donde se encuentra la estantería."
    )

    niveles = models.IntegerField(
        help_text="Número de niveles o repisas que tiene la estantería."
    )

    def __str__(self):
        return f"Estantería {self.id} en Bodega {self.bodega.id}"
    
    def toJson(self):
        return {
            'bodega': self.bodega.toJson(),
            'zona': self.zona,
            'niveles': self.niveles,
        }