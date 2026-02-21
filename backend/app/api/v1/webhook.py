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


@router.post("/evolution/{path:path}")
async def evolution_webhook_catchall(
    path: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Compatibilidade: Evolution pode enviar webhooks por evento em paths diferentes.

    Exemplos vistos em producao:
    - /api/v1/webhook/evolution/messages-upsert
    - /api/v1/webhook/evolution/connection-update
    - /api/v1/webhook/evolution/chats-upsert
    """
    try:
        data = await request.json()
        if isinstance(data, dict) and not data.get("event"):
            event_hint = str((path or "").strip("/").split("/")[-1] or "").strip()
            if event_hint:
                data["event"] = event_hint.replace("-", ".").replace("_", ".")
        processado = await webhook_service.processar_webhook(data, db)
        return {"status": "received", "processed": processado}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/evolution")
async def evolution_webhook_verify():
    """Health simples do webhook para testes."""
    return {"status": "webhook ativo", "service": "evolution"}
