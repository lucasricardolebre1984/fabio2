"""Facade para o prompt principal da VIVA.

Fonte canonica de persona: backend/COFRE/persona-skills/AGENT.md
"""

from typing import Optional

from app.services.viva_agent_profile_service import viva_agent_profile_service


class VivaConciergeService:
    """Builds the VIVA system prompt from the project-level AGENT.md."""

    def build_system_prompt(self, modo: Optional[str] = None) -> str:
        return viva_agent_profile_service.build_system_prompt(modo=modo)


viva_concierge_service = VivaConciergeService()
