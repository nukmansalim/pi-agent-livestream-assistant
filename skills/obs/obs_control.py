"""
skills/obs/obs_control.py
High-level OBS Control Skill for Pi Agent.
Wraps OBS WebSocket client with natural language command parsing.
"""

import os
import re
from typing import Dict, Any, Optional
from .obs_websocket import OBSWebSocketClient


class OBSControlSkill:
    """High-level OBS control skill."""

    def __init__(self):
        self.host = os.getenv("OBS_HOST", "localhost")
        self.port = int(os.getenv("OBS_PORT", "4455"))
        self.password = os.getenv("OBS_PASSWORD", "")
        self.client: Optional[OBSWebSocketClient] = None


    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute OBS action with parameters."""
        client = None
        try:
            client = OBSWebSocketClient(self.host, self.port, self.password)
            await client.connect()
            result = await self._execute_action(client, action, **kwargs)
            await client.disconnect()
            return {"success": True, **result}
        except Exception as e:
            if client:
                try:
                    await client.disconnect()
                except Exception:
                    pass
            return {"success": False, "error": str(e)}

    async def _execute_action(self, client: OBSWebSocketClient, action: str, **kwargs) -> Dict[str, Any]:
        """Route action to specific method."""
        action = action.lower().replace(" ", "_")

        # ==================== STATUS ====================
        if action in ["status", "get_status", "obs_status"]:
            status = await client.get_full_status()
            return {"status": status}

        if action in ["version", "get_version"]:
            return await client.get_version()

        if action in ["stats", "get_stats"]:
            return await client.get_stats()

        # ==================== SCENES ====================
        if action in ["list_scenes", "scenes", "get_scenes"]:
            result = await client.get_scene_list()
            return {
                "current_scene": result.get("currentProgramSceneName"),
                "scenes": [s.get("sceneName", "") for s in result.get("scenes", [])]
            }

        if action in ["set_scene", "switch_scene", "change_scene"]:
            scene_name = kwargs.get("scene_name") or kwargs.get("scene")
            if not scene_name:
                return {"error": "scene_name required"}
            await client.set_current_scene(scene_name)
            return {"message": f"Switched to scene: {scene_name}"}

        if action in ["create_scene", "add_scene"]:
            scene_name = kwargs.get("scene_name") or kwargs.get("scene")
            if not scene_name:
                return {"error": "scene_name required"}
            await client.create_scene(scene_name)
            return {"message": f"Created scene: {scene_name}"}

        if action in ["remove_scene", "delete_scene"]:
            scene_name = kwargs.get("scene_name") or kwargs.get("scene")
            if not scene_name:
                return {"error": "scene_name required"}
            await client.remove_scene(scene_name)
            return {"message": f"Removed scene: {scene_name}"}

        # ==================== RECORDING ====================
        if action in ["start_recording", "record_start", "start_record"]:
            await client.start_recording()
            return {"message": "Recording started"}

        if action in ["stop_recording", "record_stop", "stop_record"]:
            result = await client.stop_recording()
            return {"message": "Recording stopped", "output_path": result.get("outputPath", "")}

        if action in ["pause_recording", "record_pause"]:
            await client.pause_recording()
            return {"message": "Recording paused"}

        if action in ["resume_recording", "record_resume"]:
            await client.resume_recording()
            return {"message": "Recording resumed"}

        if action in ["recording_status", "get_recording_status"]:
            result = await client.get_recording_status()
            return {
                "active": result.get("outputActive", False),
                "paused": result.get("outputPaused", False),
                "timecode": result.get("outputTimecode", "")
            }

        # ==================== STREAMING ====================
        if action in ["start_streaming", "stream_start", "start_stream"]:
            await client.start_streaming()
            return {"message": "Streaming started"}

        if action in ["stop_streaming", "stream_stop", "stop_stream"]:
            await client.stop_streaming()
            return {"message": "Streaming stopped"}

        if action in ["streaming_status", "get_streaming_status"]:
            result = await client.get_streaming_status()
            return {
                "active": result.get("outputActive", False),
                "reconnecting": result.get("outputReconnecting", False),
                "timecode": result.get("outputTimecode", "")
            }

        if action in ["toggle_streaming", "stream_toggle"]:
            result = await client.toggle_streaming()
            return {"message": "Streaming toggled", "result": result}

        if action in ["send_caption", "stream_caption"]:
            caption = kwargs.get("caption") or kwargs.get("text", "")
            if not caption:
                return {"error": "caption text required"}
            await client.send_stream_caption(caption)
            return {"message": f"Caption sent: {caption}"}

        # ==================== VIRTUAL CAMERA ====================
        if action in ["start_virtual_cam", "virtual_cam_start"]:
            await client.start_virtual_cam()
            return {"message": "Virtual camera started"}

        if action in ["stop_virtual_cam", "virtual_cam_stop"]:
            await client.stop_virtual_cam()
            return {"message": "Virtual camera stopped"}

        if action in ["toggle_virtual_cam", "virtual_cam_toggle"]:
            result = await client.toggle_virtual_cam()
            return {"message": "Virtual camera toggled", "result": result}

        if action in ["virtual_cam_status", "get_virtual_cam_status"]:
            result = await client.get_virtual_cam_status()
            return {"active": result.get("outputActive", False)}

        # ==================== REPLAY BUFFER ====================
        if action in ["start_replay_buffer", "replay_buffer_start"]:
            await client.start_replay_buffer()
            return {"message": "Replay buffer started"}

        if action in ["stop_replay_buffer", "replay_buffer_stop"]:
            await client.stop_replay_buffer()
            return {"message": "Replay buffer stopped"}

        if action in ["save_replay", "save_replay_buffer"]:
            await client.save_replay_buffer()
            return {"message": "Replay saved"}

        if action in ["toggle_replay_buffer", "replay_buffer_toggle"]:
            result = await client.toggle_replay_buffer()
            return {"message": "Replay buffer toggled", "result": result}

        if action in ["replay_buffer_status", "get_replay_buffer_status"]:
            result = await client.get_replay_buffer_status()
            return {"active": result.get("outputActive", False)}

        if action in ["last_replay", "get_last_replay"]:
            result = await client.get_last_replay_buffer_replay()
            return {"path": result.get("savedReplayPath", "")}

        # ==================== STUDIO MODE ====================
        if action in ["enable_studio_mode", "studio_mode_on"]:
            await client.set_studio_mode_enabled(True)
            return {"message": "Studio mode enabled"}

        if action in ["disable_studio_mode", "studio_mode_off"]:
            await client.set_studio_mode_enabled(False)
            return {"message": "Studio mode disabled"}

        if action in ["toggle_studio_mode", "studio_mode_toggle"]:
            result = await client.toggle_studio_mode()
            return {"message": "Studio mode toggled", "result": result}

        if action in ["get_preview_scene", "preview_scene"]:
            result = await client.get_preview_scene()
            return {"preview_scene": result.get("currentPreviewSceneName", "")}

        if action in ["set_preview_scene"]:
            scene_name = kwargs.get("scene_name") or kwargs.get("scene")
            if not scene_name:
                return {"error": "scene_name required"}
            await client.set_preview_scene(scene_name)
            return {"message": f"Preview scene set to: {scene_name}"}

        if action in ["trigger_transition", "transition"]:
            await client.trigger_studio_mode_transition()
            return {"message": "Transition triggered"}

        # ==================== SOURCES ====================
        if action in ["list_sources", "sources", "get_sources"]:
            result = await client.get_input_list()
            return {
                "sources": [
                    {
                        "name": s.get("inputName", ""),
                        "kind": s.get("inputKind", ""),
                        "kind_display": s.get("unversionedInputKind", "")
                    }
                    for s in result.get("inputs", [])
                ]
            }

        if action in ["list_scene_items", "scene_items", "get_scene_items"]:
            scene_name = kwargs.get("scene_name") or kwargs.get("scene")
            if not scene_name:
                return {"error": "scene_name required"}
            result = await client.get_scene_item_list(scene_name)
            return {
                "scene": scene_name,
                "items": [
                    {
                        "id": item.get("sceneItemId"),
                        "name": item.get("sourceName", ""),
                        "enabled": item.get("sceneItemEnabled", True)
                    }
                    for item in result.get("sceneItems", [])
                ]
            }

        if action in ["show_source", "enable_source"]:
            scene_name = kwargs.get("scene_name") or kwargs.get("scene")
            source_name = kwargs.get("source_name") or kwargs.get("source")
            if not scene_name or not source_name:
                return {"error": "scene_name and source_name required"}
            success = await client.set_source_visibility(scene_name, source_name, True)
            return {"message": f"Source '{source_name}' shown in '{scene_name}'" if success else f"Source not found"}

        if action in ["hide_source", "disable_source"]:
            scene_name = kwargs.get("scene_name") or kwargs.get("scene")
            source_name = kwargs.get("source_name") or kwargs.get("source")
            if not scene_name or not source_name:
                return {"error": "scene_name and source_name required"}
            success = await client.set_source_visibility(scene_name, source_name, False)
            return {"message": f"Source '{source_name}' hidden in '{scene_name}'" if success else f"Source not found"}

        if action in ["toggle_source", "toggle_source_visibility"]:
            scene_name = kwargs.get("scene_name") or kwargs.get("scene")
            source_name = kwargs.get("source_name") or kwargs.get("source")
            if not scene_name or not source_name:
                return {"error": "scene_name and source_name required"}
            item_id = await client.find_scene_item_by_name(scene_name, source_name)
            if item_id is None:
                return {"error": f"Source '{source_name}' not found in scene '{scene_name}'"}
            new_state = await client.toggle_scene_item_enabled(scene_name, item_id)
            return {"message": f"Source '{source_name}' is now {'visible' if new_state else 'hidden'}"}

        if action in ["create_input", "add_source", "create_source"]:
            scene_name = kwargs.get("scene_name") or kwargs.get("scene")
            input_name = kwargs.get("input_name") or kwargs.get("source_name") or kwargs.get("name")
            input_kind = kwargs.get("input_kind") or kwargs.get("kind", "text_gdiplus_v2")
            settings = kwargs.get("settings", {})
            if not scene_name or not input_name:
                return {"error": "scene_name and input_name required"}
            result = await client.create_input(scene_name, input_name, input_kind, settings)
            return {"message": f"Created input '{input_name}' in '{scene_name}'", "scene_item_id": result.get("sceneItemId")}

        if action in ["remove_input", "remove_source", "delete_source"]:
            input_name = kwargs.get("input_name") or kwargs.get("source_name") or kwargs.get("name")
            if not input_name:
                return {"error": "input_name required"}
            await client.remove_input(input_name)
            return {"message": f"Removed input '{input_name}'"}

        if action in ["get_input_settings", "source_settings"]:
            input_name = kwargs.get("input_name") or kwargs.get("source_name") or kwargs.get("name")
            if not input_name:
                return {"error": "input_name required"}
            result = await client.get_input_settings(input_name)
            return {"input_name": input_name, "settings": result.get("inputSettings", {})}

        if action in ["set_input_settings", "update_source_settings"]:
            input_name = kwargs.get("input_name") or kwargs.get("source_name") or kwargs.get("name")
            settings = kwargs.get("settings", {})
            if not input_name:
                return {"error": "input_name required"}
            await client.set_input_settings(input_name, settings)
            return {"message": f"Updated settings for '{input_name}'"}

        if action in ["list_input_kinds", "input_kinds", "source_types"]:
            result = await client.get_input_kind_list()
            return {"input_kinds": result.get("inputKinds", [])}

        if action in ["set_source_transform", "transform_source"]:
            scene_name = kwargs.get("scene_name") or kwargs.get("scene")
            source_name = kwargs.get("source_name") or kwargs.get("source")
            transform = kwargs.get("transform", {})
            if not scene_name or not source_name:
                return {"error": "scene_name and source_name required"}
            if not transform:
                return {"error": "transform object required"}
            item_id = await client.find_scene_item_by_name(scene_name, source_name)
            if item_id is None:
                return {"error": f"Source '{source_name}' not found in scene '{scene_name}'"}
            await client.set_scene_item_transform(scene_name, item_id, transform)
            return {"message": f"Transform updated for '{source_name}' in '{scene_name}'"}

        if action in ["get_source_transform"]:
            scene_name = kwargs.get("scene_name") or kwargs.get("scene")
            source_name = kwargs.get("source_name") or kwargs.get("source")
            if not scene_name or not source_name:
                return {"error": "scene_name and source_name required"}
            item_id = await client.find_scene_item_by_name(scene_name, source_name)
            if item_id is None:
                return {"error": f"Source '{source_name}' not found in scene '{scene_name}'"}
            result = await client.get_scene_item_transform(scene_name, item_id)
            return {"source": source_name, "transform": result.get("sceneItemTransform", {})}

        # ==================== AUDIO ====================
        if action in ["mute", "mute_input"]:
            input_name = kwargs.get("input_name") or kwargs.get("source")
            if not input_name:
                return {"error": "input_name required"}
            await client.set_input_mute(input_name, True)
            return {"message": f"Muted '{input_name}'"}

        if action in ["unmute", "unmute_input"]:
            input_name = kwargs.get("input_name") or kwargs.get("source")
            if not input_name:
                return {"error": "input_name required"}
            await client.set_input_mute(input_name, False)
            return {"message": f"Unmuted '{input_name}'"}

        if action in ["toggle_mute", "toggle_input_mute"]:
            input_name = kwargs.get("input_name") or kwargs.get("source")
            if not input_name:
                return {"error": "input_name required"}
            result = await client.toggle_input_mute(input_name)
            return {"message": f"Toggled mute for '{input_name}'", "result": result}

        if action in ["get_volume", "volume"]:
            input_name = kwargs.get("input_name") or kwargs.get("source")
            if not input_name:
                return {"error": "input_name required"}
            result = await client.get_input_volume(input_name)
            return {
                "input_name": input_name,
                "volume_db": result.get("inputVolumeDb", 0),
                "volume_mul": result.get("inputVolumeMul", 0)
            }

        if action in ["set_volume", "volume_set"]:
            input_name = kwargs.get("input_name") or kwargs.get("source")
            volume_db = kwargs.get("volume_db")
            volume_mul = kwargs.get("volume_mul")
            if not input_name:
                return {"error": "input_name required"}
            if volume_db is None and volume_mul is None:
                return {"error": "volume_db or volume_mul required"}
            await client.set_input_volume(input_name, volume_db, volume_mul)
            return {"message": f"Volume set for '{input_name}'"}

        # ==================== TRANSITIONS ====================
        if action in ["list_transitions", "transitions"]:
            result = await client.get_scene_transition_list()
            return {
                "current": result.get("currentSceneTransitionName", ""),
                "transitions": [t.get("transitionName", "") for t in result.get("transitions", [])]
            }

        if action in ["set_transition"]:
            transition_name = kwargs.get("transition_name") or kwargs.get("transition")
            if not transition_name:
                return {"error": "transition_name required"}
            await client.set_current_scene_transition(transition_name)
            return {"message": f"Transition set to: {transition_name}"}

        if action in ["set_transition_duration", "transition_duration"]:
            duration = kwargs.get("duration") or kwargs.get("duration_ms", 300)
            await client.set_current_scene_transition_duration(int(duration))
            return {"message": f"Transition duration set to {duration}ms"}

        # ==================== PROFILES & COLLECTIONS ====================
        if action in ["list_profiles", "profiles"]:
            result = await client.get_profile_list()
            return {
                "current": result.get("currentProfileName", ""),
                "profiles": result.get("profiles", [])
            }

        if action in ["set_profile"]:
            profile_name = kwargs.get("profile_name") or kwargs.get("profile")
            if not profile_name:
                return {"error": "profile_name required"}
            await client.set_current_profile(profile_name)
            return {"message": f"Profile set to: {profile_name}"}

        if action in ["list_scene_collections", "scene_collections"]:
            result = await client.get_scene_collection_list()
            return {
                "current": result.get("currentSceneCollectionName", ""),
                "collections": result.get("sceneCollections", [])
            }

        if action in ["set_scene_collection"]:
            collection_name = kwargs.get("collection_name") or kwargs.get("collection")
            if not collection_name:
                return {"error": "collection_name required"}
            await client.set_current_scene_collection(collection_name)
            return {"message": f"Scene collection set to: {collection_name}"}

        # ==================== SCREENSHOTS ====================
        if action in ["screenshot", "get_screenshot"]:
            source_name = kwargs.get("source_name") or kwargs.get("source")
            if not source_name:
                return {"error": "source_name required"}
            result = await client.get_source_screenshot(source_name)
            return {"image_data": result.get("imageData", "")}

        if action in ["save_screenshot"]:
            source_name = kwargs.get("source_name") or kwargs.get("source")
            file_path = kwargs.get("file_path") or kwargs.get("path")
            if not source_name or not file_path:
                return {"error": "source_name and file_path required"}
            await client.save_source_screenshot(source_name, file_path)
            return {"message": f"Screenshot saved to: {file_path}"}

        # ==================== HOTKEYS ====================
        if action in ["list_hotkeys", "hotkeys"]:
            result = await client.get_hotkey_list()
            return {"hotkeys": result.get("hotkeys", [])}

        if action in ["trigger_hotkey", "press_hotkey"]:
            hotkey_name = kwargs.get("hotkey_name") or kwargs.get("hotkey")
            if not hotkey_name:
                return {"error": "hotkey_name required"}
            await client.trigger_hotkey_by_name(hotkey_name)
            return {"message": f"Hotkey triggered: {hotkey_name}"}

        # ==================== FILTERS ====================
        if action in ["list_filters", "source_filters"]:
            source_name = kwargs.get("source_name") or kwargs.get("source")
            if not source_name:
                return {"error": "source_name required"}
            result = await client.get_source_filter_list(source_name)
            return {
                "source": source_name,
                "filters": [
                    {
                        "name": f.get("filterName", ""),
                        "kind": f.get("filterKind", ""),
                        "enabled": f.get("filterEnabled", True)
                    }
                    for f in result.get("filters", [])
                ]
            }

        if action in ["toggle_filter"]:
            source_name = kwargs.get("source_name") or kwargs.get("source")
            filter_name = kwargs.get("filter_name") or kwargs.get("filter")
            enabled = kwargs.get("enabled")
            if not source_name or not filter_name:
                return {"error": "source_name and filter_name required"}
            if enabled is None:
                # Toggle
                current = await client.get_source_filter(source_name, filter_name)
                enabled = not current.get("filterEnabled", True)
            await client.set_source_filter_enabled(source_name, filter_name, enabled)
            return {"message": f"Filter '{filter_name}' on '{source_name}' is now {'enabled' if enabled else 'disabled'}"}

        if action in ["create_filter", "add_filter"]:
            source_name = kwargs.get("source_name") or kwargs.get("source")
            filter_name = kwargs.get("filter_name") or kwargs.get("filter")
            filter_kind = kwargs.get("filter_kind") or kwargs.get("kind", "color_correction_filter")
            settings = kwargs.get("settings", {})
            if not source_name or not filter_name:
                return {"error": "source_name and filter_name required"}
            await client.create_source_filter(source_name, filter_name, filter_kind, settings)
            return {"message": f"Created filter '{filter_name}' on '{source_name}'"}

        if action in ["remove_filter", "delete_filter"]:
            source_name = kwargs.get("source_name") or kwargs.get("source")
            filter_name = kwargs.get("filter_name") or kwargs.get("filter")
            if not source_name or not filter_name:
                return {"error": "source_name and filter_name required"}
            await client.remove_source_filter(source_name, filter_name)
            return {"message": f"Removed filter '{filter_name}' from '{source_name}'"}

        # ==================== BROWSER SOURCE ====================
        if action in ["refresh_browser", "reload_browser"]:
            source_name = kwargs.get("source_name") or kwargs.get("source")
            if not source_name:
                return {"error": "source_name required"}
            await client.refresh_browser_source(source_name)
            return {"message": f"Browser source '{source_name}' refreshed"}

        # ==================== STREAM SERVICE ====================
        if action in ["get_stream_settings", "stream_settings"]:
            result = await client.get_stream_service_settings()
            return {
                "service_type": result.get("streamServiceType", ""),
                "settings": result.get("streamServiceSettings", {})
            }

        if action in ["set_stream_settings", "update_stream_settings"]:
            service_type = kwargs.get("service_type") or kwargs.get("service", "rtmp_custom")
            settings = kwargs.get("settings", {})
            await client.set_stream_service_settings(service_type, settings)
            return {"message": f"Stream service set to: {service_type}"}

        # ==================== MEDIA SOURCE ====================
        if action in ["media_status", "get_media_status"]:
            input_name = kwargs.get("input_name") or kwargs.get("source")
            if not input_name:
                return {"error": "input_name required"}
            result = await client.get_media_input_status(input_name)
            return {
                "input_name": input_name,
                "state": result.get("mediaState", ""),
                "duration": result.get("mediaDuration", 0),
                "cursor": result.get("mediaCursor", 0)
            }

        if action in ["media_play", "play_media"]:
            input_name = kwargs.get("input_name") or kwargs.get("source")
            if not input_name:
                return {"error": "input_name required"}
            await client.trigger_media_input_action(input_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PLAY")
            return {"message": f"Playing '{input_name}'"}

        if action in ["media_pause", "pause_media"]:
            input_name = kwargs.get("input_name") or kwargs.get("source")
            if not input_name:
                return {"error": "input_name required"}
            await client.trigger_media_input_action(input_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PAUSE")
            return {"message": f"Paused '{input_name}'"}

        if action in ["media_restart", "restart_media"]:
            input_name = kwargs.get("input_name") or kwargs.get("source")
            if not input_name:
                return {"error": "input_name required"}
            await client.trigger_media_input_action(input_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART")
            return {"message": f"Restarted '{input_name}'"}

        if action in ["media_stop", "stop_media"]:
            input_name = kwargs.get("input_name") or kwargs.get("source")
            if not input_name:
                return {"error": "input_name required"}
            await client.trigger_media_input_action(input_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_STOP")
            return {"message": f"Stopped '{input_name}'"}

        if action in ["media_next", "next_media"]:
            input_name = kwargs.get("input_name") or kwargs.get("source")
            if not input_name:
                return {"error": "input_name required"}
            await client.trigger_media_input_action(input_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_NEXT")
            return {"message": f"Next track on '{input_name}'"}

        if action in ["media_previous", "previous_media"]:
            input_name = kwargs.get("input_name") or kwargs.get("source")
            if not input_name:
                return {"error": "input_name required"}
            await client.trigger_media_input_action(input_name, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_PREVIOUS")
            return {"message": f"Previous track on '{input_name}'"}

        # ==================== SPECIAL SOURCES ====================
        if action in ["special_inputs", "get_special_inputs"]:
            result = await client.get_special_inputs()
            return result

        # ==================== UNKNOWN ====================
        return {"error": f"Unknown action: {action}"}

    # ==================== NATURAL LANGUAGE PARSER ====================

    def parse_command(self, command: str) -> tuple:
        """Parse natural language command into action and kwargs."""
        cmd = command.lower().strip()

        # Status
        if any(k in cmd for k in ["obs status", "status obs", "cek obs", "obs info"]):
            return "status", {}

        # Scenes
        if any(k in cmd for k in ["list scene", "daftar scene", "scene list", "lihat scene"]):
            return "list_scenes", {}

        scene_match = re.search(r'(?:switch|change|ganti|pindah)\s+(?:ke\s+)?scene\s+["\']?([^"\']+)["\']?', cmd)
        if scene_match:
            scene_name = scene_match.group(1).strip()
            return "set_scene", {"scene_name": scene_name}

        if re.search(r'(?:buat|create|tambah)\s+scene', cmd):
            scene_match = re.search(r'(?:buat|create|tambah)\s+scene\s+["\']?([^"\']+)["\']?', cmd)
            return "create_scene", {"scene_name": scene_match.group(1).strip() if scene_match else None}

        # Recording
        if any(k in cmd for k in ["start recording", "mulai rekam", "rekam mulai"]):
            return "start_recording", {}
        if any(k in cmd for k in ["stop recording", "henti rekam", "rekam stop", "matikan rekam"]):
            return "stop_recording", {}
        if any(k in cmd for k in ["pause recording", "jeda rekam"]):
            return "pause_recording", {}
        if any(k in cmd for k in ["resume recording", "lanjut rekam"]):
            return "resume_recording", {}
        if any(k in cmd for k in ["recording status", "status rekam"]):
            return "recording_status", {}

        # Streaming
        if any(k in cmd for k in ["start streaming", "mulai stream", "stream mulai"]):
            return "start_streaming", {}
        if any(k in cmd for k in ["stop streaming", "henti stream", "stream stop", "matikan stream"]):
            return "stop_streaming", {}
        if any(k in cmd for k in ["streaming status", "status stream"]):
            return "streaming_status", {}

        # Virtual Cam
        if any(k in cmd for k in ["start virtual cam", "virtual cam on", "nyalakan virtual cam"]):
            return "start_virtual_cam", {}
        if any(k in cmd for k in ["stop virtual cam", "virtual cam off", "matikan virtual cam"]):
            return "stop_virtual_cam", {}

        # Replay Buffer
        if any(k in cmd for k in ["save replay", "simpan replay"]):
            return "save_replay", {}

        # Sources
        if any(k in cmd for k in ["list source", "daftar source", "lihat source"]):
            return "list_sources", {}

        # Show/hide source
        show_match = re.search(r'(?:show|tampilkan|nyalakan)\s+source\s+["\']?([^"\']+?)["\']?\s+(?:in|di)\s+scene\s+["\']?([^"\']+)["\']?', cmd)
        if show_match:
            return "show_source", {"source_name": show_match.group(1).strip(), "scene_name": show_match.group(2).strip()}

        hide_match = re.search(r'(?:hide|sembunyikan|matikan)\s+source\s+["\']?([^"\']+?)["\']?\s+(?:in|di)\s+scene\s+["\']?([^"\']+)["\']?', cmd)
        if hide_match:
            return "hide_source", {"source_name": hide_match.group(1).strip(), "scene_name": hide_match.group(2).strip()}

        # Create source
        create_source_match = re.search(r'(?:create|buat|tambah)\s+source\s+["\']?([^"\']+?)["\']?\s+(?:in|di)\s+scene\s+["\']?([^"\']+)["\']?(?:\s+type\s+["\']?([^"\']+)["\']?)?', cmd)
        if create_source_match:
            return "create_input", {
                "source_name": create_source_match.group(1).strip(),
                "scene_name": create_source_match.group(2).strip(),
                "input_kind": create_source_match.group(3).strip() if create_source_match.group(3) else "text_gdiplus_v2"
            }

        # Remove source
        remove_source_match = re.search(r'(?:remove|delete|hapus)\s+source\s+["\']?([^"\']+?)["\']?\s*$', cmd)
        if remove_source_match:
            return "remove_input", {"input_name": remove_source_match.group(1).strip()}

        # Get source settings
        settings_match = re.search(r'(?:get|lihat)\s+source\s+settings\s+["\']?([^"\']+)["\']?', cmd)
        if settings_match:
            return "get_input_settings", {"input_name": settings_match.group(1).strip()}

        # List input kinds
        if any(k in cmd for k in ["list source types", "source types", "input kinds", "jenis source"]):
            return "list_input_kinds", {}

        # Audio
        mute_match = re.search(r'(?:mute|bisukan)\s+["\']?([^"\']+?)["\']?\s*$', cmd)
        if mute_match:
            return "mute", {"input_name": mute_match.group(1).strip()}

        unmute_match = re.search(r'(?:unmute|nyalakan suara)\s+["\']?([^"\']+?)["\']?\s*$', cmd)
        if unmute_match:
            return "unmute", {"input_name": unmute_match.group(1).strip()}

        volume_match = re.search(r'(?:volume|set volume)\s+["\']?([^"\']+?)["\']?\s+(?:to\s+)?(-?\d+(?:\.\d+)?)', cmd)
        if volume_match:
            return "set_volume", {"input_name": volume_match.group(1).strip(), "volume_db": float(volume_match.group(2))}

        # Transitions
        if any(k in cmd for k in ["list transition", "daftar transition"]):
            return "list_transitions", {}

        # Hotkeys
        hotkey_match = re.search(r'(?:trigger|press|tekan)\s+hotkey\s+["\']?([^"\']+)["\']?', cmd)
        if hotkey_match:
            return "trigger_hotkey", {"hotkey_name": hotkey_match.group(1).strip()}

        # Screenshot
        screenshot_match = re.search(r'(?:screenshot|capture)\s+["\']?([^"\']+)["\']?', cmd)
        if screenshot_match:
            return "screenshot", {"source_name": screenshot_match.group(1).strip()}

        # Browser refresh
        refresh_match = re.search(r'(?:refresh|reload)\s+browser\s+["\']?([^"\']+)["\']?', cmd)
        if refresh_match:
            return "refresh_browser", {"source_name": refresh_match.group(1).strip()}

        # Media source control
        media_play_match = re.search(r'(?:play|mulai)\s+media\s+["\']?([^"\']+)["\']?', cmd)
        if media_play_match:
            return "media_play", {"input_name": media_play_match.group(1).strip()}

        media_pause_match = re.search(r'(?:pause|jeda)\s+media\s+["\']?([^"\']+)["\']?', cmd)
        if media_pause_match:
            return "media_pause", {"input_name": media_pause_match.group(1).strip()}

        media_restart_match = re.search(r'(?:restart|ulang)\s+media\s+["\']?([^"\']+)["\']?', cmd)
        if media_restart_match:
            return "media_restart", {"input_name": media_restart_match.group(1).strip()}

        media_stop_match = re.search(r'(?:stop|henti)\s+media\s+["\']?([^"\']+)["\']?', cmd)
        if media_stop_match:
            return "media_stop", {"input_name": media_stop_match.group(1).strip()}

        media_status_match = re.search(r'(?:status|cek)\s+media\s+["\']?([^"\']+)["\']?', cmd)
        if media_status_match:
            return "media_status", {"input_name": media_status_match.group(1).strip()}

        return "status", {}  # Default to status


# Singleton instance
_obs_skill = None


def get_obs_skill() -> OBSControlSkill:
    """Get singleton OBS control skill instance."""
    global _obs_skill
    if _obs_skill is None:
        _obs_skill = OBSControlSkill()
    return _obs_skill
