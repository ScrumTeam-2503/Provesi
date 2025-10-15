from django import forms
from .models import Pedido

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