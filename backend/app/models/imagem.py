"""Imagem model."""
import enum
from sqlalchemy import Column, String, Enum, Text
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


class TipoImagem(str, enum.Enum):
    """Tipo de origem da imagem."""
    GERADA = "gerada"      # Gerada por IA (HuggingFace)
    UPLOAD = "upload"      # Upload manual do usuário


class FormatoImagem(str, enum.Enum):
    """Formatos de proporção suportados."""
    QUADRADO = "1:1"       # Feed Instagram
    PAISAGEM = "16:9"      # Banner/Story
    RETRATO = "9:16"       # Story vertical


class StatusImagem(str, enum.Enum):
    """Status da imagem no workflow."""
    RASCUNHO = "rascunho"      # Recém criada/uploadada
    APROVADA = "aprovada"      # Movida para campanhas/


class Imagem(BaseModel):
    """Imagem model for image generation and management."""
    
    __tablename__ = "imagens"
    
    # Identificação
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    
    # Arquivo
    url = Column(String(500), nullable=False)  # Caminho relativo: storage/imagens/...
    
    # Metadados
    tipo = Column(Enum(TipoImagem), nullable=False)
    formato = Column(Enum(FormatoImagem), default=FormatoImagem.QUADRADO, nullable=False)
    
    # Para imagens geradas por IA
    prompt = Column(Text, nullable=True)  # Prompt usado na geração
    
    # Workflow
    status = Column(Enum(StatusImagem), default=StatusImagem.RASCUNHO, nullable=False)
    
    # Relacionamentos
    custos = relationship("ImagemCusto", back_populates="imagem", lazy="selectin", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Imagem {self.nome} ({self.tipo.value})>"
