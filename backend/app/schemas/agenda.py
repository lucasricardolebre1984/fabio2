"""Agenda schemas."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.agenda import EventoTipo


class EventoBase(BaseModel):
    """Base evento schema."""
    titulo: str = Field(..., min_length=2, max_length=255)
    descricao: Optional[str] = None
    tipo: EventoTipo = EventoTipo.OUTRO
    data_inicio: datetime
    data_fim: Optional[datetime] = None
    cliente_id: Optional[UUID] = None
    contrato_id: Optional[UUID] = None


class EventoCreate(EventoBase):
    """Evento creation schema."""
    pass


class EventoUpdate(BaseModel):
    """Evento update schema."""
    titulo: Optional[str] = Field(None, min_length=2, max_length=255)
    descricao: Optional[str] = None
    tipo: Optional[EventoTipo] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    cliente_id: Optional[UUID] = None
    contrato_id: Optional[UUID] = None
    concluido: Optional[bool] = None


class EventoInDB(EventoBase):
    """Evento in database schema."""
    id: UUID
    concluido: bool
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EventoResponse(EventoInDB):
    """Evento response schema."""
    cliente_nome: Optional[str] = None
    contrato_numero: Optional[str] = None


class EventoListResponse(BaseModel):
    """Evento list response."""
    items: List[EventoResponse]
    total: int
    page: int
    page_size: int
