"""
Utilidades para sincronización con MongoDB
"""
import pymongo
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def get_mongo_db():
    """
    Obtiene conexión a MongoDB.
    Retorna None si hay error.
    """
    config = settings.MONGODB_CONFIG
    try:
        client = pymongo.MongoClient(
            host=config['host'],
            port=config['port'],
            username=config.get('username'),
            password=config.get('password'),
            authSource=config.get('authSource', 'admin'),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        # Test de conexión
        client.server_info()
        db = client[config['database']]
        logger.info(f"✅ Conectado a MongoDB: {config['host']}:{config['port']}")
        return db
    except Exception as e:
        logger.error(f"❌ Error conectando a MongoDB: {e}")
        return None


def sync_pedido_to_mongo(pedido):
    """
    Sincroniza un pedido a MongoDB con todos sus items.
    """
    try:
        db = get_mongo_db()
        if not db:
            logger.warning(f"MongoDB no disponible, no se sincronizó pedido {pedido.id}")
            return False
        
        # Construir documento
        pedido_data = {
            'postgres_id': pedido.id,
            'estado': pedido.estado,
            'metodo_pago': pedido.metodo_pago,
            'fecha_creacion': pedido.fecha_creacion.isoformat(),
            'fecha_actualizacion': pedido.fecha_actualizacion.isoformat(),
            'items': []
        }
        
        # Agregar items
        total = 0
        for item in pedido.items.all():
            subtotal = item.cantidad * item.producto.precio
            total += subtotal
            
            pedido_data['items'].append({
                'id': item.id,
                'producto_codigo': item.producto.codigo,
                'producto_nombre': item.producto.nombre,
                'producto_descripcion': item.producto.descripcion,
                'producto_precio': item.producto.precio,
                'cantidad': item.cantidad,
                'subtotal': subtotal
            })
        
        pedido_data['total'] = total
        pedido_data['num_items'] = len(pedido_data['items'])
        pedido_data['sync_timestamp'] = datetime.now().isoformat()
        
        # Upsert en MongoDB
        result = db.pedidos.update_one(
            {'postgres_id': pedido.id},
            {'$set': pedido_data},
            upsert=True
        )
        
        logger.info(f"✅ Pedido {pedido.id} sincronizado a MongoDB")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error sincronizando pedido {pedido.id}: {e}")
        return False


def delete_pedido_from_mongo(pedido_id):
    """
    Elimina un pedido de MongoDB.
    """
    try:
        db = get_mongo_db()
        if not db:
            return False
        
        result = db.pedidos.delete_one({'postgres_id': pedido_id})
        logger.info(f"✅ Pedido {pedido_id} eliminado de MongoDB")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error eliminando pedido {pedido_id}: {e}")
        return False


def sync_producto_to_mongo(producto):
    """
    Sincroniza un producto a MongoDB con todas sus ubicaciones.
    """
    try:
        db = get_mongo_db()
        if not db:
            logger.warning(f"MongoDB no disponible, no se sincronizó producto {producto.codigo}")
            return False
        
        producto_data = {
            'postgres_id': producto.codigo,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'precio': producto.precio,
            'ubicaciones': []
        }
        
        stock_total = 0
        for ubicacion in producto.ubicaciones.all():
            stock_total += ubicacion.stock
            
            producto_data['ubicaciones'].append({
                'id': ubicacion.id,
                'bodega_codigo': ubicacion.estanteria.bodega.codigo,
                'bodega_ciudad': ubicacion.estanteria.bodega.ciudad,
                'bodega_direccion': ubicacion.estanteria.bodega.direccion,
                'estanteria_zona': ubicacion.estanteria.zona,
                'estanteria_codigo': ubicacion.estanteria.codigo,
                'nivel': ubicacion.nivel,
                'codigo': ubicacion.codigo,
                'codigo_completo': f"{ubicacion.estanteria.zona}{ubicacion.estanteria.codigo}{ubicacion.nivel}{ubicacion.codigo}",
                'capacidad': ubicacion.capacidad,
                'stock': ubicacion.stock,
                'fecha_actualizacion': ubicacion.fecha_actualizacion.isoformat()
            })
        
        producto_data['stock_total'] = stock_total
        producto_data['num_ubicaciones'] = len(producto_data['ubicaciones'])
        producto_data['sync_timestamp'] = datetime.now().isoformat()
        
        result = db.productos.update_one(
            {'codigo': producto.codigo},
            {'$set': producto_data},
            upsert=True
        )
        
        logger.info(f"✅ Producto {producto.codigo} sincronizado a MongoDB")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error sincronizando producto {producto.codigo}: {e}")
        return False


def delete_producto_from_mongo(codigo):
    """
    Elimina un producto de MongoDB.
    """
    try:
        db = get_mongo_db()
        if not db:
            return False
        
        result = db.productos.delete_one({'codigo': codigo})
        logger.info(f"✅ Producto {codigo} eliminado de MongoDB")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error eliminando producto {codigo}: {e}")
        return False


def sync_bodega_to_mongo(bodega):
    """
    Sincroniza una bodega a MongoDB con sus estanterías y ubicaciones.
    """
    try:
        db = get_mongo_db()
        if not db:
            logger.warning(f"MongoDB no disponible, no se sincronizó bodega {bodega.codigo}")
            return False
        
        bodega_data = {
            'postgres_id': bodega.codigo,
            'codigo': bodega.codigo,
            'ciudad': bodega.ciudad,
            'direccion': bodega.direccion,
            'estanterias': []
        }
        
        total_ubicaciones = 0
        total_stock = 0
        
        for estanteria in bodega.estanterias.all():
            est_data = {
                'zona': estanteria.zona,
                'codigo': estanteria.codigo,
                'niveles': estanteria.niveles,
                'ubicaciones': []
            }
            
            for ubicacion in estanteria.ubicaciones.all():
                total_ubicaciones += 1
                total_stock += ubicacion.stock
                
                ub_data = {
                    'id': ubicacion.id,
                    'nivel': ubicacion.nivel,
                    'codigo': ubicacion.codigo,
                    'capacidad': ubicacion.capacidad,
                    'stock': ubicacion.stock,
                    'fecha_actualizacion': ubicacion.fecha_actualizacion.isoformat()
                }
                
                if ubicacion.producto:
                    ub_data['producto'] = {
                        'codigo': ubicacion.producto.codigo,
                        'nombre': ubicacion.producto.nombre,
                        'precio': ubicacion.producto.precio
                    }
                
                est_data['ubicaciones'].append(ub_data)
            
            bodega_data['estanterias'].append(est_data)
        
        bodega_data['total_ubicaciones'] = total_ubicaciones
        bodega_data['total_stock'] = total_stock
        bodega_data['sync_timestamp'] = datetime.now().isoformat()
        
        result = db.bodegas.update_one(
            {'codigo': bodega.codigo},
            {'$set': bodega_data},
            upsert=True
        )
        
        logger.info(f"✅ Bodega {bodega.codigo} sincronizada a MongoDB")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error sincronizando bodega {bodega.codigo}: {e}")
        return False


def test_connection():
    """
    Prueba la conexión a MongoDB.
    """
    try:
        db = get_mongo_db()
        if db:
            stats = db.command('dbstats')
            print(f"✅ Conexión exitosa a MongoDB")
            print(f"   Base de datos: {stats['db']}")
            print(f"   Colecciones: {stats['collections']}")
            return True
        else:
            print("❌ No se pudo conectar a MongoDB")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False