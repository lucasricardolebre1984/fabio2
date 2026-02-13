from urllib.parse import quote_plus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_operador
from app.config import settings
from app.models.user import User
from app.services.agenda_service import AgendaService
from app.services.google_calendar_service import google_calendar_service

router = APIRouter()


@router.get("/connect-url")
async def google_calendar_connect_url(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    try:
        await google_calendar_service.ensure_tables(db)
        url = await google_calendar_service.build_connect_url(current_user.id)
        return {"url": url}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Erro Google Calendar: {str(exc)}")


@router.get("/callback")
async def google_calendar_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    frontend = settings.FRONTEND_BASE_URL.rstrip("/")
    try:
        await google_calendar_service.exchange_code_and_store(db, code=code, state=state)
        return RedirectResponse(url=f"{frontend}/agenda?google_calendar=connected", status_code=302)
    except Exception as exc:
        safe_detail = quote_plus(str(exc)[:120])
        return RedirectResponse(
            url=f"{frontend}/agenda?google_calendar=error&detail={safe_detail}",
            status_code=302,
        )


@router.get("/status")
async def google_calendar_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    return await google_calendar_service.get_status(db, current_user.id)


@router.post("/disconnect")
async def google_calendar_disconnect(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    await google_calendar_service.disconnect(db, current_user.id)
    return {"ok": True, "connected": False}


@router.post("/sync/agenda/{evento_id}")
async def google_calendar_sync_event(
    evento_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    agenda_service = AgendaService(db)
    evento = await agenda_service.get_by_id(evento_id, user_id=current_user.id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento nao encontrado")
    result = await google_calendar_service.sync_agenda_event(
        db,
        user_id=current_user.id,
        evento=evento,
    )
    return result
