"""
Modelo para tracking de custos de geração de imagens
Registra cada geração com valor, modelo e métricas
"""

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from decimal import Decimal
from app.db.base import BaseModel


class ImagemCusto(BaseModel):
    """
    Tracking de custos por geração de imagem
    Cada registro representa uma tentativa de geração (sucesso ou erro)
    """
    __tablename__ = "imagens_custos"
    
    # Relacionamento com a imagem gerada (UUID no PostgreSQL)
    imagem_id = Column(UUID(as_uuid=True), ForeignKey("imagens.id", ondelete="SET NULL"), nullable=True)
    
    # Informações da API/modelo usado
    modelo = Column(String(50), nullable=False, default="glm-image")
    provider = Column(String(50), nullable=False, default="zai")  # zai, openai, etc
    
    # Custos (armazenados em Decimal para precisão)
    custo_usd = Column(Numeric(10, 6), nullable=False, default=Decimal("0.0"))
    custo_brl = Column(Numeric(10, 6), nullable=False, default=Decimal("0.0"))
    taxa_cambio = Column(Numeric(10, 6), nullable=True)  # Taxa usada na conversão
    
    # Dimensões da imagem gerada
    dimensoes = Column(String(20), nullable=True)  # ex: "1024x1024"
    formato = Column(String(10), nullable=True)    # ex: "1:1", "16:9", "9:16"
    
    # Métricas de performance
    tempo_geracao_ms = Column(Integer, nullable=True)  # Tempo em milissegundos
    
    # Status da operação
    status = Column(String(20), nullable=False, default="pendente")  # pendente, sucesso, erro
    erro_mensagem = Column(Text, nullable=True)  # Mensagem de erro se falhou
    
    # Prompt utilizado (para auditoria)
    prompt_original = Column(Text, nullable=True)
    prompt_enhanced = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    imagem = relationship("Imagem", back_populates="custos", lazy="selectin")
    
    def __repr__(self):
        return f"<ImagemCusto(id={self.id}, custo_usd={self.custo_usd}, status={self.status})>"
    
    @property
    def custo_brl_formatado(self) -> str:
        """Retorna o custo em BRL formatado como moeda"""
        return f"R$ {float(self.custo_brl):.4f}"
    
    @property
    def custo_usd_formatado(self) -> str:
        """Retorna o custo em USD formatado"""
        return f"US$ {float(self.custo_usd):.4f}"
