"""
skills/obs/obs_websocket.py
Low-level OBS WebSocket client for Python.
Communicates directly with OBS Studio WebSocket server (default port 4455).
"""

import json
import asyncio
import websockets
from typing import Optional, Dict, Any


class OBSWebSocketClient:
    """Async OBS WebSocket client."""

    def __init__(self, host: str = "localhost", port: int = 4455, password: str = ""):
        self.host = host
        self.port = port
        self.password = password
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self._message_id = 0
        self._connected = False

    @property
    def url(self) -> str:
        return f"ws://{self.host}:{self.port}"

    async def connect(self) -> bool:
        """Connect to OBS WebSocket server."""
        try:
            self.ws = await websockets.connect(self.url)
            # OBS WebSocket v5+ requires hello + identify handshake
            hello = await self.ws.recv()
            hello_data = json.loads(hello)
            
            if hello_data.get("op") == 0:  # Hello
                auth_required = hello_data["d"]["authentication"].get("challenge") is not None
                
                identify_payload = {
                    "op": 1,
                    "d": {
                        "rpcVersion": 1,
                        "eventSubscriptions": 33  # All events
                    }
                }
                
                if auth_required and self.password:
                    import base64
                    import hashlib
                    challenge = hello_data["d"]["authentication"]["challenge"]
                    salt = hello_data["d"]["authentication"]["salt"]
                    
                    # OBS auth: base64(sha256(base64(sha256(password + salt)) + challenge))
                    secret = base64.b64encode(
                        hashlib.sha256((self.password + salt).encode()).digest()
                    ).decode()
                    auth_response = base64.b64encode(
                        hashlib.sha256((secret + challenge).encode()).digest()
                    ).decode()
                    identify_payload["d"]["authentication"] = auth_response
                
                await self.ws.send(json.dumps(identify_payload))
                response = await self.ws.recv()
                response_data = json.loads(response)
                
                if response_data.get("op") == 2:  # Identified
                    self._connected = True
                    return True
                else:
                    raise Exception(f"OBS auth failed: {response_data}")
            
            self._connected = True
            return True
            
        except Exception as e:
            raise Exception(f"Failed to connect to OBS at {self.url}: {e}")

    async def disconnect(self):
        """Disconnect from OBS."""
        if self.ws:
            await self.ws.close()
            self.ws = None
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected and self.ws is not None

    def _next_id(self) -> str:
        self._message_id += 1
        return str(self._message_id)

    async def send_request(self, request_type: str, request_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Send a request to OBS and wait for response."""
        if not self.ws:
            raise Exception("Not connected to OBS")

        payload = {
            "op": 6,
            "d": {
                "requestType": request_type,
                "requestId": self._next_id(),
                "requestData": request_data or {}
            }
        }

        await self.ws.send(json.dumps(payload))
        
        # Wait for response with matching requestId
        while True:
            response = await self.ws.recv()
            data = json.loads(response)
            
            if data.get("op") == 7:  # RequestResponse
                if data["d"]["requestId"] == payload["d"]["requestId"]:
                    if data["d"].get("requestStatus", {}).get("result") is False:
                        raise Exception(
                            f"OBS request failed: {data['d'].get('requestStatus', {}).get('comment', 'Unknown error')}"
                        )
                    return data["d"].get("responseData", {})
            
            elif data.get("op") == 8:  # RequestBatchResponse
                pass  # Ignore batch responses for now
            
            elif data.get("op") == 5:  # Event
                pass  # Ignore events for now

    # ==================== SCENE MANAGEMENT ====================

    async def get_scene_list(self) -> Dict[str, Any]:
        """List all scenes and current scene."""
        return await self.send_request("GetSceneList")

    async def set_current_scene(self, scene_name: str) -> Dict[str, Any]:
        """Switch to a specific scene."""
        return await self.send_request("SetCurrentProgramScene", {"sceneName": scene_name})

    async def create_scene(self, scene_name: str) -> Dict[str, Any]:
        """Create a new scene."""
        return await self.send_request("CreateScene", {"sceneName": scene_name})

    async def remove_scene(self, scene_name: str) -> Dict[str, Any]:
        """Remove a scene."""
        return await self.send_request("RemoveScene", {"sceneName": scene_name})

    # ==================== RECORDING CONTROL ====================

    async def start_recording(self) -> Dict[str, Any]:
        """Start recording."""
        return await self.send_request("StartRecord")

    async def stop_recording(self) -> Dict[str, Any]:
        """Stop recording. Returns output path."""
        return await self.send_request("StopRecord")

    async def pause_recording(self) -> Dict[str, Any]:
        """Pause recording."""
        return await self.send_request("PauseRecord")

    async def resume_recording(self) -> Dict[str, Any]:
        """Resume recording."""
        return await self.send_request("ResumeRecord")

    async def get_recording_status(self) -> Dict[str, Any]:
        """Get recording status."""
        return await self.send_request("GetRecordStatus")


    # ==================== STREAMING CONTROL ====================

    async def start_streaming(self) -> Dict[str, Any]:
        """Start streaming."""
        return await self.send_request("StartStream")

    async def stop_streaming(self) -> Dict[str, Any]:
        """Stop streaming."""
        return await self.send_request("StopStream")

    async def get_streaming_status(self) -> Dict[str, Any]:
        """Get streaming status."""
        return await self.send_request("GetStreamStatus")

    async def toggle_streaming(self) -> Dict[str, Any]:
        """Toggle streaming."""
        return await self.send_request("ToggleStream")

    async def send_stream_caption(self, caption_text: str) -> Dict[str, Any]:
        """Send caption to stream."""
        return await self.send_request("SendStreamCaption", {"captionText": caption_text})

    # ==================== VIRTUAL CAMERA ====================

    async def start_virtual_cam(self) -> Dict[str, Any]:
        """Start virtual camera."""
        return await self.send_request("StartVirtualCam")

    async def stop_virtual_cam(self) -> Dict[str, Any]:
        """Stop virtual camera."""
        return await self.send_request("StopVirtualCam")

    async def get_virtual_cam_status(self) -> Dict[str, Any]:
        """Get virtual camera status."""
        return await self.send_request("GetVirtualCamStatus")

    async def toggle_virtual_cam(self) -> Dict[str, Any]:
        """Toggle virtual camera."""
        return await self.send_request("ToggleVirtualCam")

    # ==================== REPLAY BUFFER ====================

    async def start_replay_buffer(self) -> Dict[str, Any]:
        """Start replay buffer."""
        return await self.send_request("StartReplayBuffer")

    async def stop_replay_buffer(self) -> Dict[str, Any]:
        """Stop replay buffer."""
        return await self.send_request("StopReplayBuffer")

    async def save_replay_buffer(self) -> Dict[str, Any]:
        """Save replay buffer."""
        return await self.send_request("SaveReplayBuffer")

    async def get_replay_buffer_status(self) -> Dict[str, Any]:
        """Get replay buffer status."""
        return await self.send_request("GetReplayBufferStatus")

    async def toggle_replay_buffer(self) -> Dict[str, Any]:
        """Toggle replay buffer."""
        return await self.send_request("ToggleReplayBuffer")

    async def get_last_replay_buffer_replay(self) -> Dict[str, Any]:
        """Get last replay buffer replay path."""
        return await self.send_request("GetLastReplayBufferReplay")

    # ==================== STUDIO MODE ====================


    async def set_studio_mode_enabled(self, enabled: bool) -> Dict[str, Any]:
        """Enable/disable studio mode."""
        return await self.send_request("SetStudioModeEnabled", {"studioModeEnabled": enabled})

    async def toggle_studio_mode(self) -> Dict[str, Any]:
        """Toggle studio mode."""
        return await self.send_request("ToggleStudioMode")

    async def get_preview_scene(self) -> Dict[str, Any]:
        """Get preview scene (studio mode)."""
        return await self.send_request("GetCurrentPreviewScene")

    async def set_preview_scene(self, scene_name: str) -> Dict[str, Any]:
        """Set preview scene (studio mode)."""
        return await self.send_request("SetCurrentPreviewScene", {"sceneName": scene_name})

    async def trigger_studio_mode_transition(self) -> Dict[str, Any]:
        """Trigger transition (studio mode)."""
        return await self.send_request("TriggerStudioModeTransition")

    # ==================== SOURCE MANAGEMENT ====================

    async def get_scene_item_list(self, scene_name: str) -> Dict[str, Any]:
        """List all items in a scene."""
        return await self.send_request("GetSceneItemList", {"sceneName": scene_name})

    async def get_input_list(self, input_kind: Optional[str] = None) -> Dict[str, Any]:
        """List all inputs."""
        data = {}
        if input_kind:
            data["inputKind"] = input_kind
        return await self.send_request("GetInputList", data)

    async def get_input_settings(self, input_name: str) -> Dict[str, Any]:
        """Get input settings."""
        return await self.send_request("GetInputSettings", {"inputName": input_name})

    async def set_input_settings(self, input_name: str, settings: Dict, overlay: bool = True) -> Dict[str, Any]:
        """Set input settings."""
        return await self.send_request("SetInputSettings", {
            "inputName": input_name,
            "inputSettings": settings,
            "overlay": overlay
        })

    async def get_scene_item_enabled(self, scene_name: str, scene_item_id: int) -> Dict[str, Any]:
        """Get if scene item is enabled (visible)."""
        return await self.send_request("GetSceneItemEnabled", {
            "sceneName": scene_name,
            "sceneItemId": scene_item_id
        })

    async def set_scene_item_enabled(self, scene_name: str, scene_item_id: int, enabled: bool) -> Dict[str, Any]:
        """Set scene item enabled (visible/hidden)."""
        return await self.send_request("SetSceneItemEnabled", {
            "sceneName": scene_name,
            "sceneItemId": scene_item_id,
            "sceneItemEnabled": enabled
        })

    async def toggle_scene_item_enabled(self, scene_name: str, scene_item_id: int) -> bool:
        """Toggle scene item visibility. Returns new state."""
        current = await self.get_scene_item_enabled(scene_name, scene_item_id)
        new_state = not current.get("sceneItemEnabled", True)
        await self.set_scene_item_enabled(scene_name, scene_item_id, new_state)
        return new_state

    async def get_scene_item_transform(self, scene_name: str, scene_item_id: int) -> Dict[str, Any]:
        """Get scene item transform."""
        return await self.send_request("GetSceneItemTransform", {
            "sceneName": scene_name,
            "sceneItemId": scene_item_id
        })

    async def set_scene_item_transform(self, scene_name: str, scene_item_id: int, transform: Dict) -> Dict[str, Any]:
        """Set scene item transform."""
        return await self.send_request("SetSceneItemTransform", {
            "sceneName": scene_name,
            "sceneItemId": scene_item_id,
            "sceneItemTransform": transform
        })

    async def create_input(self, scene_name: str, input_name: str, input_kind: str, settings: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new input source in a scene."""
        data = {
            "sceneName": scene_name,
            "inputName": input_name,
            "inputKind": input_kind
        }
        if settings:
            data["inputSettings"] = settings
        return await self.send_request("CreateInput", data)

    async def remove_input(self, input_name: str) -> Dict[str, Any]:
        """Remove an input."""
        return await self.send_request("RemoveInput", {"inputName": input_name})


    # ==================== AUDIO CONTROL ====================


    async def set_input_mute(self, input_name: str, muted: bool) -> Dict[str, Any]:
        """Set input mute state."""
        return await self.send_request("SetInputMute", {"inputName": input_name, "inputMuted": muted})

    async def toggle_input_mute(self, input_name: str) -> Dict[str, Any]:
        """Toggle input mute."""
        return await self.send_request("ToggleInputMute", {"inputName": input_name})

    async def get_input_volume(self, input_name: str) -> Dict[str, Any]:
        """Get input volume (dB and mul)."""
        return await self.send_request("GetInputVolume", {"inputName": input_name})

    async def set_input_volume(self, input_name: str, volume_db: Optional[float] = None, volume_mul: Optional[float] = None) -> Dict[str, Any]:
        """Set input volume."""
        data = {"inputName": input_name}
        if volume_db is not None:
            data["inputVolumeDb"] = volume_db
        if volume_mul is not None:
            data["inputVolumeMul"] = volume_mul
        return await self.send_request("SetInputVolume", data)

    # ==================== TRANSITIONS ====================

    async def get_scene_transition_list(self) -> Dict[str, Any]:
        """List all transitions."""
        return await self.send_request("GetSceneTransitionList")


    async def set_current_scene_transition(self, transition_name: str) -> Dict[str, Any]:
        """Set current transition."""
        return await self.send_request("SetCurrentSceneTransition", {"transitionName": transition_name})

    async def set_current_scene_transition_duration(self, duration_ms: int) -> Dict[str, Any]:
        """Set transition duration."""
        return await self.send_request("SetCurrentSceneTransitionDuration", {"transitionDuration": duration_ms})

    async def get_input_kind_list(self) -> Dict[str, Any]:
        """List all available input source types."""
        return await self.send_request("GetInputKindList")

    # ==================== PROFILE & COLLECTION ====================

    async def get_profile_list(self) -> Dict[str, Any]:
        """List all profiles."""
        return await self.send_request("GetProfileList")

    async def set_current_profile(self, profile_name: str) -> Dict[str, Any]:
        """Set current profile."""
        return await self.send_request("SetCurrentProfile", {"profileName": profile_name})

    async def get_scene_collection_list(self) -> Dict[str, Any]:
        """List all scene collections."""
        return await self.send_request("GetSceneCollectionList")

    async def set_current_scene_collection(self, scene_collection_name: str) -> Dict[str, Any]:
        """Set current scene collection."""
        return await self.send_request("SetCurrentSceneCollection", {"sceneCollectionName": scene_collection_name})

    # ==================== OUTPUTS ====================




    # ==================== HOTKEYS ====================

    async def get_hotkey_list(self) -> Dict[str, Any]:
        """List all hotkeys."""
        return await self.send_request("GetHotkeyList")

    async def trigger_hotkey_by_name(self, hotkey_name: str) -> Dict[str, Any]:
        """Trigger hotkey by name."""
        return await self.send_request("TriggerHotkeyByName", {"hotkeyName": hotkey_name})

    # ==================== STATS & INFO ====================

    async def get_version(self) -> Dict[str, Any]:
        """Get OBS version info."""
        return await self.send_request("GetVersion")

    async def get_stats(self) -> Dict[str, Any]:
        """Get OBS stats."""
        return await self.send_request("GetStats")

    async def get_stream_service_settings(self) -> Dict[str, Any]:
        """Get stream service settings."""
        return await self.send_request("GetStreamServiceSettings")

    async def set_stream_service_settings(self, service_type: str, settings: Dict) -> Dict[str, Any]:
        """Set stream service settings."""
        return await self.send_request("SetStreamServiceSettings", {
            "streamServiceType": service_type,
            "streamServiceSettings": settings
        })

    # ==================== SCREENSHOT ====================

    async def get_source_screenshot(self, source_name: str, image_format: str = "png", width: int = 0, height: int = 0, quality: int = -1) -> Dict[str, Any]:
        """Get screenshot of a source as base64."""
        data = {
            "sourceName": source_name,
            "imageFormat": image_format,
            "imageWidth": width,
            "imageHeight": height,
            "imageCompressionQuality": quality
        }
        return await self.send_request("GetSourceScreenshot", data)

    async def save_source_screenshot(self, source_name: str, file_path: str, image_format: str = "png", width: int = 0, height: int = 0, quality: int = -1) -> Dict[str, Any]:
        """Save screenshot of a source to file."""
        data = {
            "sourceName": source_name,
            "imageFilePath": file_path,
            "imageFormat": image_format,
            "imageWidth": width,
            "imageHeight": height,
            "imageCompressionQuality": quality
        }
        return await self.send_request("SaveSourceScreenshot", data)

    # ==================== SPECIAL SOURCES ====================

    async def get_special_inputs(self) -> Dict[str, Any]:
        """Get special input names (desktop audio, mic)."""
        return await self.send_request("GetSpecialInputs")


    # ==================== FILTERS ====================

    async def get_source_filter_list(self, source_name: str) -> Dict[str, Any]:
        """List filters on a source."""
        return await self.send_request("GetSourceFilterList", {"sourceName": source_name})

    async def get_source_filter(self, source_name: str, filter_name: str) -> Dict[str, Any]:
        """Get filter settings."""
        return await self.send_request("GetSourceFilter", {"sourceName": source_name, "filterName": filter_name})

    async def set_source_filter_enabled(self, source_name: str, filter_name: str, enabled: bool) -> Dict[str, Any]:
        """Enable/disable filter."""
        return await self.send_request("SetSourceFilterEnabled", {
            "sourceName": source_name,
            "filterName": filter_name,
            "filterEnabled": enabled
        })

    async def create_source_filter(self, source_name: str, filter_name: str, filter_kind: str, settings: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a filter on a source."""
        data = {
            "sourceName": source_name,
            "filterName": filter_name,
            "filterKind": filter_kind
        }
        if settings:
            data["filterSettings"] = settings
        return await self.send_request("CreateSourceFilter", data)

    async def remove_source_filter(self, source_name: str, filter_name: str) -> Dict[str, Any]:
        """Remove a filter."""
        return await self.send_request("RemoveSourceFilter", {"sourceName": source_name, "filterName": filter_name})

    # ==================== BROWSER SOURCE ====================

    async def press_input_properties_button(self, input_name: str, property_name: str) -> Dict[str, Any]:
        """Press a button property on an input (e.g. refresh browser)."""
        return await self.send_request("PressInputPropertiesButton", {
            "inputName": input_name,
            "propertyName": property_name
        })

    async def refresh_browser_source(self, source_name: str) -> Dict[str, Any]:
        """Refresh a browser source."""
        return await self.press_input_properties_button(source_name, "refreshnocache")

    # ==================== MEDIA SOURCE ====================

    async def get_media_input_status(self, input_name: str) -> Dict[str, Any]:
        """Get media input status (playing, paused, etc)."""
        return await self.send_request("GetMediaInputStatus", {"inputName": input_name})



    async def trigger_media_input_action(self, input_name: str, action: str) -> Dict[str, Any]:
        """Trigger media input action: play, pause, restart, stop, next, previous."""
        return await self.send_request("TriggerMediaInputAction", {
            "inputName": input_name,
            "mediaAction": action
        })

    # ==================== HIGH-LEVEL HELPERS ====================

    async def get_full_status(self) -> Dict[str, Any]:
        """Get comprehensive OBS status."""
        try:
            version = await self.get_version()
            stats = await self.get_stats()
            scenes = await self.get_scene_list()
            record = await self.get_recording_status()
            stream = await self.get_streaming_status()
            virtual_cam = await self.get_virtual_cam_status()
            replay = await self.get_replay_buffer_status()

            return {
                "connected": True,
                "version": version.get("obsVersion", "unknown"),
                "platform": version.get("platform", "unknown"),
                "websocket_version": version.get("obsWebSocketVersion", "unknown"),
                "current_scene": scenes.get("currentProgramSceneName", ""),
                "scenes": [s.get("sceneName", "") for s in scenes.get("scenes", [])],
                "recording": {
                    "active": record.get("outputActive", False),
                    "paused": record.get("outputPaused", False),
                    "timecode": record.get("outputTimecode", "")
                },
                "streaming": {
                    "active": stream.get("outputActive", False),
                    "reconnecting": stream.get("outputReconnecting", False),
                    "timecode": stream.get("outputTimecode", "")
                },
                "virtual_cam": {
                    "active": virtual_cam.get("outputActive", False)
                },
                "replay_buffer": {
                    "active": replay.get("outputActive", False)
                },
                "stats": {
                    "fps": stats.get("activeFps", 0),
                    "render_time_ms": stats.get("averageFrameRenderTime", 0),
                    "cpu_usage": stats.get("cpuUsage", 0),
                    "memory_usage": stats.get("memoryUsage", 0),
                    "output_skipped_frames": stats.get("outputSkippedFrames", 0),
                    "output_total_frames": stats.get("outputTotalFrames", 0)
                }
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}

    async def find_scene_item_by_name(self, scene_name: str, source_name: str) -> Optional[int]:
        """Find scene item ID by source name. Returns None if not found."""
        items = await self.get_scene_item_list(scene_name)
        for item in items.get("sceneItems", []):
            if item.get("sourceName") == source_name:
                return item.get("sceneItemId")
        return None

    async def set_source_visibility(self, scene_name: str, source_name: str, visible: bool) -> bool:
        """Set source visibility by name. Returns True if successful."""
        item_id = await self.find_scene_item_by_name(scene_name, source_name)
        if item_id is None:
            return False
        await self.set_scene_item_enabled(scene_name, item_id, visible)
        return True



    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
