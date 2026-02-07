"""Cliente schemas."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from validate_docbr import CPF, CNPJ


def _normalize_document(documento: str) -> str:
    return documento.replace(".", "").replace("-", "").replace("/", "").strip()


class ClienteBase(BaseModel):
    """Base cliente schema."""

    nome: str = Field(..., min_length=2, max_length=255)
    tipo_pessoa: str = Field(default="fisica", pattern="^(fisica|juridica)$")
    documento: str = Field(..., min_length=11, max_length=20)
    email: str = Field(..., max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    endereco: Optional[str] = None
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=10)
    observacoes: Optional[str] = None


class ClienteCreate(ClienteBase):
    """Cliente creation schema."""

    @field_validator("documento")
    @classmethod
    def validate_documento(cls, value: str, info) -> str:
        values = info.data
        tipo = values.get("tipo_pessoa", "fisica")
        doc = _normalize_document(value)

        if tipo == "fisica":
            if not CPF().validate(doc):
                raise ValueError("CPF invalido")
        else:
            if not CNPJ().validate(doc):
                raise ValueError("CNPJ invalido")

        return doc


class ClienteUpdate(BaseModel):
    """Cliente update schema."""

    nome: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    endereco: Optional[str] = None
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=10)
    observacoes: Optional[str] = None


class ClienteInDB(ClienteBase):
    """Cliente in database schema."""

    id: UUID
    primeiro_contrato_em: Optional[datetime] = None
    ultimo_contrato_em: Optional[datetime] = None
    total_contratos: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClienteResponse(ClienteInDB):
    """Cliente response schema."""

    pass


class ClienteListResponse(BaseModel):
    """Cliente list response."""

    items: List[ClienteResponse]
    total: int
    page: int
    page_size: int
