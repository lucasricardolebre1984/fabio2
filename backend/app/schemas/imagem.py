"""Imagem schemas."""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class ImagemBase(BaseModel):
    """Base imagem schema."""
    nome: str = Field(..., min_length=1, max_length=255)
    descricao: Optional[str] = None
    tipo: str = "upload"  # upload, gerada_ia, documento, assinatura, comprovante


class ImagemCreate(ImagemBase):
    """Create imagem schema."""
    contrato_id: UUID


class ImagemGerarIA(BaseModel):
    """Gerar imagem via IA."""
    contrato_id: UUID
    prompt: str = Field(..., min_length=10, description="Descrição da imagem desejada")
    nome: str = Field(..., min_length=1, max_length=255)
    descricao: Optional[str] = None
    tamanho: str = "1024x1024"  # 1024x1024, 1792x1024, 1024x1792
    qualidade: str = "standard"  # standard, hd
    estilo: str = "vivid"  # vivid, natural


class ImagemProcessar(BaseModel):
    """Processar imagem existente com IA."""
    prompt: str = Field(..., min_length=5, description="O que fazer com a imagem")
    # Ex: "remover fundo", "melhorar resolução", "extrair texto", "assinar"


class ImagemResponse(ImagemBase):
    """Imagem response schema."""
    id: UUID
    contrato_id: UUID
    status: str
    nome_arquivo: str
    caminho_arquivo: str
    tamanho_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    prompt: Optional[str] = None
    url_externa: Optional[str] = None
    processamento_resultado: Dict[str, Any] = {}
    erro_mensagem: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ImagemList(BaseModel):
    """List imagens response."""
    items: list[ImagemResponse]
    total: int


class ImagemUploadResponse(BaseModel):
    """Upload response."""
    success: bool
    imagem: Optional[ImagemResponse] = None
    message: str
