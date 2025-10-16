from django import forms
from .models import Bodega, Estanteria

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

class EstanteriaForm(forms.ModelForm):
    class Meta:
        model = Estanteria
        fields = [
            'zona', 
            'niveles'
        ]
        labels = {
            'zona': 'Zona',
            'niveles': 'Niveles',
        }