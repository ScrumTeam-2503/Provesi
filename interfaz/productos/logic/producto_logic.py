import requests

host = 'localhost'
port = '8002'

def get_productos():
    return requests.get(f"http://{host}:{port}/productos/").json()

def get_producto_by_codigo(codigo):
    print(codigo)
    return requests.get(f"http://{host}:{port}/productos/{codigo}/").json()
