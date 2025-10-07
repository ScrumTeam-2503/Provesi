import requests

host = 'localhost'
port = '8002'

session = requests.Session()

def get_productos():
    return session.get(f"http://{host}:{port}/productos/").json()

def get_producto_by_codigo(codigo):
    print(codigo)
    return session.get(f"http://{host}:{port}/productos/{codigo}/").json()
