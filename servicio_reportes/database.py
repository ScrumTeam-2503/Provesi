"""
Configuración de conexiones a bases de datos
"""
import os
import psycopg2
import pymongo
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)


def get_postgres_connection():
    """
    Obtiene una conexión a PostgreSQL
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("DATABASE_HOST", "34.229.88.183"),
            database=os.getenv("DATABASE_NAME", "provesi_db"),
            user=os.getenv("DATABASE_USER", "provesi_user"),
            password=os.getenv("DATABASE_PASSWORD", "scrumteam"),
            port=os.getenv("DATABASE_PORT", "5432")
        )
        logger.info("✅ Conectado a PostgreSQL")
        return conn
    except Exception as e:
        logger.error(f"❌ Error conectando a PostgreSQL: {e}")
        raise


def get_mongo_db():
    """
    Obtiene conexión a MongoDB
    """
    try:
        config = {
            'host': os.getenv("MONGODB_HOST", "localhost"),
            'port': int(os.getenv("MONGODB_PORT", "27017")),
            'database': os.getenv("MONGODB_DATABASE", "provesi_mongodb"),
            'username': os.getenv("MONGODB_USER", "provesi_user"),
            'password': os.getenv("MONGODB_PASSWORD", "scrumteam"),
            'authSource': os.getenv("MONGODB_AUTH_SOURCE", "provesi_mongodb"),
        }
        
        client = MongoClient(
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
        raise

