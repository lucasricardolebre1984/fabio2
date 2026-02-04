"""
Modelo para armazenar conversas do WhatsApp
Integração com Evolution API + IA VIVA
"""
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from enum import Enum

from app.db.base import Base


class StatusConversa(str, Enum):
    ATIVA = "ativa"
    ARQUIVADA = "arquivada"
    AGUARDANDO = "aguardando"


class TipoOrigem(str, Enum):
    USUARIO = "usuario"      # Mensagem do cliente
    IA = "ia"                # Resposta da IA VIVA
    SISTEMA = "sistema"      # Notificação do sistema


class WhatsappConversa(Base):
    """Conversas ativas no WhatsApp"""
    __tablename__ = "whatsapp_conversas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Dados do contato
    numero_telefone = Column(String(20), nullable=False, index=True)
    nome_contato = Column(String(200), nullable=True)
    
    # Dados da instância Evolution
    instance_name = Column(String(100), nullable=False, default="Teste")
    
    # Status e contexto
    status = Column(SQLEnum(StatusConversa), default=StatusConversa.ATIVA)
    contexto_ia = Column(JSONB, default=dict)  # Contexto da conversa para a IA
    
    # Metadados
    ultima_mensagem_em = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    mensagens = relationship("WhatsappMensagem", back_populates="conversa", 
                             order_by="WhatsappMensagem.created_at", cascade="all, delete-orphan")
    
    class Config:
        from_attributes = True


class WhatsappMensagem(Base):
    """Mensagens individuais das conversas"""
    __tablename__ = "whatsapp_mensagens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversa_id = Column(UUID(as_uuid=True), ForeignKey("whatsapp_conversas.id", ondelete="CASCADE"), nullable=False)
    
    # Conteúdo
    tipo_origem = Column(SQLEnum(TipoOrigem), nullable=False)
    conteudo = Column(Text, nullable=False)
    
    # Metadados da mensagem
    message_id = Column(String(100), nullable=True)  # ID da mensagem no WhatsApp
    tipo_midia = Column(String(50), nullable=True)   # text, image, audio, etc
    url_midia = Column(String(500), nullable=True)   # URL se for mídia
    
    # Controle
    lida = Column(Boolean, default=False)
    enviada = Column(Boolean, default=True)  # False se falhou
    erro = Column(Text, nullable=True)       # Mensagem de erro se falhou
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    conversa = relationship("WhatsappConversa", back_populates="mensagens")
    
    class Config:
        from_attributes = True
