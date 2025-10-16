from django.db import models

class Bodega(models.Model):
    """
    Modelo que representa una bodega dentro del sistema WMS Provesi.

    Contiene información sobre la ciudad y la dirección de la bodega.
    """
    codigo = models.CharField(
        max_length=5,
        primary_key=True,
        help_text="Código único que identifica la bodega. Formato: abreviatura de la ciudad seguida de un número (por ejemplo: BOG01)."
    )

    ciudad = models.CharField(
        max_length=255,
        help_text="Ciudad donde se encuentra la bodega."
    )

    direccion = models.CharField(
        max_length=255,
        help_text="Dirección de la bodega."
    )

    class Meta:
        unique_together = ('ciudad', 'direccion')

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

    codigo = models.IntegerField(
        help_text="Código único de la estantería dentro de la bodega."
    )

    niveles = models.IntegerField(
        help_text="Número de niveles o repisas que tiene la estantería."
    )

    class Meta:
        unique_together = ('bodega', 'zona', 'codigo')

    def __str__(self):
        return f"Estantería {self.zona}{self.codigo} en Bodega {self.bodega.id}"
    
    def toJson(self):
        return {
            'bodega': self.bodega.toJson(),
            'zona': self.zona,
            'niveles': self.niveles,
        }
    
class Ubicacion(models.Model):
    """
    Modelo que representa una ubicación específica dentro de una estantería en el sistema WMS Provesi.

    Contiene información sobre la estantería a la que pertenece, el nivel y la posición dentro del nivel.
    """
    estanteria = models.ForeignKey(
        Estanteria,
        on_delete=models.CASCADE,
        related_name='ubicaciones',
        help_text="Estantería a la que pertenece la ubicación."
    )

    nivel = models.IntegerField(
        help_text="Nivel o repisa dentro de la estantería."
    )

    codigo = models.IntegerField(
        help_text="Posición específica dentro del nivel de la estantería."
    )

    capacidad = models.IntegerField(
        help_text="Capacidad máxima de la ubicación."
    )

    stock = models.IntegerField(
        help_text="Cantidad actual de ítems almacenados en la ubicación."
    )

    class Meta:
        unique_together = ('estanteria', 'nivel', 'codigo')

    def __str__(self):
        return f"Ubicación en Estantería {self.estanteria.id} - Nivel {self.nivel} - Posición {self.codigo}"
    
    def toJson(self):
        return {
            'estanteria': self.estanteria.toJson(),
            'nivel': self.nivel,
            'codigo': self.codigo,
            'capacidad': self.capacidad,
            'stock': self.stock,
        }
    
class Producto(models.Model):
    """
    Modelo que representa un producto almacenado en una ubicación específica dentro del sistema WMS Provesi.

    Contiene información sobre el código del producto, la ubicación donde está almacenado, nombre, descripción y precio.
    """
    codigo = models.CharField(
        max_length=50,
        primary_key=True,
        help_text="Código único que identifica el producto."
    )

    ubicacion = models.OneToOneField(
        Ubicacion,
        on_delete=models.CASCADE,
        related_name='producto',
        help_text="Ubicación donde se encuentra almacenado el producto."
    )

    nombre = models.CharField(
        max_length=255,
        help_text="Nombre del producto."
    )

    descripcion = models.CharField(
        max_length=255,
        help_text="Descripción del producto."
    )

    precio = models.IntegerField(
        help_text="Precio del producto en la moneda local (COP)."
    )

    def __str__(self):
        return f"Producto {self.codigo} - {self.nombre}"
    
    def toJson(self):
        return {
            'codigo': self.codigo,
            'ubicacion': self.ubicacion.toJson(),
            'descripcion': self.descripcion,
            'cantidad': self.precio,
        }