"""Canonical COFRE memory registry (file-based mirror per table/domain)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import json
import shutil
from urllib.parse import unquote, urlparse

from app.services.viva_brain_paths_service import viva_brain_paths_service


class CofreMemoryService:
    """Writes and reads memory mirrors under COFRE/memories/<table_name>/."""

    def __init__(self) -> None:
        self._paths = viva_brain_paths_service
        self._paths.ensure_runtime_dirs()
        self._known_tables = [
            "viva_chat_sessions",
            "viva_chat_messages",
            "viva_campanhas",
            "viva_handoff_tasks",
            "viva_memory_vectors",
            "redis_viva_memory_medium",
        ]
        self.ensure_known_table_dirs()

    @staticmethod
    def _safe_table_name(table_name: str) -> str:
        raw = str(table_name or "").strip().lower().replace("-", "_").replace(" ", "_")
        safe = "".join(ch for ch in raw if ch.isalnum() or ch == "_")
        return safe or "unknown_table"

    def _table_dir(self, table_name: str) -> Path:
        safe_name = self._safe_table_name(table_name)
        path = self._paths.memories_dir / safe_name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def ensure_table_dir(self, table_name: str) -> str:
        return self._table_dir(table_name).name

    def _daily_log_file(self, table_name: str) -> Path:
        day = datetime.utcnow().strftime("%Y-%m-%d")
        return self._table_dir(table_name) / f"{day}.jsonl"

    def _campaign_items_dir(self) -> Path:
        path = self._table_dir("viva_campanhas") / "items"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _campaign_item_file(self, campaign_id: str) -> Path:
        safe_id = "".join(ch for ch in str(campaign_id or "") if ch.isalnum() or ch in ("-", "_"))
        return self._campaign_items_dir() / f"{safe_id or 'unknown'}.json"

    def log_event(self, *, table_name: str, action: str, payload: Dict[str, Any]) -> None:
        record = {
            "ts": datetime.utcnow().isoformat(),
            "table": self._safe_table_name(table_name),
            "action": str(action or "").strip().lower() or "write",
            "payload": payload,
        }
        path = self._daily_log_file(table_name)
        try:
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            # Mirror log is observability-only and must not break API flow.
            return

    def list_tables(self) -> List[str]:
        self._paths.ensure_runtime_dirs()
        self.ensure_known_table_dirs()
        names: List[str] = []
        for child in self._paths.memories_dir.iterdir():
            if child.is_dir():
                names.append(child.name)
        names.sort()
        return names

    def tail_table(self, table_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        safe_limit = max(1, min(int(limit or 50), 300))
        table_dir = self._table_dir(table_name)
        files = sorted(table_dir.glob("*.jsonl"), reverse=True)
        items: List[Dict[str, Any]] = []
        for file_path in files:
            try:
                lines = file_path.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue
            for line in reversed(lines):
                if len(items) >= safe_limit:
                    break
                try:
                    parsed = json.loads(line)
                    if isinstance(parsed, dict):
                        items.append(parsed)
                except Exception:
                    continue
            if len(items) >= safe_limit:
                break
        items.reverse()
        return items

    def ensure_known_table_dirs(self) -> None:
        for table_name in self._known_tables:
            self._table_dir(table_name)

    def clear_table(self, table_name: str) -> int:
        table_dir = self._table_dir(table_name)
        removed = 0
        for file_path in table_dir.glob("*.jsonl"):
            try:
                file_path.unlink(missing_ok=True)
                removed += 1
            except Exception:
                continue
        return removed

    def save_campaign_snapshot(self, campaign_id: str, payload: Dict[str, Any]) -> bool:
        target = self._campaign_item_file(campaign_id)
        record = {
            "saved_at": datetime.utcnow().isoformat(),
            "campaign_id": str(campaign_id),
            "payload": payload or {},
        }
        try:
            target.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
            return True
        except Exception:
            return False

    def delete_campaign_snapshot(self, campaign_id: str) -> bool:
        target = self._campaign_item_file(campaign_id)
        try:
            target.unlink(missing_ok=True)
            return True
        except Exception:
            return False

    def clear_campaign_snapshots(self) -> int:
        items_dir = self._campaign_items_dir()
        removed = 0
        for file_path in items_dir.glob("*.json"):
            try:
                file_path.unlink(missing_ok=True)
                removed += 1
            except Exception:
                continue
        return removed

    def _resolve_local_path_from_image_url(self, image_url: str) -> Path | None:
        raw = str(image_url or "").strip()
        if not raw:
            return None

        if raw.startswith("file://"):
            parsed = urlparse(raw)
            if parsed.path:
                return Path(unquote(parsed.path))

        parsed = urlparse(raw)
        if parsed.scheme in ("http", "https"):
            marker = "/COFRE/memories/viva_campanhas/assets/"
            full_path = f"{parsed.path}"
            idx = full_path.find(marker)
            if idx >= 0:
                relative = full_path[idx + 1 :]
                base = self._paths.root_dir.parent
                return base / relative
            return None

        candidate = Path(raw)
        if candidate.is_absolute() or raw.startswith(".") or raw.startswith("/"):
            return candidate
        return None

    def delete_campaign_asset_from_url(self, image_url: str) -> bool:
        path = self._resolve_local_path_from_image_url(image_url)
        if not path:
            return False
        try:
            if path.exists() and path.is_file():
                path.unlink(missing_ok=True)
                return True
        except Exception:
            return False
        return False

    def clear_all_tables(self) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for table in self.list_tables():
            result[table] = self.clear_table(table)
        return result

    def clear_campaign_assets(self) -> int:
        assets_dir = self._table_dir("viva_campanhas") / "assets"
        if not assets_dir.exists():
            return 0
        removed = 0
        for child in assets_dir.iterdir():
            try:
                if child.is_file():
                    child.unlink(missing_ok=True)
                    removed += 1
                elif child.is_dir():
                    shutil.rmtree(child, ignore_errors=True)
                    removed += 1
            except Exception:
                continue
        return removed


cofre_memory_service = CofreMemoryService()
