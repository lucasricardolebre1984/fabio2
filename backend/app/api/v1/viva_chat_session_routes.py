from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.api.v1.viva_schemas import (
    ChatSessionListResponse,
    ChatSessionStartRequest,
    ChatSnapshotResponse,
)
from app.models.user import User
from app.services.viva_chat_repository_service import viva_chat_repository_service
from app.services.viva_chat_session_service import (
    chat_session_from_row,
    create_chat_session as create_chat_session_record,
    ensure_chat_tables,
    get_latest_chat_session_row,
    load_chat_snapshot,
)
from app.services.viva_shared_service import _normalize_mode

router = APIRouter()


@router.get("/chat/snapshot", response_model=ChatSnapshotResponse)
async def get_chat_snapshot(
    session_id: Optional[UUID] = None,
    limit: int = 120,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await ensure_chat_tables(db)
        target_session_id = session_id
        if not target_session_id:
            latest = await get_latest_chat_session_row(db, current_user.id)
            target_session_id = latest.id if latest else None

        if not target_session_id:
            return ChatSnapshotResponse(session_id=None, modo=None, messages=[])

        return await load_chat_snapshot(
            db=db,
            user_id=current_user.id,
            session_id=target_session_id,
            limit=limit,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar historico: {str(exc)}")


@router.get("/chat/sessions", response_model=ChatSessionListResponse)
async def list_chat_sessions(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await ensure_chat_tables(db)
        total, rows, safe_page, safe_size = await viva_chat_repository_service.list_sessions_rows(
            db=db,
            user_id=current_user.id,
            page=page,
            page_size=page_size,
        )
        items = [chat_session_from_row(row) for row in rows]
        return ChatSessionListResponse(items=items, total=total, page=safe_page, page_size=safe_size)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao listar sessoes: {str(exc)}")


@router.post("/chat/session/new", response_model=ChatSnapshotResponse)
async def create_chat_session(
    payload: ChatSessionStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await ensure_chat_tables(db)
        session_id = await create_chat_session_record(db, current_user.id, payload.modo)
        return ChatSnapshotResponse(session_id=session_id, modo=_normalize_mode(payload.modo), messages=[])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao criar sessao: {str(exc)}")
