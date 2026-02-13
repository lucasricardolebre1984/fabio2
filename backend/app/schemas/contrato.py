"""Contrato schemas."""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.contrato import ContratoStatus


class ContratoBase(BaseModel):
    """Base contrato schema."""
    template_id: str
    
    # Dados do contratante
    contratante_nome: str = Field(..., min_length=2, max_length=255)
    contratante_documento: str = Field(..., min_length=11, max_length=20)
    contratante_email: str = Field(..., max_length=255)
    contratante_telefone: Optional[str] = Field(None, max_length=20)
    contratante_endereco: str
    
    # Valores
    valor_total: Decimal = Field(..., decimal_places=2)
    valor_entrada: Decimal = Field(..., decimal_places=2)
    qtd_parcelas: int = Field(..., ge=1, le=99)
    valor_parcela: Decimal = Field(..., decimal_places=2)
    prazo_1: int = Field(..., ge=1, le=999)
    prazo_2: int = Field(..., ge=1, le=999)
    
    # Assinatura
    local_assinatura: str = Field(default="Ribeirão Preto/SP")
    data_assinatura: str  # DD/MM/YYYY


class ContratoCreate(ContratoBase):
    """Contrato creation schema."""
    # Valores por extenso (calculados automaticamente pelo backend)
    valor_total_extenso: Optional[str] = None
    valor_entrada_extenso: Optional[str] = None
    qtd_parcelas_extenso: Optional[str] = None
    valor_parcela_extenso: Optional[str] = None
    prazo_1_extenso: Optional[str] = None
    prazo_2_extenso: Optional[str] = None
    
    # Dados extras do template
    dados_extras: Optional[Dict[str, Any]] = None


class ContratoUpdate(BaseModel):
    """Contrato update schema."""
    status: Optional[ContratoStatus] = None
    dados_extras: Optional[Dict[str, Any]] = None
    pdf_url: Optional[str] = None


class ContratoInDB(ContratoBase):
    """Contrato in database schema."""
    id: UUID
    numero: str
    status: ContratoStatus
    template_nome: str
    
    # Valores por extenso
    valor_total_extenso: str
    valor_entrada_extenso: str
    qtd_parcelas_extenso: str
    valor_parcela_extenso: str
    prazo_1_extenso: str
    prazo_2_extenso: str
    
    # Relacionamentos
    cliente_id: Optional[UUID] = None
    cliente_nome: Optional[str] = None
    
    # Metadados
    dados_extras: Optional[Dict[str, Any]] = None
    pdf_url: Optional[str] = None
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ContratoResponse(ContratoInDB):
    """Contrato response schema."""
    pass


class ContratoListResponse(BaseModel):
    """Contrato list response."""
    items: List[ContratoResponse]
    total: int
    page: int
    page_size: int


# Template schemas
class ContratoTemplateResponse(BaseModel):
    """Contrato template response."""
    id: str
    nome: str
    tipo: str
    categoria: Optional[str] = None
    subtitulo: Optional[str] = None
    descricao: Optional[str] = None
    versao: str
    ativo: bool
    campos: List[Dict[str, Any]]
    secoes: List[Dict[str, Any]]
    clausulas: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ContratoPreviewRequest(BaseModel):
    """Contrato preview request."""
    template_id: str
    dados: Dict[str, Any]


class ContratoPreviewResponse(BaseModel):
    """Contrato preview response."""
    html: str
    dados_completos: Dict[str, Any]
