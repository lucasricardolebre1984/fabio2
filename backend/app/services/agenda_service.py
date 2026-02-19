"""Agenda service - Business logic for calendar events."""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import select, desc, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agenda import Agenda, EventoTipo
from app.schemas.agenda import EventoCreate, EventoUpdate


class AgendaService:
    """Service for agenda management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _normalize_event_datetime(value: Optional[datetime]) -> Optional[datetime]:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=ZoneInfo("America/Sao_Paulo"))
        return value
    
    async def create(self, data: EventoCreate, user_id: UUID) -> Agenda:
        """Create a new event."""
        evento = Agenda(
            titulo=data.titulo,
            descricao=data.descricao,
            tipo=data.tipo,
            data_inicio=self._normalize_event_datetime(data.data_inicio),
            data_fim=self._normalize_event_datetime(data.data_fim),
            cliente_id=data.cliente_id,
            contrato_id=data.contrato_id,
            concluido=False,
            created_by=user_id
        )
        
        self.db.add(evento)
        await self.db.commit()
        await self.db.refresh(evento)
        
        return evento
    
    async def list(
        self,
        inicio: Optional[datetime] = None,
        fim: Optional[datetime] = None,
        cliente_id: Optional[UUID] = None,
        concluido: Optional[bool] = None,
        user_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """List events with pagination."""
        query = select(Agenda).order_by(desc(Agenda.data_inicio))
        
        if inicio:
            query = query.where(Agenda.data_inicio >= inicio)
        if fim:
            query = query.where(Agenda.data_inicio < fim)
        if cliente_id:
            query = query.where(Agenda.cliente_id == cliente_id)
        if concluido is not None:
            query = query.where(Agenda.concluido == concluido)
        if user_id:
            query = query.where(Agenda.created_by == user_id)
        
        # Count total
        count_result = await self.db.execute(
            select(func.count(Agenda.id)).select_from(query.subquery())
        )
        total = count_result.scalar()
        
        # Paginate
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return {
            "items": list(items),
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    async def get_by_id(self, evento_id: UUID, user_id: Optional[UUID] = None) -> Optional[Agenda]:
        """Get event by ID."""
        query = select(Agenda).where(Agenda.id == evento_id)
        if user_id:
            query = query.where(Agenda.created_by == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update(self, evento_id: UUID, data: EventoUpdate, user_id: Optional[UUID] = None) -> Optional[Agenda]:
        """Update event."""
        query = select(Agenda).where(Agenda.id == evento_id)
        if user_id:
            query = query.where(Agenda.created_by == user_id)
        result = await self.db.execute(query)
        evento = result.scalar_one_or_none()
        
        if not evento:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if field in {"data_inicio", "data_fim"}:
                value = self._normalize_event_datetime(value)
            setattr(evento, field, value)
        
        await self.db.commit()
        await self.db.refresh(evento)
        
        return evento
    
    async def concluir(self, evento_id: UUID, user_id: Optional[UUID] = None) -> Optional[Agenda]:
        """Mark event as completed."""
        return await self.update(evento_id, EventoUpdate(concluido=True), user_id=user_id)
    
    async def delete(self, evento_id: UUID, user_id: Optional[UUID] = None) -> bool:
        """Delete event."""
        query = select(Agenda).where(Agenda.id == evento_id)
        if user_id:
            query = query.where(Agenda.created_by == user_id)
        result = await self.db.execute(query)
        evento = result.scalar_one_or_none()
        
        if not evento:
            return False
        
        await self.db.delete(evento)
        await self.db.commit()
        
        return True
    
    async def get_hoje(self, user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get today's events."""
        hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).replace(hour=0, minute=0, second=0, microsecond=0)
        amanha = hoje + timedelta(days=1)
        
        return await self.list(
            inicio=hoje,
            fim=amanha,
            user_id=user_id,
            page=1,
            page_size=100
        )
