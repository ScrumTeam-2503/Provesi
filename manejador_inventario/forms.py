from django import forms
from .models import Bodega

class BodegaForm(forms.ModelForm):
    class Meta:
        model = Bodega
        fields = [
            'ciudad', 
            'direccion'
        ]
        labels = {
            'ciudad': 'Ciudad',
            'direccion': 'Dirección',
        }