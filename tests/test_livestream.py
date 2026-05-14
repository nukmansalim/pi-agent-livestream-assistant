# tests/test_livestream.py
# pyrefly: ignore [missing-import]
import pytest

def test_create_livestream(client):
    response = client.post('/livestream/create', json={
        "title": "Pi Agent Livestream Test",
        "description": "Testing automated livestream with natural language",
        "privacy": "public"
    })
    assert response.status_code == 200
    data = response.json
    assert data["success"] is True
    assert "broadcast_id" in data


def test_start_livestream(client):
    response = client.post('/livestream/start', json={
        "broadcast_id": "fake_bc_123456789"
    })
    assert response.status_code == 200
    assert response.json["success"] is True


def test_end_livestream(client):
    response = client.post('/livestream/end', json={
        "broadcast_id": "fake_bc_123456789"
    })
    assert response.status_code == 200
    assert response.json["success"] is True