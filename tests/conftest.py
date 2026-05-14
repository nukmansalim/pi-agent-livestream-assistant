
# pyrefly: ignore [missing-import]
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import pi_agent_rest_api
from pi_agent_rest_api import app as flask_app


def _make_mock_agent():
    """Build a fully-mocked PiAgent that always returns success."""

    def livestream_side_effect(context, **kwargs):
        action = kwargs.get("action", "unknown")
        return {
            "success": True,
            "message": f"Livestream {action} berhasil dijalankan",
            "broadcast_id": kwargs.get("broadcast_id", "fake_bc_123456789"),
            "rtmp_url": "rtmp://a.rtmp.youtube.com/live2/fakekey",
        }

    mock_livestream_skill = MagicMock()
    mock_livestream_skill.execute = AsyncMock(side_effect=livestream_side_effect)

    mock_agent = MagicMock()
    mock_agent.skills = {"youtube_livestream": mock_livestream_skill}
    mock_agent.get_context = MagicMock(return_value=MagicMock())
    mock_agent.execute = AsyncMock(return_value={
        "success": True,
        "message": "Command executed successfully",
        "result": {},
    })
    return mock_agent


@pytest.fixture(scope="session", autouse=True)
def disable_real_services():
    """
    Disable real OAuth, YouTube API, and external calls for all tests.

    KEY FIX: patch `pi_agent_rest_api.agent` directly.
    The module-level `agent = get_pi_agent()` runs at import time, so patching
    the factory function `get_pi_agent` is too late — the object is already stored.
    Replacing `pi_agent_rest_api.agent` is the only way to make the endpoints
    use the mock.
    """
    print("🔒 [TEST] Real OAuth, YouTube, and external services disabled")

    patches = []

    # OAuth Mocks
    p1 = patch("skills.youtube.youtube_auth.get_auth_url")
    p1.start().return_value = ("https://fake-auth-url.com", "test-state", None)
    patches.append(p1)

    p2 = patch("skills.youtube.youtube_auth.save_credentials_from_code")
    p2.start().return_value = True
    patches.append(p2)

    p3 = patch("skills.youtube.youtube_auth.get_authenticated_service",
               return_value=MagicMock())
    p3.start()
    patches.append(p3)

    # ✅ Replace the already-instantiated agent object in the REST API module
    mock_agent = _make_mock_agent()
    p4 = patch.object(pi_agent_rest_api, "agent", mock_agent)
    p4.start()
    patches.append(p4)

    yield

    for p in patches:
        p.stop()


@pytest.fixture(scope="session")
def app():
    """Flask app for testing"""
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key-pi-agent-livestream",
        "DEBUG": False,
        "GOOGLE_OAUTH_DISABLED": True,
    })
    return flask_app


@pytest.fixture(scope="function")
def client(app):
    """Flask test client"""
    return app.test_client()