import requests

base_url = 'http://localhost:8001/'

def get_pedidos():
    return requests.get(base_url + 'pedidos/')