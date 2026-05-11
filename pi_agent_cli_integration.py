#!/usr/bin/env python3
"""
Pi Agent CLI Integration Module

This module allows the YouTube Pi Agent to be used as a skill
in external Pi Agent CLI systems.
"""

import sys
import os
from typing import Dict, Any, Optional
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pi_agent_core import get_pi_agent, PiAgentContext

class PiAgentCLISkill:
    """Wrapper to expose YouTube Pi Agent as CLI skill."""

    def __init__(self):
        self.agent = get_pi_agent()
        self.name = "youtube_manager"
        self.description = "Manage YouTube videos: upload, edit metadata, check status"

    def execute(self, user_id: str, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute YouTube management command.

        Args:
            user_id: User identifier (for context)
            command: Natural language command
            **kwargs: Additional parameters

        Returns:
            Dict with success status and result
        """
        try:
            # Convert user_id to int for PiAgentContext
            user_id_int = hash(user_id) % 1000000  # Simple hash to int

            # Execute via Pi Agent
            result = await self.agent.execute(user_id_int, command)

            return {
                "success": result.get("success", False),
                "result": result,
                "message": result.get("message", result.get("error", "Unknown result"))
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Pi Agent execution failed: {str(e)}"
            }

    def get_capabilities(self) -> Dict[str, Any]:
        """Return skill capabilities for CLI discovery."""
        return {
            "name": self.name,
            "description": self.description,
            "commands": [
                "upload video from /path/to/file.mp4 titled 'Title' with description 'Desc'",
                "edit video VIDEO_ID with new title 'New Title'",
                "check youtube authentication status",
                "upload /path/file.mp4 'Title' 'Description' tag1,tag2",
                "edit VIDEO_ID 'New Title' 'New Desc' private"
            ],
            "examples": [
                "upload video from /home/user/video.mp4 titled 'My Video'",
                "edit video dQw4w9WgXcQ with new title 'Updated Title'",
                "check youtube status"
            ]
        }

# Global instance
_pi_cli_skill = None

def get_pi_cli_skill() -> PiAgentCLISkill:
    """Get singleton CLI skill instance."""
    global _pi_cli_skill
    if _pi_cli_skill is None:
        _pi_cli_skill = PiAgentCLISkill()
    return _pi_cli_skill

def main():
    """CLI entry point for testing."""
    if len(sys.argv) < 3:
        print("Usage: python pi_agent_cli_integration.py <user_id> <command>")
        print("\nExample:")
        print("python pi_agent_cli_integration.py user123 'upload /path/video.mp4 \"My Video\" \"Description\"'")
        return

    user_id = sys.argv[1]
    command = " ".join(sys.argv[2:])

    skill = get_pi_cli_skill()

    # Note: This would need to be run in an async context
    print(f"Would execute: {command}")
    print("For actual execution, integrate with async CLI framework")

if __name__ == "__main__":
    main()</content>
<parameter name="filePath">/home/nukman/Dokumen/Pi to Youtube/pi_agent_cli_integration.py