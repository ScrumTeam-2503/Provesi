from rest_framework import serializers
from .models import Item, Etapa


class EtapaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etapa
        fields = ['nombre', 'valor']


class ItemSerializer(serializers.ModelSerializer):
    etapas = EtapaSerializer(many=True, required=False)

    class Meta:
        model = Item
        fields = ['id', 'estado', 'metodo_de_pago', 'etapas']

    def create(self, validated_data):
        etapas_data = validated_data.pop('etapas', [])
        item = Item.objects.create(**validated_data)
        for etapa_data in etapas_data:
            Etapa.objects.create(pedido=item, **etapa_data)
        return item

    def update(self, instance, validated_data):
        etapas_data = validated_data.pop('etapas', [])

        instance.estado = validated_data.get('estado', instance.estado)
        instance.metodo_de_pago = validated_data.get(
            'metodo_de_pago', instance.metodo_de_pago)
        instance.save()

        if etapas_data:
            instance.etapas.all().delete()
            for etapa_data in etapas_data:
                Etapa.objects.create(pedido=instance, **etapa_data)

        return instance
