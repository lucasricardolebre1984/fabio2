"""Loads the single agent profile and campaign skill from canonical folders."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from app.services.viva_brain_paths_service import viva_brain_paths_service


class VivaAgentProfileService:
    def __init__(self) -> None:
        # Canonical source (single folder): COFRE/persona-skills
        self._brain_paths = viva_brain_paths_service
        self._brain_paths.ensure_runtime_dirs()
        self._agent_file = self._brain_paths.persona_skills_dir / "AGENT.md"
        self._campaign_skill_files = [
            self._brain_paths.persona_skills_dir / "skill-generate-campanha-neutra.md",
            self._brain_paths.persona_skills_dir / "skillconteudo.txt",
        ]

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

    def get_agent_prompt(self) -> str:
        content = self._safe_read_text(self._agent_file, "")
        if content:
            return content
        return self._fallback_agent

    def get_campaign_skill_prompt(self, max_chars: int = 2400) -> str:
        content = ""
        for path in self._campaign_skill_files:
            content = self._safe_read_text(path, "")
            if content:
                break
        if not content:
            content = self._fallback_campaign_skill
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
