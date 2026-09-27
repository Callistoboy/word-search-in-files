#
# Здесь проводятся тесты API
#

from fastapi.testclient import TestClient

from config import WEB_HOST, WEB_PORT
from main import app

client = TestClient(app)


def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == f"Server has started. To work with search logic try sending HTTP/1.1 GET http://{WEB_HOST}:{WEB_PORT}/files/search"


def test_read_key():
    response = client.get("/files/search")
    assert response.status_code == 200
    assert response.json() == f'To use the search logic, send HTTP/1.1 GET request with param "keyword", like http://{WEB_HOST}:{WEB_PORT}/files/search?keyword=helloworld'


def test_read_key_with_param():
    response = client.get("/files/search?keyword=test")
    assert response.status_code == 200
    assert response.json() == '[]'


def test_read_key_with_real_param_1():
    response = client.get("/files/search?keyword=свет")
    assert response.status_code == 200
    assert response.json() == '["file1.txt"]'


def test_read_key_with_real_param_2():
    response = client.get("/files/search?keyword=вы")
    assert response.status_code == 200
    assert response.json() == '["file3.txt"]'


def test_read_key_with_real_param_3():
    response = client.get("/files/search?keyword=")
    assert response.status_code == 200
    assert response.json() == f'To use the search logic, send HTTP/1.1 GET request with param "keyword", like http://{WEB_HOST}:{WEB_PORT}/files/search?keyword=helloworld'


def test_read_key_with_real_param_and_regular_search():
    response = client.get("/files/search?keyword=вы&regular_search=true")
    assert response.status_code == 200
    assert response.json() == '["file3.txt"]'
