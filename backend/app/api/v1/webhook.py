"""
Endpoints de Webhook para Evolution API.
Recebe eventos do WhatsApp.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.evolution_webhook_service import webhook_service

router = APIRouter()


@router.post("/evolution")
async def evolution_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Webhook para receber eventos do Evolution API.

    Configure no Evolution Manager:
    URL: http://localhost:8000/api/v1/webhook/evolution
    Eventos: messages.upsert, connection.update
    """
    try:
        data = await request.json()
        processado = await webhook_service.processar_webhook(data, db)
        return {"status": "received", "processed": processado}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/evolution")
async def evolution_webhook_verify():
    """Health simples do webhook para testes."""
    return {"status": "webhook ativo", "service": "evolution"}
