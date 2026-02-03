"""Agenda model."""
from sqlalchemy import Column, String, ForeignKey, Text, Enum, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel


class EventoTipo(str, enum.Enum):
    """Event types."""
    REUNIAO = "reuniao"
    LIGACAO = "ligacao"
    PRAZO = "prazo"
    OUTRO = "outro"


class Agenda(BaseModel):
    """Agenda/Evento model."""
    
    __tablename__ = "agenda"
    
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    tipo = Column(Enum(EventoTipo), default=EventoTipo.OUTRO, nullable=False)
    
    # Datas
    data_inicio = Column(DateTime(timezone=True), nullable=False)
    data_fim = Column(DateTime(timezone=True), nullable=True)
    
    # Vinculações
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=True)
    cliente = relationship("Cliente", foreign_keys=[cliente_id])
    
    contrato_id = Column(UUID(as_uuid=True), ForeignKey("contratos.id"), nullable=True)
    contrato = relationship("Contrato", foreign_keys=[contrato_id])
    
    # Status
    concluido = Column(Boolean, default=False, nullable=False)
    
    # Usuário que criou
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    usuario = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self) -> str:
        return f"<Agenda {self.titulo}>"
