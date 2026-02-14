"""Chat endpoint VIVA (rota minima)."""

import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.api.v1.viva_schemas import ChatRequest, ChatResponse
from app.models.user import User

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_viva(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.services.viva_chat_orchestrator_service import viva_chat_orchestrator_service

    return await viva_chat_orchestrator_service.handle_chat_with_viva(
        request=request,
        current_user=current_user,
        db=db,
    )


@router.post("/chat/stream")
async def chat_with_viva_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Chat VIVA com streaming de resposta em tempo real (SSE)."""
    from app.services.viva_chat_orchestrator_service import viva_chat_orchestrator_service

    async def generate():
        """Generator para Server-Sent Events (SSE)."""
        try:
            # Gera stream de chunks
            async for chunk in viva_chat_orchestrator_service.handle_chat_with_viva_stream(
                request=request,
                current_user=current_user,
                db=db,
            ):
                # Envia cada chunk como evento SSE
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            error_chunk = {"error": str(e)}
            yield f"data: {json.dumps(error_chunk)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
