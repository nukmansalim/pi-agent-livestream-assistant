"""
core/pi_agent_core.py
Pi Agent Core Orchestrator - Updated with Livestream Feature
"""

import os
import pickle
import re
import asyncio
from typing import Any, Dict, Optional
from pathlib import Path

# Import existing skills
from skills.youtube.upload_video import upload_video
from skills.youtube.edit_metadata import edit_video_metadata
from skills.youtube.youtube_auth import get_authenticated_service

# NEW: Livestream Skill
from skills.youtube.livestream import YouTubeLivestreamSkill


TOKEN_FILE = "token.pickle"
CLIENT_SECRETS_FILE = "client_secrets.json"


class PiAgentContext:
    """Context for each user/session"""
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.authenticated = False
        self.youtube_service = None

    def is_authenticated(self) -> bool:
        if not self.authenticated and os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "rb") as f:
                    self.youtube_service = pickle.load(f)
                self.authenticated = True
            except:
                pass
        return self.authenticated


class Skill:
    """Base class for all skills"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    async def execute(self, context: PiAgentContext, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("Skill must implement execute()")


class YouTubeUploadSkill(Skill):
    def __init__(self):
        super().__init__("youtube_upload", "Upload video to YouTube")

    async def execute(self, context: PiAgentContext, **kwargs) -> Dict[str, Any]:
        if not context.is_authenticated():
            return {"success": False, "error": "Belum autentikasi. Gunakan /auth terlebih dahulu."}
        # ... your existing upload logic ...
        return {"success": True, "message": "Video uploaded"}


class YouTubeEditSkill(Skill):
    def __init__(self):
        super().__init__("youtube_edit", "Edit YouTube video metadata")

    async def execute(self, context: PiAgentContext, **kwargs) -> Dict[str, Any]:
        if not context.is_authenticated():
            return {"success": False, "error": "Belum autentikasi. Gunakan /auth terlebih dahulu."}
        # ... your existing edit logic ...
        return {"success": True, "message": "Video metadata updated"}


class YouTubeLivestreamSkillClass(Skill):
    """Livestream Skill"""
    def __init__(self):
        super().__init__("youtube_livestream", "Create and control YouTube livestreams")
        self.livestream = YouTubeLivestreamSkill()

    async def execute(self, context: PiAgentContext, **kwargs) -> Dict[str, Any]:
        if not context.is_authenticated():
            return {
                "success": False,
                "error": "Belum autentikasi. Gunakan /auth terlebih dahulu."
            }

        action = kwargs.get("action", "create").lower()

        try:
            if action == "create":
                result = self.livestream.create_broadcast(
                    title=kwargs.get("title", "Pi Agent Livestream"),
                    description=kwargs.get("description", ""),
                    privacy=kwargs.get("privacy", "private"),
                    scheduled_minutes=kwargs.get("scheduled_minutes", 10)   # ← Fixed here
                )

                stream = self.livestream.create_stream()
                self.livestream.bind_broadcast(result["broadcast_id"], stream["stream_id"])

                return {
                    "success": True,
                    "action": "create",
                    "broadcast_id": result["broadcast_id"],
                    "rtmp_url": stream["rtmp_url"],
                    "stream_key": stream["stream_key"],
                    "message": "✅ Livestream berhasil dibuat!\n\n"
                              f"RTMP URL: {stream['rtmp_url']}\n"
                              f"Stream Key: {stream['stream_key']}\n\n"
                              "Paste ke OBS Studio → Settings → Stream"
                }

            elif action == "start":
                broadcast_id = kwargs.get("broadcast_id")
                if not broadcast_id:
                    return {"success": False, "error": "broadcast_id diperlukan"}
                self.livestream.start_broadcast(broadcast_id)
                return {"success": True, "message": f"✅ Broadcast {broadcast_id} sedang LIVE!"}

            elif action == "end":
                broadcast_id = kwargs.get("broadcast_id")
                if not broadcast_id:
                    return {"success": False, "error": "broadcast_id diperlukan"}
                self.livestream.end_broadcast(broadcast_id)
                return {"success": True, "message": f"✅ Broadcast {broadcast_id} telah diakhiri."}

        except Exception as e:
            return {"success": False, "error": str(e)}

            
class PiAgent:
    """Main Pi Agent Orchestrator"""
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.contexts: Dict[int, PiAgentContext] = {}
        self._register_skills()

    def _register_skills(self):
        self.skills = {
            "youtube_upload": YouTubeUploadSkill(),
            "youtube_edit": YouTubeEditSkill(),
            "youtube_livestream": YouTubeLivestreamSkillClass(),
        }

    def get_context(self, user_id: int) -> PiAgentContext:
        if user_id not in self.contexts:
            self.contexts[user_id] = PiAgentContext(user_id)
        return self.contexts[user_id]

    def parse_intent(self, user_message: str) -> tuple:
        """Parse natural language into skill + parameters"""
        msg = user_message.lower()

        # Livestream Intent
        if any(word in msg for word in ["live", "livestream", "streaming", "mulai siaran", "akhiri siaran"]):
            params = self._extract_livestream_params(user_message)
            return "youtube_livestream", params

        # Upload Intent (keep your existing logic)
        if any(word in msg for word in ["upload", "unggah"]):
            return "youtube_upload", {"file_path": "...", "title": "..."}

        # Edit Intent
        if any(word in msg for word in ["edit", "ubah"]):
            return "youtube_edit", {}

        return "unknown", {}

    def _extract_livestream_params(self, message: str) -> Dict[str, Any]:
        """Extract parameters from livestream command"""
        msg = message.lower()
        params = {"action": "create"}

        if any(word in msg for word in ["start", "mulai", "live now"]):
            params["action"] = "start"
        elif any(word in msg for word in ["end", "stop", "akhiri", "selesai"]):
            params["action"] = "end"

        # Extract title
        title_match = re.search(r'(?:judul|title|named)\s*[:\s]*["\']?([^"\']+?)["\']?', message, re.IGNORECASE)
        if title_match:
            params["title"] = title_match.group(1).strip()

        # Extract broadcast_id for start/end
        id_match = re.search(r'([a-zA-Z0-9_-]{11,})', message)
        if id_match and params["action"] in ["start", "end"]:
            params["broadcast_id"] = id_match.group(1)

        return params

    async def execute(self, user_id: int, command: str) -> Dict[str, Any]:
        context = self.get_context(user_id)
        skill_name, params = self.parse_intent(command)

        if skill_name not in self.skills:
            return {"success": False, "error": "Unknown command"}

        skill = self.skills[skill_name]
        return await skill.execute(context, **params)


# Singleton
_pi_agent = None

def get_pi_agent():
    global _pi_agent
    if _pi_agent is None:
        _pi_agent = PiAgent()
    return _pi_agent