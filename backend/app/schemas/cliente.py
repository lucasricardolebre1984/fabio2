"""Cliente schemas."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from validate_docbr import CPF, CNPJ


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
    
    @field_validator("documento")
    @classmethod
    def validate_documento(cls, v: str, info) -> str:
        """Validate CPF/CNPJ."""
        values = info.data
        tipo = values.get("tipo_pessoa", "fisica")
        
        # Remove formatting
        doc = v.replace(".", "").replace("-", "").replace("/", "").strip()
        
        if tipo == "fisica":
            cpf = CPF()
            if not cpf.validate(doc):
                raise ValueError("CPF inválido")
        else:
            cnpj = CNPJ()
            if not cnpj.validate(doc):
                raise ValueError("CNPJ inválido")
        
        return doc


class ClienteCreate(ClienteBase):
    """Cliente creation schema."""
    pass


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
