import requests

host = 'localhost'
port = '8001'

def get_pedidos():
    return requests.get(f"http://{host}:{port}/pedidos/").json()

def get_pedido_by_id(id):
    return requests.get(f"http://{host}:{port}/pedidos/{id}/").json()
