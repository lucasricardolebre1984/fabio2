"""
Serviço para gestão e dashboard de custos de imagens
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import func, select, desc, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.imagem_custo import ImagemCusto


class CustoService:
    """Service for cost tracking and dashboard"""
    
    # Configurações de custo
    CUSTO_POR_IMAGEM_USD = Decimal("0.015")
    TAXA_CAMBIO_PADRAO = Decimal("5.0")
    
    async def get_dashboard(
        self,
        db: AsyncSession,
        dias: int = 30
    ) -> dict:
        """
        Retorna dados do dashboard de custos
        
        Args:
            db: Database session
            dias: Período em dias (padrão: 30)
            
        Returns:
            Dict com métricas de custo
        """
        data_inicio = datetime.utcnow() - timedelta(days=dias)
        data_fim = datetime.utcnow()
        
        # Total de imagens geradas no período
        total_query = select(func.count(ImagemCusto.id)).where(
            ImagemCusto.created_at >= data_inicio
        )
        total_result = await db.execute(total_query)
        total_imagens = total_result.scalar() or 0
        
        # Total de custo (USD)
        custo_query = select(func.sum(ImagemCusto.custo_usd)).where(
            ImagemCusto.created_at >= data_inicio
        )
        custo_result = await db.execute(custo_query)
        total_custo_usd = custo_result.scalar() or Decimal("0")
        
        # Total de custo (BRL)
        custo_brl_query = select(func.sum(ImagemCusto.custo_brl)).where(
            ImagemCusto.created_at >= data_inicio
        )
        custo_brl_result = await db.execute(custo_brl_query)
        total_custo_brl = custo_brl_result.scalar() or Decimal("0")
        
        # Imagens com sucesso
        sucesso_query = select(func.count(ImagemCusto.id)).where(
            ImagemCusto.created_at >= data_inicio,
            ImagemCusto.status == "sucesso"
        )
        sucesso_result = await db.execute(sucesso_query)
        imagens_sucesso = sucesso_result.scalar() or 0
        
        # Imagens com erro
        erro_query = select(func.count(ImagemCusto.id)).where(
            ImagemCusto.created_at >= data_inicio,
            ImagemCusto.status == "erro"
        )
        erro_result = await db.execute(erro_query)
        imagens_erro = erro_result.scalar() or 0
        
        # Tempo médio de geração
        tempo_query = select(func.avg(ImagemCusto.tempo_geracao_ms)).where(
            ImagemCusto.created_at >= data_inicio,
            ImagemCusto.status == "sucesso"
        )
        tempo_result = await db.execute(tempo_query)
        tempo_medio = tempo_result.scalar()
        
        # Custo médio por imagem
        custo_medio_usd = total_custo_usd / total_imagens if total_imagens > 0 else Decimal("0")
        
        # Projeção mensal (baseada nos últimos 7 dias)
        projecao = await self._calcular_projecao_mensal(db)
        
        # Dados diários para gráfico
        dados_diarios = await self._get_dados_diarios(db, dias)
        
        return {
            "periodo_inicio": data_inicio,
            "periodo_fim": data_fim,
            "total_imagens": total_imagens,
            "total_custo_usd": total_custo_usd,
            "total_custo_brl": total_custo_brl,
            "imagens_sucesso": imagens_sucesso,
            "imagens_erro": imagens_erro,
            "custo_medio_usd": custo_medio_usd,
            "tempo_medio_ms": int(tempo_medio) if tempo_medio else None,
            "projecao_mensal_brl": projecao,
            "dados_diarios": dados_diarios
        }
    
    async def _calcular_projecao_mensal(self, db: AsyncSession) -> Decimal:
        """Calcula projeção de gasto mensal baseada nos últimos 7 dias"""
        data_7dias = datetime.utcnow() - timedelta(days=7)
        
        query = select(func.sum(ImagemCusto.custo_brl)).where(
            ImagemCusto.created_at >= data_7dias
        )
        result = await db.execute(query)
        custo_7dias = result.scalar() or Decimal("0")
        
        # Projetar para 30 dias
        projecao = (custo_7dias / 7) * 30
        return projecao
    
    async def _get_dados_diarios(self, db: AsyncSession, dias: int) -> List[dict]:
        """Retorna dados agregados por dia para gráficos"""
        data_inicio = datetime.utcnow() - timedelta(days=dias)
        
        query = select(
            cast(ImagemCusto.created_at, Date).label("data"),
            func.count(ImagemCusto.id).label("quantidade"),
            func.sum(ImagemCusto.custo_brl).label("custo_total")
        ).where(
            ImagemCusto.created_at >= data_inicio
        ).group_by(
            cast(ImagemCusto.created_at, Date)
        ).order_by(
            cast(ImagemCusto.created_at, Date)
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        return [
            {
                "data": row.data.isoformat(),
                "quantidade": row.quantidade,
                "custo": float(row.custo_total) if row.custo_total else 0.0
            }
            for row in rows
        ]
    
    async def get_historico(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50
    ) -> List[ImagemCusto]:
        """
        Retorna histórico de custos
        
        Args:
            db: Database session
            skip: Offset
            limit: Limite de registros
            
        Returns:
            Lista de ImagemCusto
        """
        query = select(ImagemCusto).order_by(
            desc(ImagemCusto.created_at)
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_custo_atual_mes(self, db: AsyncSession) -> dict:
        """Retorna custo do mês atual"""
        hoje = datetime.utcnow()
        inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        query = select(
            func.count(ImagemCusto.id),
            func.sum(ImagemCusto.custo_usd),
            func.sum(ImagemCusto.custo_brl)
        ).where(
            ImagemCusto.created_at >= inicio_mes
        )
        
        result = await db.execute(query)
        count, usd, brl = result.first()
        
        return {
            "mes": hoje.month,
            "ano": hoje.year,
            "quantidade": count or 0,
            "custo_usd": usd or Decimal("0"),
            "custo_brl": brl or Decimal("0")
        }
    
    def get_config_custo(self) -> dict:
        """Retorna configuração de custos"""
        return {
            "custo_por_imagem_usd": self.CUSTO_POR_IMAGEM_USD,
            "taxa_cambio_brl": self.TAXA_CAMBIO_PADRAO,
            "modelo_padrao": "glm-image",
            "provider_padrao": "zai"
        }


# Instância singleton
custo_service = CustoService()
