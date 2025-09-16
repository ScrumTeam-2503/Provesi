from django.db import models

# Create your models here.  

class Item(models.Model):
    estado = models.CharField(max_length=120)
    metodo_de_pago = models.CharField(max_length=120)
    
    def __str__(self):
        return f"{self.estado}: {self.metodo_de_pago}"



class Etapa(models.Model):
    pedido = models.ForeignKey(Item, related_name="etapas", on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)   # clave del dict
    valor = models.CharField(max_length=100)   # valor del dict

    def __str__(self):
        return f"{self.nombre}: {self.valor}"







