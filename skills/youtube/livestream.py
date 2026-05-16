"""
skills/youtube/livestream.py
YouTube Livestream Skill - Fixed Parameter Names
"""

import datetime
# pyrefly: ignore [missing-import]
from googleapiclient.discovery import build
import pickle
import os

TOKEN_FILE = "token.pickle"

class YouTubeLivestreamSkill:
    def __init__(self):
        self.youtube = None
        self._build_service()

    def _build_service(self):
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "rb") as f:
                    credentials = pickle.load(f)
                self.youtube = build('youtube', 'v3', credentials=credentials)
            except Exception as e:
                print(f"[Livestream] Error building service: {e}")

    def create_broadcast(self, title: str, description: str = "", privacy: str = "private",
                        scheduled_minutes: int = 10,
                        enable_auto_start: bool = True,
                        enable_auto_stop: bool = True,
                        enable_dvr: bool = True,
                        enable_embed: bool = True):
        """Create a new live broadcast with monitor stream settings for replay."""
        if not self.youtube:
            raise Exception("YouTube service not initialized. Please authenticate first.")

        start_time = (datetime.datetime.now(datetime.timezone.utc) +
                     datetime.timedelta(minutes=scheduled_minutes)).isoformat()

        broadcast_body = {
            "snippet": {
                "title": title,
                "description": description,
                "scheduledStartTime": start_time
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False
            },
            "contentDetails": {
                "enableAutoStart": enable_auto_start,
                "enableAutoStop": enable_auto_stop,
                "enableDvr": enable_dvr,
                "enableEmbed": enable_embed,
                "monitorStream": {
                    "enableMonitorStream": True,
                    "broadcastStreamDelayMs": 0
                }
            }
        }

        request = self.youtube.liveBroadcasts().insert(
            part="snippet,status,contentDetails",
            body=broadcast_body
        )
        response = request.execute()

        return {
            "broadcast_id": response["id"],
            "title": title,
            "scheduled_start": start_time,
            "privacy": privacy,
            "auto_start": enable_auto_start,
            "auto_stop": enable_auto_stop,
            "dvr_enabled": enable_dvr,
            "embed_enabled": enable_embed
        }

    def create_stream(self, title: str = "Pi Agent Livestream"):
        if not self.youtube:
            raise Exception("YouTube service not initialized.")

        stream_body = {
            "snippet": {"title": title},
            "cdn": {
                "frameRate": "variable",
                "ingestionType": "rtmp",
                "resolution": "variable"
            }
        }

        request = self.youtube.liveStreams().insert(
            part="snippet,cdn",
            body=stream_body
        )
        response = request.execute()

        return {
            "stream_id": response["id"],
            "rtmp_url": response["cdn"]["ingestionInfo"]["ingestionAddress"],
            "stream_key": response["cdn"]["ingestionInfo"]["streamName"]
        }

    # State machine: valid transitions
    VALID_TRANSITIONS = {
        "ready": ["live"],
        "live": ["complete"],
        "complete": []
    }

    def get_broadcast_status(self, broadcast_id: str) -> str:
        """Get current status of a live broadcast."""
        if not self.youtube:
            raise Exception("YouTube service not initialized.")
        request = self.youtube.liveBroadcasts().list(
            id=broadcast_id,
            part="status"
        )
        response = request.execute()
        items = response.get("items", [])
        if not items:
            raise Exception(f"Broadcast '{broadcast_id}' not found.")
        return items[0]["status"]["lifeCycleStatus"]

    def bind_broadcast(self, broadcast_id: str, stream_id: str):
        request = self.youtube.liveBroadcasts().bind(
            id=broadcast_id,
            part="id",
            streamId=stream_id
        )
        return request.execute()

    def update_broadcast_privacy(self, broadcast_id: str, privacy: str):
        """Update broadcast privacy status (public/unlisted/private)."""
        if not self.youtube:
            raise Exception("YouTube service not initialized.")
        if privacy not in ("public", "unlisted", "private"):
            raise Exception(f"Invalid privacy '{privacy}'. Must be public, unlisted, or private.")
        body = {
            "id": broadcast_id,
            "status": {
                "privacyStatus": privacy
            }
        }
        request = self.youtube.liveBroadcasts().update(
            part="status",
            body=body
        )
        return request.execute()

    def _validate_transition(self, current_status: str, target_status: str):
        """Validate state transition according to YouTube state machine."""
        allowed = self.VALID_TRANSITIONS.get(current_status, [])
        if target_status not in allowed:
            raise Exception(
                f"Invalid transition: cannot go from '{current_status}' to '{target_status}'. "
                f"Allowed transitions from '{current_status}': {allowed if allowed else 'none'}"
            )

    def start_broadcast(self, broadcast_id: str):
        if not self.youtube:
            raise Exception("YouTube service not initialized.")
        try:
            current = self.get_broadcast_status(broadcast_id)
        except Exception as e:
            raise Exception(f"Failed to check broadcast status: {e}")
        self._validate_transition(current, "live")
        request = self.youtube.liveBroadcasts().transition(
            broadcastStatus="live",
            id=broadcast_id,
            part="id,status"
        )
        return request.execute()

    def end_broadcast(self, broadcast_id: str):
        if not self.youtube:
            raise Exception("YouTube service not initialized.")
        try:
            current = self.get_broadcast_status(broadcast_id)
        except Exception as e:
            raise Exception(f"Failed to check broadcast status: {e}")
        self._validate_transition(current, "complete")
        request = self.youtube.liveBroadcasts().transition(
            broadcastStatus="complete",
            id=broadcast_id,
            part="id,status"
        )
        return request.execute()