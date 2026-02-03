"""ContratoTemplate model."""
from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import BaseModel


class ContratoTemplate(BaseModel):
    """Contrato template model."""
    
    __tablename__ = "contrato_templates"
    
    # Identificação
    nome = Column(String(255), nullable=False)
    tipo = Column(String(50), nullable=False, unique=True, index=True)
    descricao = Column(Text, nullable=True)
    versao = Column(String(10), default="1.0.0", nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Dados da contratada (fixos para este template)
    contratada_nome = Column(String(255), nullable=False)
    contratada_cnpj = Column(String(20), nullable=False)
    contratada_email = Column(String(255), nullable=False)
    contratada_endereco = Column(Text, nullable=False)
    contratada_telefone = Column(String(20), nullable=True)
    
    # Configuração do template
    campos = Column(JSONB, default=list, nullable=False)
    secoes = Column(JSONB, default=list, nullable=False)
    clausulas = Column(JSONB, default=list, nullable=False)
    assinaturas = Column(JSONB, default=dict, nullable=False)
    layout = Column(JSONB, default=dict, nullable=False)
    
    def __repr__(self) -> str:
        return f"<ContratoTemplate {self.tipo}>"
