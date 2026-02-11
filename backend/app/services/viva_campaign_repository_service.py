"""Persistence layer for VIVA campaign records."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class VivaCampaignRepositoryService:
    """Encapsulates SQL operations for campaign history."""

    async def ensure_table(self, db: AsyncSession) -> None:
        await db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS viva_campanhas (
                    id UUID PRIMARY KEY,
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    modo VARCHAR(32) NOT NULL,
                    titulo VARCHAR(255) NOT NULL,
                    briefing TEXT,
                    mensagem_original TEXT,
                    image_url TEXT NOT NULL,
                    overlay_json JSONB NOT NULL DEFAULT '{}'::jsonb,
                    meta_json JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        )
        await db.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_viva_campanhas_user_mode_created
                ON viva_campanhas(user_id, modo, created_at DESC)
                """
            )
        )
        await db.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_viva_campanhas_created
                ON viva_campanhas(created_at DESC)
                """
            )
        )

    async def save_campaign(
        self,
        db: AsyncSession,
        user_id: Optional[UUID],
        modo: str,
        titulo: str,
        briefing: Optional[str],
        mensagem_original: Optional[str],
        image_url: str,
        overlay: Optional[Dict[str, Any]],
        meta: Optional[Dict[str, Any]],
    ) -> Optional[UUID]:
        if not image_url:
            return None

        await self.ensure_table(db)
        campaign_id = uuid4()
        now = datetime.now(timezone.utc)
        await db.execute(
            text(
                """
                INSERT INTO viva_campanhas (
                    id, user_id, modo, titulo, briefing, mensagem_original, image_url,
                    overlay_json, meta_json, created_at, updated_at
                )
                VALUES (
                    :id, :user_id, :modo, :titulo, :briefing, :mensagem_original, :image_url,
                    CAST(:overlay_json AS JSONB), CAST(:meta_json AS JSONB), :created_at, :updated_at
                )
                """
            ),
            {
                "id": str(campaign_id),
                "user_id": str(user_id) if user_id else None,
                "modo": modo,
                "titulo": titulo,
                "briefing": briefing,
                "mensagem_original": mensagem_original,
                "image_url": image_url,
                "overlay_json": json.dumps(overlay or {}, ensure_ascii=False),
                "meta_json": json.dumps(meta or {}, ensure_ascii=False),
                "created_at": now,
                "updated_at": now,
            },
        )
        return campaign_id

    async def get_campaign_row(self, db: AsyncSession, campaign_id: UUID) -> Optional[Any]:
        result = await db.execute(
            text(
                """
                SELECT id, modo, titulo, briefing, mensagem_original, image_url, overlay_json, meta_json, created_at
                FROM viva_campanhas
                WHERE id = :id
                """
            ),
            {"id": str(campaign_id)},
        )
        return result.first()

    async def list_campaign_rows(
        self,
        db: AsyncSession,
        user_id: UUID,
        modo: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[Any], int]:
        await self.ensure_table(db)
        params: Dict[str, Any] = {
            "user_id": str(user_id),
            "limit": min(max(limit, 1), 200),
            "offset": max(offset, 0),
        }

        where_clause = "WHERE user_id = :user_id"
        if modo in ("FC", "REZETA"):
            where_clause += " AND modo = :modo"
            params["modo"] = modo

        rows_result = await db.execute(
            text(
                f"""
                SELECT id, modo, titulo, briefing, mensagem_original, image_url, overlay_json, meta_json, created_at
                FROM viva_campanhas
                {where_clause}
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        )
        rows = list(rows_result.fetchall())

        count_result = await db.execute(
            text(
                f"""
                SELECT COUNT(*) AS total
                FROM viva_campanhas
                {where_clause}
                """
            ),
            {k: v for k, v in params.items() if k in ("user_id", "modo")},
        )
        total = int(count_result.scalar() or 0)
        return rows, total

    async def get_campaign_row_by_id(
        self,
        db: AsyncSession,
        campaign_id: UUID,
        user_id: UUID,
    ) -> Optional[Any]:
        await self.ensure_table(db)
        result = await db.execute(
            text(
                """
                SELECT id, modo, titulo, briefing, mensagem_original, image_url, overlay_json, meta_json, created_at
                FROM viva_campanhas
                WHERE id = :id AND user_id = :user_id
                """
            ),
            {"id": str(campaign_id), "user_id": str(user_id)},
        )
        return result.first()

    async def get_recent_cast_ids(
        self,
        db: AsyncSession,
        user_id: Optional[UUID],
        modo: str,
        limit: int = 10,
    ) -> List[str]:
        if not user_id:
            return []
        await self.ensure_table(db)
        result = await db.execute(
            text(
                """
                SELECT overlay_json
                FROM viva_campanhas
                WHERE user_id = :user_id AND modo = :modo
                ORDER BY created_at DESC
                LIMIT :limit
                """
            ),
            {
                "user_id": str(user_id),
                "modo": modo,
                "limit": max(1, min(int(limit), 30)),
            },
        )
        rows = result.fetchall()
        cast_ids: List[str] = []
        for row in rows:
            overlay_raw = row.overlay_json if hasattr(row, "overlay_json") else None
            overlay = self._safe_json(overlay_raw, {})
            cast_profile = overlay.get("cast_profile") if isinstance(overlay, dict) else {}
            cast_id = str(cast_profile.get("id") if isinstance(cast_profile, dict) else "").strip()
            if cast_id and cast_id not in cast_ids:
                cast_ids.append(cast_id)
        return cast_ids

    async def get_recent_scene_ids(
        self,
        db: AsyncSession,
        user_id: Optional[UUID],
        modo: str,
        limit: int = 10,
    ) -> List[str]:
        if not user_id:
            return []
        await self.ensure_table(db)
        result = await db.execute(
            text(
                """
                SELECT overlay_json
                FROM viva_campanhas
                WHERE user_id = :user_id AND modo = :modo
                ORDER BY created_at DESC
                LIMIT :limit
                """
            ),
            {
                "user_id": str(user_id),
                "modo": modo,
                "limit": max(1, min(int(limit), 30)),
            },
        )
        rows = result.fetchall()
        scene_ids: List[str] = []
        for row in rows:
            overlay_raw = row.overlay_json if hasattr(row, "overlay_json") else None
            overlay = self._safe_json(overlay_raw, {})
            scene_profile = overlay.get("scene_profile") if isinstance(overlay, dict) else {}
            scene_id = str(scene_profile.get("id") if isinstance(scene_profile, dict) else "").strip()
            if scene_id and scene_id not in scene_ids:
                scene_ids.append(scene_id)
        return scene_ids

    @staticmethod
    def _safe_json(value: Any, fallback: Any) -> Any:
        if value is None:
            return fallback
        if isinstance(value, type(fallback)):
            return value
        if isinstance(fallback, dict) and isinstance(value, dict):
            return value
        if isinstance(fallback, list) and isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(fallback, dict) and isinstance(parsed, dict):
                    return parsed
                if isinstance(fallback, list) and isinstance(parsed, list):
                    return parsed
            except Exception:
                return fallback
        return fallback


viva_campaign_repository_service = VivaCampaignRepositoryService()
