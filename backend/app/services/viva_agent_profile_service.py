"""Loads the single agent profile and campaign skill from /agents."""

from __future__ import annotations

from pathlib import Path
from typing import Optional


class VivaAgentProfileService:
    def __init__(self) -> None:
        # Look for /agents relative to this file to work in:
        # - local repo layout: <repo>/backend/app/services/...
        # - dev container layout: /app/app/services/... with /app/agents mounted
        self._agents_dir = self._discover_agents_dir()
        self._agent_file = self._agents_dir / "AGENT.md"
        self._campaign_skill_file = self._agents_dir / "skillconteudo.txt"

        self._fallback_agent = (
            "Voce e VIVA, assistente principal do Fabio no SaaS. "
            "Atue com tom institucional, objetivo e pratico. "
            "Nao invente dados e confirme claramente as acoes executadas."
        )
        self._fallback_campaign_skill = (
            "Skill generate_campanha_neutra: "
            "seguir o pedido atual do usuario, sem padrao visual herdado."
        )

    @staticmethod
    def _safe_read_text(path: Path, fallback: str) -> str:
        if not path.exists():
            return fallback
        encodings = ("utf-8-sig", "utf-8", "cp1252", "latin-1")
        for encoding in encodings:
            try:
                content = path.read_text(encoding=encoding).strip()
                if content:
                    return content
            except Exception:
                continue
        return fallback

    @staticmethod
    def _discover_agents_dir() -> Path:
        here = Path(__file__).resolve()
        for parent in (here.parent,) + tuple(here.parents):
            candidate = parent / "agents"
            if (candidate / "AGENT.md").exists():
                return candidate
        # Last resort: assume repo root relative layout from current file.
        return here.parents[3] / "agents"

    def get_agent_prompt(self) -> str:
        return self._safe_read_text(self._agent_file, self._fallback_agent)

    def get_campaign_skill_prompt(self, max_chars: int = 2400) -> str:
        content = self._safe_read_text(self._campaign_skill_file, self._fallback_campaign_skill)
        if max_chars <= 0:
            return content
        if len(content) <= max_chars:
            return content
        return f"{content[:max_chars].rstrip()}..."

    def build_system_prompt(self, modo: Optional[str] = None) -> str:
        base = self.get_agent_prompt()
        # O "modo" vem da UI (abas laterais). Ele nao deve mudar a persona nem induzir "menus"
        # de capacidades. So usamos quando for contexto de marca/arte.
        allowed = {"FC", "REZETA", "LOGO"}
        normalized = str(modo or "").strip().upper()
        if normalized in allowed:
            return f"{base}\n\nContexto de marca atual: {normalized}."
        return base


viva_agent_profile_service = VivaAgentProfileService()
