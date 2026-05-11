"""
Pi Agent Core - Central orchestrator for all skills and operations.

Architecture:
  Pi Agent (orchestrator) manages:
  - Skills (YouTube, Auth, Status, etc.)
  - User context (credentials, state)
  - Intent parsing and execution
"""

import os
import pickle
import re
from typing import Any, Dict, Optional, Tuple
from pathlib import Path

# Import skills from modular structure
from skills.youtube.upload_video import upload_video
from skills.youtube.edit_metadata import edit_video_metadata
from skills.youtube.youtube_auth import get_authenticated_service

TOKEN_FILE = "token.pickle"
CLIENT_SECRETS_FILE = "client_secrets.json"


class PiAgentContext:
    """Manages user session and credentials."""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.credentials = None
        self.youtube_service = None
        self._load_credentials()
    
    def _load_credentials(self):
        """Load credentials from token.pickle if exists."""
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "rb") as f:
                    self.credentials = pickle.load(f)
                self.youtube_service = get_authenticated_service()
            except Exception as e:
                print(f"Error loading credentials: {e}")
    
    def is_authenticated(self) -> bool:
        """Check if user has valid YouTube credentials."""
        return self.credentials is not None and self.youtube_service is not None
    
    def refresh_service(self):
        """Refresh YouTube service."""
        try:
            self.youtube_service = get_authenticated_service()
        except Exception as e:
            print(f"Error refreshing service: {e}")


class Skill:
    """Base class for all Pi Agent skills."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the skill and return result."""
        raise NotImplementedError


