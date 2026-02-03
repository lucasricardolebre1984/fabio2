"""Cliente model."""
from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class Cliente(BaseModel):
    """Cliente (contratante) model."""
    
    __tablename__ = "clientes"
    
    # Dados básicos
    nome = Column(String(255), nullable=False, index=True)
    tipo_pessoa = Column(String(10), nullable=False, default="fisica")  # fisica | juridica
    documento = Column(String(20), unique=True, nullable=False, index=True)  # CPF/CNPJ
    email = Column(String(255), nullable=False)
    telefone = Column(String(20), nullable=True)
    
    # Endereço
    endereco = Column(Text, nullable=True)
    cidade = Column(String(100), nullable=True)
    estado = Column(String(2), nullable=True)
    cep = Column(String(10), nullable=True)
    
    # Observações
    observacoes = Column(Text, nullable=True)
    
    # Métricas
    primeiro_contrato_em = Column(DateTime(timezone=True), nullable=True)
    ultimo_contrato_em = Column(DateTime(timezone=True), nullable=True)
    total_contratos = Column(Integer, default=0, nullable=False)
    
    # Relationships
    contratos = relationship("Contrato", back_populates="cliente", lazy="dynamic")
    
    def __repr__(self) -> str:
        return f"<Cliente {self.nome}>"
