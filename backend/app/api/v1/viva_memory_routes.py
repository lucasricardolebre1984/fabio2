from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.api.v1.viva_schemas import (
    VivaMemoryReindexResponse,
    VivaMemorySearchItem,
    VivaMemorySearchResponse,
    VivaMemoryStatusResponse,
)
from app.models.user import User
from app.services.viva_memory_service import viva_memory_service
from app.services.viva_shared_service import _normalize_mode

router = APIRouter()


@router.get("/memory/status", response_model=VivaMemoryStatusResponse)
async def get_memory_status(
    session_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        status = await viva_memory_service.memory_status(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
        )
        return VivaMemoryStatusResponse(**status)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar memoria: {str(exc)}")


@router.get("/memory/search", response_model=VivaMemorySearchResponse)
async def search_memory(
    q: str,
    limit: int = 6,
    modo: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = str(q or "").strip()
    if not query:
        return VivaMemorySearchResponse(items=[], total=0)

    try:
        items_raw = await viva_memory_service.search_long_memory(
            db=db,
            user_id=current_user.id,
            query=query,
            modo=_normalize_mode(modo),
            limit=limit,
        )
        items = [
            VivaMemorySearchItem(
                id=UUID(str(item["id"])),
                tipo=str(item["tipo"]),
                modo=item.get("modo"),
                conteudo=str(item["conteudo"]),
                score=float(item["score"]),
                created_at=item["created_at"],
            )
            for item in items_raw
        ]
        return VivaMemorySearchResponse(items=items, total=len(items))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar memoria: {str(exc)}")


@router.post("/memory/reindex", response_model=VivaMemoryReindexResponse)
async def reindex_memory(
    limit: int = 400,
    session_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await viva_memory_service.reindex_from_chat_messages(
            db=db,
            user_id=current_user.id,
            limit=limit,
            session_id=session_id,
        )
        return VivaMemoryReindexResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao reindexar memoria: {str(exc)}")
