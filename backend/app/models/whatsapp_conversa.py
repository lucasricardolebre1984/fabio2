"""
Modelo para armazenar conversas do WhatsApp.
Integracao com Evolution API + IA VIVA.
"""
from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def _enum_values(enum_cls):
    return [member.value for member in enum_cls]


class StatusConversa(str, Enum):
    ATIVA = "ativa"
    ARQUIVADA = "arquivada"
    AGUARDANDO = "aguardando"


class TipoOrigem(str, Enum):
    USUARIO = "usuario"
    IA = "ia"
    SISTEMA = "sistema"


class WhatsappConversa(Base):
    """Conversas ativas no WhatsApp."""

    __tablename__ = "whatsapp_conversas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    numero_telefone = Column(String(20), nullable=False, index=True)
    nome_contato = Column(String(200), nullable=True)
    instance_name = Column(String(100), nullable=False, default="Teste")

    status = Column(
        SQLEnum(
            StatusConversa,
            name="status_conversa_enum",
            native_enum=False,
            values_callable=_enum_values,
            validate_strings=True,
        ),
        default=StatusConversa.ATIVA,
        nullable=False,
    )
    contexto_ia = Column(JSON, default=dict)

    ultima_mensagem_em = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    mensagens = relationship(
        "WhatsappMensagem",
        back_populates="conversa",
        order_by="WhatsappMensagem.created_at",
        cascade="all, delete-orphan",
    )

    class Config:
        from_attributes = True


class WhatsappMensagem(Base):
    """Mensagens individuais das conversas."""

    __tablename__ = "whatsapp_mensagens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("whatsapp_conversas.id", ondelete="CASCADE"),
        nullable=False,
    )

    tipo_origem = Column(
        SQLEnum(
            TipoOrigem,
            name="tipo_origem_enum",
            native_enum=False,
            values_callable=_enum_values,
            validate_strings=True,
        ),
        nullable=False,
    )
    conteudo = Column(Text, nullable=False)

    message_id = Column(String(100), nullable=True)
    tipo_midia = Column(String(50), nullable=True)
    url_midia = Column(String(500), nullable=True)

    lida = Column(Boolean, default=False)
    enviada = Column(Boolean, default=True)
    erro = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    conversa = relationship("WhatsappConversa", back_populates="mensagens")

    class Config:
        from_attributes = True
