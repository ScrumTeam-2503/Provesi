from django import forms
from .models import Pedido, Item

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'estado', 
            'metodo_pago'
        ]
        labels = {
            'estado': 'Estado del Pedido',
            'metodo_pago': 'Método de Pago',
        }

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'producto', 
            'cantidad'
        ]
        labels = {
            'producto': 'Código del producto',
            'cantidad': 'Cantidad',
        }