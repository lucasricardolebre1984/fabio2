"""COFRE manifest loader (single source of truth for modules/endpoints)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.services.viva_brain_paths_service import viva_brain_paths_service


class CofreManifestService:
    def __init__(self) -> None:
        self._paths = viva_brain_paths_service
        self._paths.ensure_runtime_dirs()
        self._system_dir = self._paths.root_dir / "system"
        self._manifest_file = self._system_dir / "endpoints_manifest.json"

    def _fallback(self) -> Dict[str, Any]:
        return {
            "version": "fallback",
            "updated_at": None,
            "capabilities": [],
            "modules": [],
        }

    def load_manifest(self) -> Dict[str, Any]:
        try:
            self._system_dir.mkdir(parents=True, exist_ok=True)
            if not self._manifest_file.exists():
                return self._fallback()
            raw = self._manifest_file.read_text(encoding="utf-8")
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                return self._fallback()
            parsed.setdefault("capabilities", [])
            parsed.setdefault("modules", [])
            return parsed
        except Exception:
            return self._fallback()

    def capabilities(self) -> List[Dict[str, Any]]:
        data = self.load_manifest()
        items = data.get("capabilities") or []
        return [item for item in items if isinstance(item, dict)]

    def modules(self) -> List[Dict[str, Any]]:
        data = self.load_manifest()
        items = data.get("modules") or []
        return [item for item in items if isinstance(item, dict)]


cofre_manifest_service = CofreManifestService()
