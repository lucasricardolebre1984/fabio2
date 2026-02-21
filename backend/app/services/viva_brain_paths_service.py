"""Canonical path resolver for VIVA brain assets (persona, skills, memories)."""

from __future__ import annotations

from pathlib import Path

from app.config import settings


class VivaBrainPathsService:
    """Resolves a single canonical folder for persona/skills and memory files."""

    def __init__(self) -> None:
        self.root_dir = self._discover_root_dir()
        self.persona_skills_dir = self.root_dir / "persona-skills"
        self.viva_persona_dir = self.persona_skills_dir / "viva"
        self.viviane_persona_dir = self.persona_skills_dir / "viviane"
        self.viva_agent_file = self.viva_persona_dir / "AGENT.md"
        self.viviane_agent_file = self.viviane_persona_dir / "AGENT.md"
        self.memories_dir = self.root_dir / "memories"

    @staticmethod
    def _marker_exists(path: Path) -> bool:
        viva_v2 = path / "persona-skills" / "viva" / "AGENT.md"
        viviane_v2 = path / "persona-skills" / "viviane" / "AGENT.md"
        return viva_v2.exists() and viviane_v2.exists()

    def _discover_root_dir(self) -> Path:
        raw = str(getattr(settings, "VIVA_BRAIN_ROOT", "COFRE") or "COFRE").strip()
        requested = Path(raw)
        if requested.is_absolute():
            return requested

        here = Path(__file__).resolve()
        for parent in (here.parent,) + tuple(here.parents):
            candidate = parent / requested
            if self._marker_exists(candidate):
                return candidate

        # fallback: infer repo root from backend/app/services/*
        inferred_repo_root = here.parents[3]
        return inferred_repo_root / requested

    def ensure_runtime_dirs(self) -> None:
        self.persona_skills_dir.mkdir(parents=True, exist_ok=True)
        self.viva_persona_dir.mkdir(parents=True, exist_ok=True)
        self.viviane_persona_dir.mkdir(parents=True, exist_ok=True)
        self.memories_dir.mkdir(parents=True, exist_ok=True)


viva_brain_paths_service = VivaBrainPathsService()