class YouTubeUploadSkill(Skill):
    """Skill untuk upload video ke YouTube."""
    
    def __init__(self):
        super().__init__(
            "youtube_upload",
            "Upload video ke YouTube"
        )
    
    async def execute(self, context: PiAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute upload."""
        if not context.is_authenticated():
            return {
                "success": False,
                "error": "Belum autentikasi. Gunakan /auth terlebih dahulu."
            }
        
        try:
            file_path = kwargs.get("file_path")
            title = kwargs.get("title", "Untitled")
            description = kwargs.get("description", "")
            tags = kwargs.get("tags", [])
            privacy = kwargs.get("privacy", "private")
            
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File tidak ditemukan: {file_path}"
                }
            
            video_id = upload_video(
                file_path=file_path,
                title=title,
                description=description,
                tags=tags,
                privacy=privacy
            )
            
            return {
                "success": True,
                "video_id": video_id,
                "title": title,
                "message": f"✅ Video berhasil diupload!\nID: {video_id}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class YouTubeEditSkill(Skill):
    """Skill untuk edit metadata video YouTube."""
    
    def __init__(self):
        super().__init__(
            "youtube_edit",
            "Edit metadata video YouTube"
        )
    
    async def execute(self, context: PiAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute edit."""
        if not context.is_authenticated():
            return {
                "success": False,
                "error": "Belum autentikasi. Gunakan /auth terlebih dahulu."
            }
        
        try:
            video_id = kwargs.get("video_id")
            title = kwargs.get("title")
            description = kwargs.get("description")
            privacy = kwargs.get("privacy")
            
            edit_video_metadata(
                video_id=video_id,
                title=title,
                description=description,
                privacy=privacy
            )
            
            return {
                "success": True,
                "video_id": video_id,
                "message": f"✅ Metadata video {video_id} berhasil diupdate!"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class StatusSkill(Skill):
    """Skill untuk cek status autentikasi."""
    
    def __init__(self):
        super().__init__(
            "status",
            "Cek status autentikasi YouTube"
        )
    
    async def execute(self, context: PiAgentContext, **kwargs) -> Dict[str, Any]:
        """Execute status check."""
        auth_action = {
            "text": "Login ke YouTube",
            "url": "http://localhost:5000/auth/login"
        }

        if not os.path.exists(TOKEN_FILE):
            return {
                "success": True,
                "authenticated": False,
                "message": "❌ Belum terautentikasi dengan YouTube. Silakan login.",
                "auth_action": auth_action
            }
        
        try:
            if context.credentials:
                if not context.credentials.valid and not (context.credentials.expired and context.credentials.refresh_token):
                    return {
                        "success": True,
                        "authenticated": False,
                        "message": "❌ Token expired dan tidak bisa di-refresh. Silakan login ulang.",
                        "auth_action": auth_action
                    }
                
                status = (
                    f"✅ token.pickle ada\n"
                    f"Valid: {context.credentials.valid}\n"
                    f"Expired: {context.credentials.expired}"
                )
                if context.credentials.refresh_token:
                    status += "\n✅ Refresh token tersedia"
                return {
                    "success": True,
                    "authenticated": True,
                    "message": status
                }
        except Exception as e:
            pass
        
        return {
            "success": True,
            "authenticated": False,
            "message": "⚠️ Error membaca token. Silakan login ulang.",
            "auth_action": auth_action
        }


class PiAgent:
    """Main orchestrator for all operations."""
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.contexts: Dict[int, PiAgentContext] = {}
        self._register_skills()
    
    def _register_skills(self):
        """Register all available skills."""
        skills = [
            YouTubeUploadSkill(),
            YouTubeEditSkill(),
            StatusSkill(),
        ]
        for skill in skills:
            self.skills[skill.name] = skill
    
    def get_context(self, user_id: int) -> PiAgentContext:
        """Get or create user context."""
        if user_id not in self.contexts:
            self.contexts[user_id] = PiAgentContext(user_id)
        return self.contexts[user_id]
    
    async def parse_intent(self, user_message: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse user message to determine intent and extract parameters.
        Returns: (skill_name, kwargs)
        """
        msg = user_message.lower().strip()
        
        # Upload intent
        if any(word in msg for word in ["upload", "unggah", "kirim"]):
            params = self._extract_upload_params(user_message)
            if params:
                return "youtube_upload", params
        
        # Edit intent
        if any(word in msg for word in ["edit", "ubah", "update", "ganti"]):
            params = self._extract_edit_params(user_message)
            if params:
                return "youtube_edit", params
        
        # Status intent
        if any(word in msg for word in ["status", "cek", "check"]):
            return "status", {}
        
        return None, {}
    
    def _extract_upload_params(self, message: str) -> Optional[Dict[str, Any]]:
        """Extract upload parameters from message."""
        import shlex
        import re
        try:
            # Find file path - look for paths starting with / or containing .mp4
            path_match = re.search(r'["\']?(/[^"\s]+(?:\.mp4)?)["\']?', message)
            if not path_match:
                return None
            
            file_path = path_match.group(1)
            
            # Extract title - look for quoted strings or words after "judul/title/judulnya"
            title_match = re.search(
                r'(?:judul|title|judulnya|named)["\']?\s*[:\s]*["\']?([^"\']+?)["\']?(?:\s+(?:desc|deskripsi|tag|tag1)|$)',
                message,
                re.IGNORECASE
            )
            title = title_match.group(1).strip() if title_match else "Untitled"
            
            # Extract description
            desc_match = re.search(
                r'(?:desc|deskripsi|description)["\']?\s*[:\s]*["\']?([^"\']+?)["\']?(?:\s+(?:tag|tag1)|$)',
                message,
                re.IGNORECASE
            )
            description = desc_match.group(1).strip() if desc_match else ""
            
            # Extract tags
            tags_match = re.search(
                r'(?:tag|tags|tagged)["\']?\s*[:\s]*["\']?([^"\']+?)["\']?$',
                message,
                re.IGNORECASE
            )
            tags_str = tags_match.group(1) if tags_match else ""
            tags = [t.strip() for t in tags_str.split(",") if t.strip()]
            
            return {
                "file_path": file_path,
                "title": title,
                "description": description,
                "tags": tags,
                "privacy": "private"
            }
        except Exception:
            return None
    
    def _extract_edit_params(self, message: str) -> Optional[Dict[str, Any]]:
        """Extract edit parameters from message."""
        import re
        try:
            # Find video ID - look for 11-char YouTube IDs or quoted strings after "video"
            id_match = re.search(
                r'(?:video|video_id|ID)\s+["\']?([a-zA-Z0-9_-]{11})["\']?',
                message,
                re.IGNORECASE
            )
            if not id_match:
                # Try second pattern: just a word that looks like video ID
                id_match = re.search(r'(?:edit|ubah|update)\s+([a-zA-Z0-9_-]{11})', message, re.IGNORECASE)
            
            if not id_match:
                return None
            
            video_id = id_match.group(1)
            
            # Extract title
            title_match = re.search(
                r'(?:judul|title|judulnya)["\']?\s*[:\s]*["\']?([^"\']+?)["\']?(?:\s+(?:desc|deskripsi)|$)',
                message,
                re.IGNORECASE
            )
            title = title_match.group(1).strip() if title_match else None
            
            # Extract description
            desc_match = re.search(
                r'(?:desc|deskripsi|description)["\']?\s*[:\s]*["\']?([^"\']+?)["\']?(?:\s+(?:privacy|status|private|public|unlisted)|$)',
                message,
                re.IGNORECASE
            )
            description = desc_match.group(1).strip() if desc_match else None
            
            # Extract privacy
            privacy_match = re.search(r'(private|public|unlisted)', message, re.IGNORECASE)
            privacy = privacy_match.group(1).lower() if privacy_match else None
            
            return {
                "video_id": video_id,
                "title": title,
                "description": description,
                "privacy": privacy
            }
        except Exception:
            return None
    
    async def execute(self, user_id: int, user_message: str) -> Dict[str, Any]:
        """Execute user request."""
        context = self.get_context(user_id)
        skill_name, params = await self.parse_intent(user_message)
        
        if not skill_name or skill_name not in self.skills:
            return {
                "success": False,
                "error": "Maksud pesan tidak jelas. Gunakan /help untuk panduan."
            }
        
        skill = self.skills[skill_name]
        result = await skill.execute(context=context, **params)
        
        return result


# Global instance
_pi_agent = None


def get_pi_agent() -> PiAgent:
    """Get or create global Pi Agent instance."""
    global _pi_agent
    if _pi_agent is None:
        _pi_agent = PiAgent()
    return _pi_agent
