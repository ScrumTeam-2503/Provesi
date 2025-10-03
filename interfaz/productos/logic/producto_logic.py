import requests

base_url = 'http://localhost:8002/'

def get_productos():
    return requests.get(base_url + 'productos/')