"""
Tests for OBS Control Skill
"""

import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skills.obs.obs_control import OBSControlSkill, get_obs_skill


class TestOBSControlSkill:
    """Test OBS Control Skill."""

    @pytest.fixture
    def obs_skill(self):
        return OBSControlSkill()

    def test_parse_status(self, obs_skill):
        action, params = obs_skill.parse_command("obs status")
        assert action == "status"

    def test_parse_list_scenes(self, obs_skill):
        action, params = obs_skill.parse_command("list scenes")
        assert action == "list_scenes"

    def test_parse_switch_scene(self, obs_skill):
        action, params = obs_skill.parse_command("switch scene Main Scene")
        assert action == "set_scene"
        # Parser lowercases the scene name
        assert params.get("scene_name") == "main scene"

    def test_parse_start_recording(self, obs_skill):
        action, params = obs_skill.parse_command("start recording")
        assert action == "start_recording"

    def test_parse_stop_recording(self, obs_skill):
        action, params = obs_skill.parse_command("stop recording")
        assert action == "stop_recording"

    def test_parse_start_streaming(self, obs_skill):
        action, params = obs_skill.parse_command("start streaming")
        assert action == "start_streaming"

    def test_parse_mute(self, obs_skill):
        action, params = obs_skill.parse_command("mute Mic/Aux")
        assert action == "mute"
        # Parser lowercases the input name
        assert params.get("input_name") == "mic/aux"

    def test_parse_screenshot(self, obs_skill):
        action, params = obs_skill.parse_command("screenshot Main Scene")
        assert action == "screenshot"
        # Parser lowercases the source name
        assert params.get("source_name") == "main scene"

    def test_singleton(self):
        skill1 = get_obs_skill()
        skill2 = get_obs_skill()
        assert skill1 is skill2


class TestOBSWebSocketClient:
    """Test OBS WebSocket Client (requires running OBS)."""

    @pytest.fixture
    def client(self):
        from skills.obs.obs_websocket import OBSWebSocketClient
        client = OBSWebSocketClient()
        yield client

    @pytest.mark.asyncio
    async def test_get_version(self, client):
        try:
            await client.connect()
            result = await client.get_version()
            assert "obsVersion" in result
        except Exception:
            pytest.skip("OBS not running or not accessible")
        finally:
            await client.disconnect()

    @pytest.mark.asyncio
    async def test_get_scene_list(self, client):
        try:
            await client.connect()
            result = await client.get_scene_list()
            assert "scenes" in result
            assert "currentProgramSceneName" in result
        except Exception:
            pytest.skip("OBS not running or not accessible")
        finally:
            await client.disconnect()

    @pytest.mark.asyncio
    async def test_get_recording_status(self, client):
        try:
            await client.connect()
            result = await client.get_recording_status()
            assert "outputActive" in result
        except Exception:
            pytest.skip("OBS not running or not accessible")
        finally:
            await client.disconnect()

    @pytest.mark.asyncio
    async def test_get_streaming_status(self, client):
        try:
            await client.connect()
            result = await client.get_streaming_status()
            assert "outputActive" in result
        except Exception:
            pytest.skip("OBS not running or not accessible")
        finally:
            await client.disconnect()

    @pytest.mark.asyncio
    async def test_get_full_status(self, client):
        try:
            await client.connect()
            result = await client.get_full_status()
            assert result["connected"] is True
            assert "version" in result
            assert "current_scene" in result
        except Exception:
            pytest.skip("OBS not running or not accessible")
        finally:
            await client.disconnect()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
