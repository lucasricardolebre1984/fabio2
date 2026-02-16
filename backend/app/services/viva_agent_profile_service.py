"""Loads the single agent profile and campaign skill from canonical folders."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, Optional

from app.config import settings
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

    @staticmethod
    def _sha256(path: Path) -> str:
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            return digest
        except Exception:
            return ""

    def get_agent_prompt(self) -> str:
        content = self._safe_read_text(self._agent_file, "")
        if content:
            return content
        if bool(getattr(settings, "VIVA_AGENT_STRICT", True)):
            raise RuntimeError(
                "AGENT.md canonico ausente/vazio em COFRE/persona-skills. "
                "Modo estrito ativo para evitar drift de persona."
            )
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

    def get_profile_status(self) -> Dict[str, Any]:
        agent_exists = self._agent_file.exists()
        agent_content = self._safe_read_text(self._agent_file, "")
        using_fallback = not bool(agent_content)
        strict_mode = bool(getattr(settings, "VIVA_AGENT_STRICT", True))

        campaign_file = None
        for path in self._campaign_skill_files:
            if path.exists() and self._safe_read_text(path, ""):
                campaign_file = path
                break

        return {
            "cofre_root": str(self._brain_paths.root_dir),
            "persona_file": str(self._agent_file),
            "persona_exists": agent_exists,
            "persona_sha256": self._sha256(self._agent_file) if agent_exists else "",
            "persona_fallback_active": using_fallback,
            "strict_mode": strict_mode,
            "campaign_skill_file": str(campaign_file) if campaign_file else "",
            "campaign_skill_sha256": self._sha256(campaign_file) if campaign_file else "",
        }

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
