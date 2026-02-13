from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.api.v1.viva_schemas import (
    HandoffItem,
    HandoffListResponse,
    HandoffProcessResponse,
    HandoffScheduleRequest,
)
from app.models.user import User
from app.services.viva_handoff_service import viva_handoff_service
from app.services.viva_shared_service import _handoff_row_to_item

router = APIRouter()


@router.post("/handoff/schedule", response_model=HandoffItem)
async def schedule_handoff(
    payload: HandoffScheduleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        task_id = await viva_handoff_service.schedule_task(
            db=db,
            user_id=current_user.id,
            cliente_nome=payload.cliente_nome,
            cliente_numero=payload.cliente_numero,
            mensagem=payload.mensagem,
            scheduled_for=payload.scheduled_for,
            agenda_event_id=payload.agenda_event_id,
            meta=payload.meta or {},
        )
        rows = await db.execute(
            text(
                """
                SELECT id, user_id, agenda_event_id, cliente_nome, cliente_numero, mensagem,
                       scheduled_for, status, attempts, sent_at, last_error, meta_json, created_at, updated_at
                FROM viva_handoff_tasks
                WHERE id = :id AND user_id = :user_id
                """
            ),
            {"id": str(task_id), "user_id": str(current_user.id)},
        )
        row = rows.first()
        if not row:
            raise HTTPException(status_code=500, detail="Falha ao agendar handoff.")
        return _handoff_row_to_item(row)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao agendar handoff: {str(exc)}")


@router.get("/handoff", response_model=HandoffListResponse)
async def list_handoff(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        data = await viva_handoff_service.list_tasks(
            db=db,
            user_id=current_user.id,
            status=status,
            page=max(1, page),
            page_size=max(1, min(page_size, 200)),
        )
        return HandoffListResponse(
            items=[_handoff_row_to_item(row) for row in data["items"]],
            total=int(data["total"]),
            page=int(data["page"]),
            page_size=int(data["page_size"]),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao listar handoff: {str(exc)}")


@router.post("/handoff/process-due", response_model=HandoffProcessResponse)
async def process_handoff_due(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await viva_handoff_service.process_due_tasks(db=db, limit=limit)
        return HandoffProcessResponse(
            processed=int(result["processed"]),
            sent=int(result["sent"]),
            failed=int(result["failed"]),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao processar handoff: {str(exc)}")
