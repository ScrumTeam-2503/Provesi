from django.apps import AppConfig

class ManejadorInventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'manejador_inventario'
    
    def ready(self):
        """Importar signals cuando la app esté lista"""
        import manejador_inventario.models  # Esto registra los signals