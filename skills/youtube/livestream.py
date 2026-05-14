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
                        scheduled_minutes: int = 10):
        """Create a new live broadcast"""
        if not self.youtube:
            raise Exception("YouTube service not initialized. Please authenticate first.")

        start_time = (datetime.datetime.utcnow() + 
                     datetime.timedelta(minutes=scheduled_minutes)).isoformat() + "Z"

        broadcast_body = {
            "snippet": {
                "title": title,
                "description": description,
                "scheduledStartTime": start_time
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False
            }
        }

        request = self.youtube.liveBroadcasts().insert(
            part="snippet,status",
            body=broadcast_body
        )
        response = request.execute()

        return {
            "broadcast_id": response["id"],
            "title": title,
            "scheduled_start": start_time,
            "privacy": privacy
        }

    def create_stream(self):
        if not self.youtube:
            raise Exception("YouTube service not initialized.")

        stream_body = {
            "snippet": {"title": "Pi Agent Livestream"},
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

    def bind_broadcast(self, broadcast_id: str, stream_id: str):
        request = self.youtube.liveBroadcasts().bind(
            id=broadcast_id,
            part="id",
            streamId=stream_id
        )
        return request.execute()

    def start_broadcast(self, broadcast_id: str):
        request = self.youtube.liveBroadcasts().transition(
            broadcastStatus="live",
            id=broadcast_id,
            part="id,status"
        )
        return request.execute()

    def end_broadcast(self, broadcast_id: str):
        request = self.youtube.liveBroadcasts().transition(
            broadcastStatus="complete",
            id=broadcast_id,
            part="id,status"
        )
        return request.execute()