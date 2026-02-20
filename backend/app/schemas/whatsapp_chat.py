"""
Schemas para API de Chat WhatsApp
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
from uuid import UUID


class MensagemResponse(BaseModel):
    id: UUID
    tipo_origem: str
    conteudo: str
    lida: bool
    enviada: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ConversaResponse(BaseModel):
    id: UUID
    numero_telefone: str
    nome_contato: Optional[str]
    instance_name: str
    status: str
    ultima_mensagem_em: Optional[datetime]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ConversaDetalheResponse(BaseModel):
    id: UUID
    numero_telefone: str
    nome_contato: Optional[str]
    instance_name: str
    status: str
    contexto_ia: dict
    ultima_mensagem_em: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    mensagens: List[MensagemResponse]
    
    model_config = ConfigDict(from_attributes=True)


class ConversaCreate(BaseModel):
    numero_telefone: str
    nome_contato: Optional[str] = None
    instance_name: str = "Teste"


class EnviarMensagemRequest(BaseModel):
    conteudo: str


class BindNumeroRequest(BaseModel):
    numero_real: str
