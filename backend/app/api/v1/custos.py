"""
API endpoints para dashboard e gestão de custos de imagens
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.custo_service import custo_service
from app.schemas.imagem_custo import (
    DashboardCustoResponse,
    ImagemCustoResponse,
    CustoConfigResponse
)

router = APIRouter()


@router.get("/dashboard", response_model=DashboardCustoResponse)
async def get_dashboard_custos(
    dias: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna dados do dashboard de custos
    
    - **dias**: Período em dias (padrão: 30, máx: 365)
    """
    if dias > 365:
        dias = 365
    
    dashboard = await custo_service.get_dashboard(db, dias=dias)
    return dashboard


@router.get("/historico", response_model=List[ImagemCustoResponse])
async def get_historico_custos(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna histórico de custos (últimas gerações)
    
    - **skip**: Offset para paginação
    - **limit**: Limite de registros (máx: 100)
    """
    if limit > 100:
        limit = 100
    
    historico = await custo_service.get_historico(db, skip=skip, limit=limit)
    return historico


@router.get("/mes-atual")
async def get_custo_mes_atual(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna custo acumulado do mês atual
    """
    custo = await custo_service.get_custo_atual_mes(db)
    return custo


@router.get("/config", response_model=CustoConfigResponse)
async def get_config_custos(
    current_user: User = Depends(get_current_user)
):
    """
    Retorna configuração de custos (preço por imagem, taxa câmbio, etc)
    """
    config = custo_service.get_config_custo()
    return config
