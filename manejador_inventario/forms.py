from django import forms
from .models import Bodega, Estanteria

class BodegaForm(forms.ModelForm):
    class Meta:
        model = Bodega
        fields = [
            'codigo',
            'ciudad', 
            'direccion'
        ]
        labels = {
            'codigo': 'Código',
            'ciudad': 'Ciudad',
            'direccion': 'Dirección',
        }

class EstanteriaForm(forms.ModelForm):
    class Meta:
        model = Estanteria
        fields = [
            'zona',
            'codigo',
            'niveles'
        ]
        labels = {
            'zona': 'Zona',
            'codigo': 'Código',
            'niveles': 'Niveles',
        }