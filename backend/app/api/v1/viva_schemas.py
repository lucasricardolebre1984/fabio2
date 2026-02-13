"""Schemas da VIVA (contratos HTTP compartilhados entre rotas)."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    mensagem: str
    contexto: List[Dict[str, Any]] = []
    prompt_extra: Optional[str] = None
    modo: Optional[str] = None
    session_id: Optional[UUID] = None


class MediaItem(BaseModel):
    tipo: str
    url: str
    nome: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    resposta: str
    midia: Optional[List[MediaItem]] = None
    session_id: Optional[UUID] = None


class ChatMessageItem(BaseModel):
    id: UUID
    tipo: str
    conteudo: str
    modo: Optional[str] = None
    anexos: List[Dict[str, Any]] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ChatSnapshotResponse(BaseModel):
    session_id: Optional[UUID] = None
    modo: Optional[str] = None
    messages: List[ChatMessageItem] = Field(default_factory=list)


class ChatSessionItem(BaseModel):
    id: UUID
    modo: Optional[str] = None
    message_count: int = 0
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime


class ChatSessionListResponse(BaseModel):
    items: List[ChatSessionItem]
    total: int
    page: int
    page_size: int


class ChatSessionStartRequest(BaseModel):
    modo: Optional[str] = None


class CampanhaSaveRequest(BaseModel):
    modo: str
    image_url: str
    titulo: Optional[str] = None
    briefing: Optional[str] = None
    mensagem_original: Optional[str] = None
    overlay: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


class CampanhaItem(BaseModel):
    id: UUID
    modo: str
    titulo: str
    briefing: Optional[str] = None
    mensagem_original: Optional[str] = None
    image_url: str
    overlay: Dict[str, Any] = {}
    meta: Dict[str, Any] = {}
    created_at: datetime


class CampanhaListResponse(BaseModel):
    items: List[CampanhaItem]
    total: int


class CampanhaResetResponse(BaseModel):
    deleted: int
    modo: Optional[str] = None
    message: str


class VivaCapabilitiesResponse(BaseModel):
    items: List[Dict[str, Any]]


class HandoffScheduleRequest(BaseModel):
    cliente_numero: str
    mensagem: str
    scheduled_for: datetime
    cliente_nome: Optional[str] = None
    agenda_event_id: Optional[UUID] = None
    meta: Optional[Dict[str, Any]] = None


class HandoffItem(BaseModel):
    id: UUID
    user_id: UUID
    agenda_event_id: Optional[UUID] = None
    cliente_nome: Optional[str] = None
    cliente_numero: str
    mensagem: str
    scheduled_for: datetime
    status: str
    attempts: int = 0
    sent_at: Optional[datetime] = None
    last_error: Optional[str] = None
    meta_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None


class HandoffListResponse(BaseModel):
    items: List[HandoffItem]
    total: int
    page: int
    page_size: int


class HandoffProcessResponse(BaseModel):
    processed: int
    sent: int
    failed: int


class VivaMemoryStatusResponse(BaseModel):
    vector_enabled: bool
    redis_enabled: bool
    total_vectors: int
    medium_items: int
    embedding_model: str


class VivaMemorySearchItem(BaseModel):
    id: UUID
    tipo: str
    modo: Optional[str] = None
    conteudo: str
    score: float
    created_at: datetime


class VivaMemorySearchResponse(BaseModel):
    items: List[VivaMemorySearchItem]
    total: int


class VivaMemoryReindexResponse(BaseModel):
    processed: int
    indexed: int


class ImageAnalysisRequest(BaseModel):
    image_base64: str
    prompt: str = "Descreva esta imagem em detalhes"


class ImageGenerationRequest(BaseModel):
    prompt: str
    width: int = 1024
    height: int = 1024


class VideoGenerationRequest(BaseModel):
    prompt: str
    size: str = "1920x1080"
    fps: int = 30
    duration: int = 5
    quality: str = "quality"
    with_audio: bool = True
