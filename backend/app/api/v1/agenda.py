"""Agenda routes."""
from datetime import datetime
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, require_operador
from app.models.user import User
from app.models.agenda import Agenda
from app.schemas.agenda import (
    EventoCreate,
    EventoUpdate,
    EventoResponse,
    EventoListResponse
)
from app.services.agenda_service import AgendaService
from app.services.google_calendar_service import google_calendar_service

router = APIRouter()
logger = logging.getLogger(__name__)


async def _sync_google_safe(db: AsyncSession, current_user_id: UUID, evento: Agenda) -> None:
    try:
        await google_calendar_service.sync_agenda_event(
            db,
            user_id=current_user_id,
            evento=evento,
        )
    except Exception as exc:
        logger.warning("agenda_google_sync_failed evento=%s erro=%s", str(evento.id), str(exc)[:180])


async def _delete_google_sync_safe(db: AsyncSession, current_user_id: UUID, evento_id: UUID) -> None:
    try:
        await google_calendar_service.delete_synced_agenda_event(
            db,
            user_id=current_user_id,
            agenda_event_id=evento_id,
        )
    except Exception as exc:
        logger.warning("agenda_google_delete_sync_failed evento=%s erro=%s", str(evento_id), str(exc)[:180])


@router.post("", response_model=EventoResponse, status_code=status.HTTP_201_CREATED)
async def create_evento(
    data: EventoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Create a new event."""
    service = AgendaService(db)
    evento = await service.create(data, current_user.id)
    await _sync_google_safe(db, current_user.id, evento)
    return evento


@router.get("", response_model=EventoListResponse)
async def list_eventos(
    inicio: Optional[datetime] = Query(None, description="Filter start date"),
    fim: Optional[datetime] = Query(None, description="Filter end date"),
    cliente_id: Optional[UUID] = Query(None, description="Filter by cliente"),
    concluido: Optional[bool] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """List events with pagination."""
    service = AgendaService(db)
    return await service.list(
        inicio=inicio,
        fim=fim,
        cliente_id=cliente_id,
        concluido=concluido,
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )


@router.get("/hoje", response_model=EventoListResponse)
async def get_eventos_hoje(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Get today's events."""
    service = AgendaService(db)
    return await service.get_hoje(user_id=current_user.id)


@router.get("/{evento_id}", response_model=EventoResponse)
async def get_evento(
    evento_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Get event by ID."""
    service = AgendaService(db)
    evento = await service.get_by_id(evento_id, user_id=current_user.id)
    
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    return evento


@router.put("/{evento_id}", response_model=EventoResponse)
async def update_evento(
    evento_id: UUID,
    data: EventoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Update event."""
    service = AgendaService(db)
    evento = await service.update(evento_id, data, user_id=current_user.id)
    
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    await _sync_google_safe(db, current_user.id, evento)
    return evento


@router.patch("/{evento_id}/concluir", response_model=EventoResponse)
async def concluir_evento(
    evento_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Mark event as completed."""
    service = AgendaService(db)
    evento = await service.concluir(evento_id, user_id=current_user.id)
    
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
    
    await _sync_google_safe(db, current_user.id, evento)
    return evento


@router.delete("/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evento(
    evento_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Delete event."""
    await _delete_google_sync_safe(db, current_user.id, evento_id)
    service = AgendaService(db)
    deleted = await service.delete(evento_id, user_id=current_user.id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado"
        )
