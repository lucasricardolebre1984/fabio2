"""Contrato model."""
from sqlalchemy import Column, String, Numeric, ForeignKey, Text, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.db.base import BaseModel


class ContratoStatus(str, enum.Enum):
    """Contrato status."""
    RASCUNHO = "rascunho"
    FINALIZADO = "finalizado"
    ENVIADO = "enviado"
    CANCELADO = "cancelado"


class Contrato(BaseModel):
    """Contrato model."""
    
    __tablename__ = "contratos"
    
    # Identificação
    numero = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(Enum(ContratoStatus), default=ContratoStatus.RASCUNHO, nullable=False)
    
    # Template
    template_id = Column(String(50), nullable=False)
    template_nome = Column(String(255), nullable=False)
    
    # Cliente (contratante)
    cliente_id = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=True)
    cliente = relationship("Cliente", back_populates="contratos")
    
    # Dados do contratante
    contratante_nome = Column(String(255), nullable=False)
    contratante_documento = Column(String(20), nullable=False)
    contratante_email = Column(String(255), nullable=False)
    contratante_telefone = Column(String(20), nullable=True)
    contratante_endereco = Column(Text, nullable=False)
    
    # Valores
    valor_total = Column(Numeric(12, 2), nullable=False)
    valor_total_extenso = Column(String(500), nullable=False)
    
    valor_entrada = Column(Numeric(12, 2), nullable=False)
    valor_entrada_extenso = Column(String(500), nullable=False)
    
    qtd_parcelas = Column(Integer, nullable=False)
    qtd_parcelas_extenso = Column(String(100), nullable=False)
    
    valor_parcela = Column(Numeric(12, 2), nullable=False)
    valor_parcela_extenso = Column(String(500), nullable=False)
    
    prazo_1 = Column(Integer, nullable=False)
    prazo_1_extenso = Column(String(100), nullable=False)
    
    prazo_2 = Column(Integer, nullable=False)
    prazo_2_extenso = Column(String(100), nullable=False)
    
    # Assinatura
    local_assinatura = Column(String(255), nullable=False)
    data_assinatura = Column(String(20), nullable=False)
    
    # Dados adicionais (campos extras do template)
    dados_extras = Column(JSONB, default=dict, nullable=True)
    
    # PDF
    pdf_url = Column(String(500), nullable=True)
    
    # Usuário que criou
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    usuario = relationship("User")
    
    def __repr__(self) -> str:
        return f"<Contrato {self.numero}>"
