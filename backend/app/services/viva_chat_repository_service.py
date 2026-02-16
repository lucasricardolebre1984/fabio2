"""Persistence layer for VIVA chat sessions and messages."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.cofre_memory_service import cofre_memory_service


class VivaChatRepositoryService:
    """Encapsulates SQL operations for VIVA chat persistence."""

    async def ensure_tables(self, db: AsyncSession) -> None:
        await db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS viva_chat_sessions (
                    id UUID PRIMARY KEY,
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    modo VARCHAR(32),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    last_message_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        )
        await db.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_viva_chat_sessions_user_updated
                ON viva_chat_sessions(user_id, updated_at DESC)
                """
            )
        )
        await db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS viva_chat_messages (
                    id UUID PRIMARY KEY,
                    session_id UUID NOT NULL REFERENCES viva_chat_sessions(id) ON DELETE CASCADE,
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    tipo VARCHAR(16) NOT NULL,
                    conteudo TEXT NOT NULL,
                    modo VARCHAR(32),
                    anexos_json JSONB NOT NULL DEFAULT '[]'::jsonb,
                    meta_json JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        )
        await db.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_viva_chat_messages_session_created
                ON viva_chat_messages(session_id, created_at DESC)
                """
            )
        )

    async def create_session(self, db: AsyncSession, user_id: UUID, modo: Optional[str]) -> UUID:
        session_id = uuid4()
        now = datetime.now(timezone.utc)
        await db.execute(
            text(
                """
                INSERT INTO viva_chat_sessions (id, user_id, modo, created_at, updated_at, last_message_at)
                VALUES (:id, :user_id, :modo, :created_at, :updated_at, :last_message_at)
                """
            ),
            {
                "id": str(session_id),
                "user_id": str(user_id),
                "modo": modo,
                "created_at": now,
                "updated_at": now,
                "last_message_at": now,
            },
        )
        cofre_memory_service.log_event(
            table_name="viva_chat_sessions",
            action="insert",
            payload={
                "id": str(session_id),
                "user_id": str(user_id),
                "modo": modo,
            },
        )
        return session_id

    async def get_latest_session_row(self, db: AsyncSession, user_id: UUID) -> Optional[Any]:
        result = await db.execute(
            text(
                """
                SELECT id, modo
                FROM viva_chat_sessions
                WHERE user_id = :user_id
                ORDER BY updated_at DESC
                LIMIT 1
                """
            ),
            {"user_id": str(user_id)},
        )
        return result.first()

    async def resolve_session(
        self,
        db: AsyncSession,
        user_id: UUID,
        requested_session_id: Optional[UUID],
        modo: Optional[str],
    ) -> UUID:
        if requested_session_id:
            result = await db.execute(
                text(
                    """
                    SELECT id
                    FROM viva_chat_sessions
                    WHERE id = :id AND user_id = :user_id
                    LIMIT 1
                    """
                ),
                {"id": str(requested_session_id), "user_id": str(user_id)},
            )
            row = result.first()
            if row:
                await db.execute(
                    text(
                        """
                        UPDATE viva_chat_sessions
                        SET modo = COALESCE(:modo, modo),
                            updated_at = NOW()
                        WHERE id = :id
                        """
                    ),
                    {"id": str(requested_session_id), "modo": modo},
                )
                return requested_session_id

        latest = await self.get_latest_session_row(db=db, user_id=user_id)
        if latest:
            await db.execute(
                text(
                    """
                    UPDATE viva_chat_sessions
                    SET modo = COALESCE(:modo, modo),
                        updated_at = NOW()
                    WHERE id = :id
                    """
                ),
                {"id": str(latest.id), "modo": modo},
            )
            return latest.id

        return await self.create_session(db=db, user_id=user_id, modo=modo)

    async def append_message(
        self,
        db: AsyncSession,
        session_id: UUID,
        user_id: UUID,
        tipo: str,
        conteudo: str,
        modo: Optional[str] = None,
        anexos: Optional[List[Dict[str, Any]]] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        await db.execute(
            text(
                """
                INSERT INTO viva_chat_messages (
                    id, session_id, user_id, tipo, conteudo, modo, anexos_json, meta_json, created_at
                )
                VALUES (
                    :id, :session_id, :user_id, :tipo, :conteudo, :modo,
                    CAST(:anexos_json AS JSONB), CAST(:meta_json AS JSONB), NOW()
                )
                """
            ),
            {
                "id": str(uuid4()),
                "session_id": str(session_id),
                "user_id": str(user_id),
                "tipo": tipo,
                "conteudo": conteudo,
                "modo": modo,
                "anexos_json": json.dumps(anexos or [], ensure_ascii=False),
                "meta_json": json.dumps(meta or {}, ensure_ascii=False),
            },
        )
        cofre_memory_service.log_event(
            table_name="viva_chat_messages",
            action="insert",
            payload={
                "session_id": str(session_id),
                "user_id": str(user_id),
                "tipo": tipo,
                "modo": modo,
                "conteudo": conteudo,
                "anexos": anexos or [],
                "meta": meta or {},
            },
        )
        await db.execute(
            text(
                """
                UPDATE viva_chat_sessions
                SET modo = COALESCE(:modo, modo),
                    updated_at = NOW(),
                    last_message_at = NOW()
                WHERE id = :id AND user_id = :user_id
                """
            ),
            {
                "id": str(session_id),
                "user_id": str(user_id),
                "modo": modo,
            },
        )

    async def load_snapshot_rows(
        self,
        db: AsyncSession,
        user_id: UUID,
        session_id: UUID,
        limit: int,
    ) -> Tuple[Optional[Any], List[Any]]:
        session_result = await db.execute(
            text(
                """
                SELECT id, modo
                FROM viva_chat_sessions
                WHERE id = :session_id AND user_id = :user_id
                LIMIT 1
                """
            ),
            {"session_id": str(session_id), "user_id": str(user_id)},
        )
        session_row = session_result.first()
        if not session_row:
            return None, []

        safe_limit = min(max(limit, 1), 250)
        messages_result = await db.execute(
            text(
                """
                SELECT id, tipo, conteudo, modo, anexos_json, meta_json, created_at
                FROM (
                    SELECT m.id, m.tipo, m.conteudo, m.modo, m.anexos_json, m.meta_json, m.created_at
                    FROM viva_chat_messages m
                    WHERE m.session_id = :session_id AND m.user_id = :user_id
                    ORDER BY m.created_at DESC
                    LIMIT :limit
                ) recent
                ORDER BY created_at ASC
                """
            ),
            {
                "session_id": str(session_id),
                "user_id": str(user_id),
                "limit": safe_limit,
            },
        )
        return session_row, list(messages_result.fetchall())

    async def list_sessions_rows(
        self,
        db: AsyncSession,
        user_id: UUID,
        page: int,
        page_size: int,
    ) -> Tuple[int, List[Any], int, int]:
        safe_page = max(1, page)
        safe_size = max(1, min(page_size, 100))
        offset = (safe_page - 1) * safe_size

        total_result = await db.execute(
            text("SELECT COUNT(*) FROM viva_chat_sessions WHERE user_id = :user_id"),
            {"user_id": str(user_id)},
        )
        total = int(total_result.scalar() or 0)

        rows_result = await db.execute(
            text(
                """
                SELECT s.id, s.modo, s.created_at, s.updated_at, s.last_message_at,
                       COALESCE(msg.cnt, 0) AS message_count
                FROM viva_chat_sessions s
                LEFT JOIN (
                    SELECT session_id, COUNT(*) AS cnt
                    FROM viva_chat_messages
                    WHERE user_id = :user_id
                    GROUP BY session_id
                ) msg ON msg.session_id = s.id
                WHERE s.user_id = :user_id
                ORDER BY s.updated_at DESC
                OFFSET :offset LIMIT :limit
                """
            ),
            {"user_id": str(user_id), "offset": offset, "limit": safe_size},
        )
        return total, list(rows_result.fetchall()), safe_page, safe_size


viva_chat_repository_service = VivaChatRepositoryService()
