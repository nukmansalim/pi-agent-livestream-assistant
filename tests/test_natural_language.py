# tests/test_natural_language.py
# pyrefly: ignore [missing-import]
import pytest

@pytest.mark.parametrize("command", [
    "buat livestream berjudul Pi Agent Live Coding",
    "create live stream title 'Daily Update'",
    "start livestream sekarang",
    "mulai broadcast",
    "akhiri livestream",
    "stop live streaming",
])
def test_execute_livestream_natural_language(client, command):
    """Natural language commands should be routed to the livestream skill via /execute."""
    response = client.post('/execute', json={
        "command": command,
        "user_id": "test_user"
    })

    assert response.status_code == 200
    data = response.json
    assert data["success"] is True


def test_full_livestream_flow_with_natural_language(client):
    """Simulate real user flow: create → start (with id) → end (with id)"""
    # Step 1: Create the livestream via NLP
    r1 = client.post('/execute', json={
        "command": "buat livestream judul 'Test Live Session'",
        "user_id": "test_user"
    })
    assert r1.json["success"] is True
    broadcast_id = r1.json.get("broadcast_id", "fake_bc_123456789")

    # Step 2: Start it via direct endpoint with the broadcast_id
    r2 = client.post('/livestream/start', json={
        "broadcast_id": broadcast_id,
        "user_id": "test_user"
    })
    assert r2.json["success"] is True

    # Step 3: End it via direct endpoint
    r3 = client.post('/livestream/end', json={
        "broadcast_id": broadcast_id,
        "user_id": "test_user"
    })
    assert r3.json["success"] is True