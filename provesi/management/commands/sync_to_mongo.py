from django.core.management.base import BaseCommand
from manejador_pedidos.models import Pedido
from manejador_inventario.models import Producto, Bodega
from provesi.mongodb_sync import (
    sync_pedido_to_mongo,
    sync_producto_to_mongo,
    sync_bodega_to_mongo,
    test_connection
)

class Command(BaseCommand):
    help = 'Sincroniza todos los datos existentes de PostgreSQL a MongoDB'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Solo probar conexión sin sincronizar',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('🚀 Sincronización PostgreSQL → MongoDB'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')
        
        # Test de conexión
        self.stdout.write('📡 Probando conexión a MongoDB...')
        if not test_connection():
            self.stdout.write(self.style.ERROR('❌ No se pudo conectar a MongoDB'))
            return
        
        self.stdout.write(self.style.SUCCESS('✅ Conexión exitosa\n'))
        
        if options['test']:
            self.stdout.write(self.style.SUCCESS('✅ Test de conexión completado'))
            return
        
        # Sincronizar Pedidos
        self.stdout.write('📦 Sincronizando pedidos...')
        pedidos_ok = 0
        for pedido in Pedido.objects.all():
            if sync_pedido_to_mongo(pedido):
                pedidos_ok += 1
        self.stdout.write(self.style.SUCCESS(f'   ✅ {pedidos_ok} pedidos sincronizados\n'))
        
        # Sincronizar Productos
        self.stdout.write('📦 Sincronizando productos...')
        productos_ok = 0
        for producto in Producto.objects.all():
            if sync_producto_to_mongo(producto):
                productos_ok += 1
        self.stdout.write(self.style.SUCCESS(f'   ✅ {productos_ok} productos sincronizados\n'))
        
        # Sincronizar Bodegas
        self.stdout.write('📦 Sincronizando bodegas...')
        bodegas_ok = 0
        for bodega in Bodega.objects.all():
            if sync_bodega_to_mongo(bodega):
                bodegas_ok += 1
        self.stdout.write(self.style.SUCCESS(f'   ✅ {bodegas_ok} bodegas sincronizadas\n'))
        
        # Resumen
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('✅ Sincronización completada'))
        self.stdout.write(self.style.SUCCESS('=' * 50))