"""
API de Chat WhatsApp para frontend.
Gerencia conversas e mensagens.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_operador
from app.db.session import get_db
from app.models.user import User
from app.models.whatsapp_conversa import (
    StatusConversa,
    WhatsappConversa,
    WhatsappMensagem,
)
from app.schemas.whatsapp_chat import (
    BindNumeroRequest,
    ConversaDetalheResponse,
    ConversaResponse,
    MensagemResponse,
)
from app.services.evolution_webhook_service import webhook_service

router = APIRouter()


@router.get("/conversas", response_model=List[ConversaResponse])
async def listar_conversas(
    status: StatusConversa = Query(StatusConversa.ATIVA),
    instance: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    """Lista conversas do WhatsApp com filtros."""
    _ = current_user

    stmt = select(WhatsappConversa).where(WhatsappConversa.status == status)
    if instance:
        stmt = stmt.where(WhatsappConversa.instance_name == instance)

    stmt = stmt.order_by(desc(WhatsappConversa.ultima_mensagem_em)).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/conversas/{conversa_id}", response_model=ConversaDetalheResponse)
async def obter_conversa(
    conversa_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    """Obtem detalhes de uma conversa com mensagens."""
    _ = current_user

    stmt = select(WhatsappConversa).where(WhatsappConversa.id == conversa_id)
    result = await db.execute(stmt)
    conversa = result.scalar_one_or_none()

    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa nao encontrada")
    return conversa


@router.get("/conversas/{conversa_id}/mensagens", response_model=List[MensagemResponse])
async def listar_mensagens(
    conversa_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    """Lista mensagens de uma conversa."""
    _ = current_user

    stmt = (
        select(WhatsappMensagem)
        .where(WhatsappMensagem.conversa_id == conversa_id)
        .order_by(desc(WhatsappMensagem.created_at))
        .limit(limit)
    )
    result = await db.execute(stmt)
    mensagens = result.scalars().all()
    return list(reversed(mensagens))


@router.post("/conversas/{conversa_id}/arquivar")
async def arquivar_conversa(
    conversa_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    """Arquiva uma conversa."""
    _ = current_user

    stmt = select(WhatsappConversa).where(WhatsappConversa.id == conversa_id)
    result = await db.execute(stmt)
    conversa = result.scalar_one_or_none()

    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa nao encontrada")

    conversa.status = StatusConversa.ARQUIVADA
    await db.commit()
    return {"status": "arquivada"}


@router.post("/conversas/{conversa_id}/bind-number")
async def bind_numero_real(
    conversa_id: UUID,
    payload: BindNumeroRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    """Vincula numero real para conversa @lid e dispara flush da fila pendente."""
    _ = current_user

    stmt = select(WhatsappConversa).where(WhatsappConversa.id == conversa_id)
    result = await db.execute(stmt)
    conversa = result.scalar_one_or_none()
    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa nao encontrada")

    digits = "".join(ch for ch in str(payload.numero_real or "") if ch.isdigit())
    if len(digits) <= 11 and not digits.startswith("55"):
        digits = "55" + digits
    if len(digits) < 12 or len(digits) > 15:
        raise HTTPException(status_code=400, detail="Numero invalido para bind")

    contexto = dict(conversa.contexto_ia or {})
    contexto["resolved_whatsapp_number"] = digits
    contexto["resolved_whatsapp_source"] = "manual_bind"
    contexto["needs_manual_bind"] = False
    contexto["manual_bind_at"] = datetime.utcnow().isoformat()
    contexto.pop("manual_bind_reason", None)
    conversa.contexto_ia = contexto
    await db.commit()
    await db.refresh(conversa)

    sent = await webhook_service._flush_pending_outbound_for_conversation(  # noqa: SLF001
        db=db,
        conversa=conversa,
        push_name=conversa.nome_contato,
        remote_jid=conversa.numero_telefone,
    )
    return {
        "status": "bound",
        "numero_real": digits,
        "pending_sent": sent,
    }


@router.get("/status")
async def status_whatsapp(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador),
):
    """Retorna estatisticas do WhatsApp."""
    _ = current_user

    stmt_ativas = select(func.count()).where(WhatsappConversa.status == StatusConversa.ATIVA)
    result = await db.execute(stmt_ativas)
    ativas = result.scalar() or 0

    hoje = datetime.utcnow().date()
    amanha = hoje + timedelta(days=1)

    stmt_hoje = select(func.count()).where(
        and_(
            WhatsappMensagem.created_at >= hoje,
            WhatsappMensagem.created_at < amanha,
        )
    )
    result = await db.execute(stmt_hoje)
    mensagens_hoje = result.scalar() or 0

    return {
        "conversas_ativas": ativas,
        "mensagens_hoje": mensagens_hoje,
        "status": "online",
    }
