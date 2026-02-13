"""Sessao e historico de chat VIVA (persistencia/snapshot)."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.viva_schemas import ChatMessageItem, ChatSessionItem, ChatSnapshotResponse, MediaItem
from app.services.viva_chat_repository_service import viva_chat_repository_service
from app.services.viva_shared_service import _normalize_mode


async def ensure_chat_tables(db: AsyncSession) -> None:
    await viva_chat_repository_service.ensure_tables(db)


def safe_json(value: Any, fallback: Any) -> Any:
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


def serialize_media_items(items: Optional[List[MediaItem]]) -> List[Dict[str, Any]]:
    if not items:
        return []
    payload: List[Dict[str, Any]] = []
    for item in items:
        if isinstance(item, MediaItem):
            payload.append(item.model_dump(exclude_none=True))
        elif isinstance(item, dict):
            payload.append(item)
    return payload


async def create_chat_session(db: AsyncSession, user_id: UUID, modo: Optional[str]) -> UUID:
    return await viva_chat_repository_service.create_session(
        db=db,
        user_id=user_id,
        modo=_normalize_mode(modo),
    )


async def get_latest_chat_session_row(db: AsyncSession, user_id: UUID) -> Optional[Any]:
    return await viva_chat_repository_service.get_latest_session_row(db=db, user_id=user_id)


async def resolve_chat_session(
    db: AsyncSession,
    user_id: UUID,
    requested_session_id: Optional[UUID],
    modo: Optional[str],
) -> UUID:
    return await viva_chat_repository_service.resolve_session(
        db=db,
        user_id=user_id,
        requested_session_id=requested_session_id,
        modo=_normalize_mode(modo),
    )


async def append_chat_message(
    db: AsyncSession,
    session_id: UUID,
    user_id: UUID,
    tipo: str,
    conteudo: str,
    modo: Optional[str] = None,
    anexos: Optional[List[Dict[str, Any]]] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    await viva_chat_repository_service.append_message(
        db=db,
        session_id=session_id,
        user_id=user_id,
        tipo=tipo,
        conteudo=conteudo,
        modo=_normalize_mode(modo),
        anexos=anexos or [],
        meta=meta or {},
    )


def chat_message_from_row(row: Any) -> ChatMessageItem:
    return ChatMessageItem(
        id=row.id,
        tipo=row.tipo,
        conteudo=row.conteudo,
        modo=row.modo,
        anexos=safe_json(row.anexos_json, []),
        meta=safe_json(row.meta_json, {}),
        created_at=row.created_at,
    )


def chat_session_from_row(row: Any) -> ChatSessionItem:
    return ChatSessionItem(
        id=row.id,
        modo=row.modo,
        message_count=int(row.message_count or 0),
        created_at=row.created_at,
        updated_at=row.updated_at,
        last_message_at=row.last_message_at,
    )


async def load_chat_snapshot(
    db: AsyncSession,
    user_id: UUID,
    session_id: UUID,
    limit: int,
) -> ChatSnapshotResponse:
    session_row, message_rows = await viva_chat_repository_service.load_snapshot_rows(
        db=db,
        user_id=user_id,
        session_id=session_id,
        limit=limit,
    )
    if not session_row:
        return ChatSnapshotResponse(session_id=None, modo=None, messages=[])
    messages = [chat_message_from_row(row) for row in message_rows]
    return ChatSnapshotResponse(session_id=session_row.id, modo=session_row.modo, messages=messages)


def context_from_snapshot(snapshot: ChatSnapshotResponse) -> List[Dict[str, Any]]:
    contexto: List[Dict[str, Any]] = []
    for item in snapshot.messages:
        contexto.append(
            {
                "id": str(item.id),
                "tipo": item.tipo,
                "conteudo": item.conteudo,
                "modo": item.modo,
                "anexos": item.anexos,
                "meta": item.meta,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
        )
    return contexto
