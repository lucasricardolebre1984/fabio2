"""WhatsApp routes."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, require_operador
from app.models.user import User
from app.services.whatsapp_service import WhatsAppService

router = APIRouter()


@router.get("/status")
async def get_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Get WhatsApp connection status."""
    service = WhatsAppService()
    return await service.get_status()


@router.post("/conectar")
async def conectar(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Start WhatsApp connection."""
    service = WhatsAppService()
    return await service.connect()


@router.post("/desconectar")
async def desconectar(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Disconnect WhatsApp."""
    service = WhatsAppService()
    return await service.disconnect()


@router.post("/enviar-texto")
async def enviar_texto(
    numero: str,
    mensagem: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Send text message."""
    service = WhatsAppService()
    return await service.send_text(numero, mensagem)


@router.post("/enviar-arquivo")
async def enviar_arquivo(
    numero: str,
    arquivo_url: str,
    legenda: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operador)
):
    """Send file/document."""
    service = WhatsAppService()
    return await service.send_document(numero, arquivo_url, legenda)
