import requests

host = 'localhost'
port = '8001'

session = requests.Session()

def get_pedidos():
    return session.get(f"http://{host}:{port}/pedidos/").json()

def get_pedido_by_id(id):
    return session.get(f"http://{host}:{port}/pedidos/{id}/").json()
