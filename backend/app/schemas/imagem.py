"""Imagem schemas."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.imagem import TipoImagem, FormatoImagem, StatusImagem


class ImagemBase(BaseModel):
    """Base imagem schema."""
    nome: str = Field(..., min_length=1, max_length=255)
    descricao: Optional[str] = None
    formato: FormatoImagem = Field(default=FormatoImagem.QUADRADO)


class ImagemCreate(BaseModel):
    """Imagem creation schema."""
    nome: str = Field(..., min_length=1, max_length=255)
    descricao: Optional[str] = None
    formato: FormatoImagem = Field(default=FormatoImagem.QUADRADO)
    prompt: Optional[str] = None  # Para imagens geradas


class ImagemUpdate(BaseModel):
    """Imagem update schema."""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = None
    status: Optional[StatusImagem] = None


class ImagemInDB(ImagemBase):
    """Imagem in database schema."""
    id: UUID
    url: str
    tipo: TipoImagem
    status: StatusImagem
    prompt: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ImagemResponse(ImagemInDB):
    """Imagem response schema."""
    pass


class ImagemListResponse(BaseModel):
    """Imagem list response."""
    items: List[ImagemResponse]
    total: int


# Request/Response específicos
class GerarImagemRequest(BaseModel):
    """Request para gerar imagem via IA."""
    prompt: str = Field(..., min_length=10, description="Prompt para geração da imagem")
    formato: FormatoImagem = Field(default=FormatoImagem.QUADRADO)
    nome: Optional[str] = Field(None, description="Nome opcional para a imagem")


class GerarImagemResponse(BaseModel):
    """Response da geração de imagem."""
    success: bool
    imagem: Optional[ImagemResponse] = None
    message: str


class UploadImagemResponse(BaseModel):
    """Response do upload de imagem."""
    success: bool
    imagem: Optional[ImagemResponse] = None
    message: str


class AprovarImagemResponse(BaseModel):
    """Response da aprovação de imagem."""
    success: bool
    nova_url: Optional[str] = None
    message: str
