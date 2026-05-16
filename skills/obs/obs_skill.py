"""
skills/obs/obs_skill.py
Pi Agent Skill wrapper for OBS Control.
Integrates with Pi Agent Core orchestrator.
"""

import sys
import os
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .obs_control import get_obs_skill


class OBSSkill:
    """OBS Control Skill for Pi Agent."""

    def __init__(self):
        # Delay import to avoid circular dependency
        from core.pi_agent_core import Skill
        self._base = Skill.__new__(Skill)
        self._base.name = "obs_control"
        self._base.description = "Control OBS Studio via WebSocket"
        self.obs = get_obs_skill()

    # Inherit name and description
    @property
    def name(self):
        return self._base.name

    @name.setter
    def name(self, value):
        self._base.name = value

    @property
    def description(self):
        return self._base.description

    @description.setter
    def description(self, value):
        self._base.description = value

    async def execute(self, context, **kwargs) -> Dict[str, Any]:
        """Execute OBS command."""
        action = kwargs.get("action", "status")
        
        # Remove action from kwargs to avoid duplication
        params = {k: v for k, v in kwargs.items() if k != "action"}
        
        result = await self.obs.execute(action, **params)
        return result

    def parse_intent(self, command: str) -> tuple:
        """Parse natural language into action and params."""
        return self.obs.parse_command(command)
