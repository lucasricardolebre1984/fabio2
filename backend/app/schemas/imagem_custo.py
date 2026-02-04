"""
Schemas Pydantic para ImagemCusto
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID


class ImagemCustoBase(BaseModel):
    """Schema base para ImagemCusto"""
    modelo: str = Field(default="glm-image", description="Modelo de IA utilizado")
    provider: str = Field(default="zai", description="Provedor da API")
    dimensoes: Optional[str] = Field(None, description="Dimensões da imagem (ex: 1024x1024)")
    formato: Optional[str] = Field(None, description="Formato da imagem (1:1, 16:9, 9:16)")
    status: str = Field(default="pendente", description="Status da geração")


class ImagemCustoCreate(ImagemCustoBase):
    """Schema para criar um registro de custo"""
    imagem_id: Optional[UUID] = None
    custo_usd: Decimal = Field(default=Decimal("0.015"), description="Custo em USD")
    custo_brl: Optional[Decimal] = Field(None, description="Custo em BRL (calculado)")
    taxa_cambio: Optional[Decimal] = Field(None, description="Taxa de câmbio USD->BRL")
    tempo_geracao_ms: Optional[int] = Field(None, description="Tempo de geração em ms")
    prompt_original: Optional[str] = None
    prompt_enhanced: Optional[str] = None
    erro_mensagem: Optional[str] = None


class ImagemCustoUpdate(BaseModel):
    """Schema para atualizar um registro de custo"""
    status: Optional[str] = None
    tempo_geracao_ms: Optional[int] = None
    erro_mensagem: Optional[str] = None
    imagem_id: Optional[UUID] = None


class ImagemCustoResponse(ImagemCustoBase):
    """Schema de resposta para ImagemCusto"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    imagem_id: Optional[UUID] = None
    custo_usd: Decimal
    custo_brl: Decimal
    taxa_cambio: Optional[Decimal] = None
    tempo_geracao_ms: Optional[int] = None
    prompt_original: Optional[str] = None
    prompt_enhanced: Optional[str] = None
    erro_mensagem: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Campos computados
    custo_brl_formatado: str = Field("", description="Custo em BRL formatado")
    custo_usd_formatado: str = Field("", description="Custo em USD formatado")


class DashboardCustoResponse(BaseModel):
    """Schema para dashboard de custos"""
    periodo_inicio: datetime
    periodo_fim: datetime
    
    # Totais
    total_imagens: int
    total_custo_usd: Decimal
    total_custo_brl: Decimal
    
    # Por status
    imagens_sucesso: int
    imagens_erro: int
    
    # Médias
    custo_medio_usd: Decimal
    tempo_medio_ms: Optional[int] = None
    
    # Projeção
    projecao_mensal_brl: Decimal
    
    # Dados diários (para gráficos)
    dados_diarios: list[dict] = Field(default_factory=list)


class CustoConfigResponse(BaseModel):
    """Schema para configuração de custos"""
    custo_por_imagem_usd: Decimal
    taxa_cambio_brl: Decimal
    modelo_padrao: str
    provider_padrao: str
