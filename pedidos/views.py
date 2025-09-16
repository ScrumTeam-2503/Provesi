from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ModelViewSet
from .models import Item, Etapa
from .serializers import ItemSerializer, EtapaSerializer

class ItemViewSet(ModelViewSet): #CRUD completo
    queryset = Item.objects.prefetch_related('etapas').all()  # Optimización para cargar etapas relacionadas
    serializer_class = ItemSerializer

class EtapaViewSet(ModelViewSet): #CRUD completo para etapas
    queryset = Etapa.objects.all()
    serializer_class = EtapaSerializer
