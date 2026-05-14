# tests/test_api.py
def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_capabilities(client):
    response = client.get('/capabilities')
    assert response.status_code == 200