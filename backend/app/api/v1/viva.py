"""
Chat direto com a VIVA - Assistente Virtual Interna
Usa Z.AI (GLM-4) para Chat, Visão, Áudio e Imagem
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
import base64

from app.api.deps import get_current_user
from app.models.user import User
from app.services.viva_local_service import viva_local_service
from app.services.openrouter_service import openrouter_service
from app.config import settings

router = APIRouter()


class ChatRequest(BaseModel):
    mensagem: str
    contexto: List[Dict[str, Any]] = []


class ChatResponse(BaseModel):
    resposta: str


class ImageAnalysisRequest(BaseModel):
    image_base64: str
    prompt: str = "Descreva esta imagem em detalhes"


class ImageGenerationRequest(BaseModel):
    prompt: str
    width: int = 1024
    height: int = 1024


# ============================================
# CHAT
# ============================================
@router.post("/chat", response_model=ChatResponse)
async def chat_with_viva(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Chat direto com a VIVA
    Usa OpenRouter se disponível, senão usa modo local
    """
    try:
        # Detecta modo ativo pelo contexto
        modo = None
        for msg in reversed(request.contexto):
            if msg.get('modo'):
                modo = msg.get('modo')
                break
        
        # Verifica se tem API configurada
        if settings.OPENROUTER_API_KEY and settings.OPENROUTER_API_KEY != 'sk-or-v1-000000000000000000000000000000000000000000000000':
            # Usa OpenRouter
            messages = openrouter_service.build_messages(
                request.mensagem, 
                request.contexto
            )
            resposta = await openrouter_service.chat(messages)
        else:
            # Usa modo local (templates)
            messages = viva_local_service.build_messages(
                request.mensagem,
                request.contexto
            )
            resposta = await viva_local_service.chat(messages, modo)
        
        return ChatResponse(resposta=resposta)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


# ============================================
# VISÃO - Análise de Imagens
# ============================================
@router.post("/vision")
async def analyze_image(
    request: ImageAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analisa imagem usando GLM-4V
    """
    try:
        # Usa serviço local para visão
        resultado = await viva_local_service.vision(
            request.image_base64,
            request.prompt
        )
        return {"analise": resultado}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


@router.post("/vision/upload")
async def analyze_image_upload(
    file: UploadFile = File(...),
    prompt: str = "Descreva esta imagem",
    current_user: User = Depends(get_current_user)
):
    """
    Faz upload e analisa imagem
    """
    try:
        contents = await file.read()
        image_base64 = base64.b64encode(contents).decode('utf-8')
        mime_type = file.content_type or "image/jpeg"
        
        resultado = await viva_local_service.vision(
            image_base64,
            prompt
        )
        return {"analise": resultado}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


# ============================================
# ÁUDIO - Transcrição
# ============================================
@router.post("/audio/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Transcreve áudio usando GLM-ASR
    """
    try:
        contents = await file.read()
        audio_base64 = base64.b64encode(contents).decode('utf-8')
        mime_type = file.content_type or "audio/wav"
        
        resultado = await zai_service.audio_transcribe(
            audio_base64,
            mime_type
        )
        return {"transcricao": resultado}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


# ============================================
# IMAGEM - Geração
# ============================================
@router.post("/image/generate")
async def generate_image(
    request: ImageGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Gera imagem usando GLM-Image
    """
    try:
        resultado = await zai_service.generate_image(
            request.prompt,
            request.width,
            request.height
        )
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


# ============================================
# STATUS
# ============================================
@router.get("/status")
async def viva_status(
    current_user: User = Depends(get_current_user)
):
    """
    Verifica status da VIVA
    """
    # Verifica se tem API externa configurada
    if settings.OPENROUTER_API_KEY and settings.OPENROUTER_API_KEY != 'sk-or-v1-000000000000000000000000000000000000000000000000':
        return openrouter_service.get_status()
    else:
        return viva_local_service.get_status()
