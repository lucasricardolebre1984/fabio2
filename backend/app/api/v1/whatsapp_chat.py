"""
API de Chat WhatsApp para Frontend
Gerencia conversas e mensagens
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.models.whatsapp_conversa import WhatsappConversa, WhatsappMensagem, StatusConversa
from app.schemas.whatsapp_chat import (
    ConversaResponse, 
    ConversaCreate,
    MensagemResponse,
    ConversaDetalheResponse
)

router = APIRouter()


@router.get("/conversas", response_model=List[ConversaResponse])
async def listar_conversas(
    status: Optional[StatusConversa] = StatusConversa.ATIVA,
    instance: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Lista conversas do WhatsApp com filtros"""
    
    stmt = select(WhatsappConversa).where(WhatsappConversa.status == status)
    
    if instance:
        stmt = stmt.where(WhatsappConversa.instance_name == instance)
    
    stmt = stmt.order_by(desc(WhatsappConversa.ultima_mensagem_em)).limit(limit)
    
    result = await db.execute(stmt)
    conversas = result.scalars().all()
    
    return conversas


@router.get("/conversas/{conversa_id}", response_model=ConversaDetalheResponse)
async def obter_conversa(
    conversa_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Obtém detalhes de uma conversa com mensagens"""
    
    stmt = select(WhatsappConversa).where(WhatsappConversa.id == conversa_id)
    result = await db.execute(stmt)
    conversa = result.scalar_one_or_none()
    
    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    
    return conversa


@router.get("/conversas/{conversa_id}/mensagens", response_model=List[MensagemResponse])
async def listar_mensagens(
    conversa_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Lista mensagens de uma conversa"""
    
    stmt = (
        select(WhatsappMensagem)
        .where(WhatsappMensagem.conversa_id == conversa_id)
        .order_by(desc(WhatsappMensagem.created_at))
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    mensagens = result.scalars().all()
    
    # Inverte para ordem cronológica
    return list(reversed(mensagens))


@router.post("/conversas/{conversa_id}/arquivar")
async def arquivar_conversa(
    conversa_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Arquiva uma conversa"""
    
    stmt = select(WhatsappConversa).where(WhatsappConversa.id == conversa_id)
    result = await db.execute(stmt)
    conversa = result.scalar_one_or_none()
    
    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    
    conversa.status = StatusConversa.ARQUIVADA
    await db.commit()
    
    return {"status": "arquivada"}


@router.get("/status")
async def status_whatsapp(
    db: AsyncSession = Depends(get_db)
):
    """Retorna estatísticas do WhatsApp"""
    
    from sqlalchemy import func
    
    # Conta conversas ativas
    stmt_ativas = select(func.count()).where(WhatsappConversa.status == StatusConversa.ATIVA)
    result = await db.execute(stmt_ativas)
    ativas = result.scalar()
    
    # Conta mensagens hoje
    from datetime import datetime, timedelta
    hoje = datetime.utcnow().date()
    amanha = hoje + timedelta(days=1)
    
    stmt_hoje = select(func.count()).where(
        and_(
            WhatsappMensagem.created_at >= hoje,
            WhatsappMensagem.created_at < amanha
        )
    )
    result = await db.execute(stmt_hoje)
    mensagens_hoje = result.scalar()
    
    return {
        "conversas_ativas": ativas,
        "mensagens_hoje": mensagens_hoje,
        "status": "online"
    }
