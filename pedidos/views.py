from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ModelViewSet
from .models import Item
from .serializers import ItemSerializer

class ItemViewSet(ModelViewSet): #CRUD completo
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
