"""Chat endpoint VIVA (rota minima)."""

from fastapi import APIRouter, Depends
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
