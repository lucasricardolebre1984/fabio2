"""
Chat direto com a VIVA - Assistente Virtual Interna
Usa Z.AI (GLM-4) para Chat, Visão, Áudio e Imagem
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
import base64

from app.api.deps import get_current_user
from app.models.user import User
from app.services.viva_local_service import viva_local_service
from app.services.openrouter_service import openrouter_service
from app.services.zai_service import zai_service
from app.config import settings

router = APIRouter()


class ChatRequest(BaseModel):
    mensagem: str
    contexto: List[Dict[str, Any]] = []
    prompt_extra: Optional[str] = None


class MediaItem(BaseModel):
    tipo: str
    url: str


class ChatResponse(BaseModel):
    resposta: str
    midia: Optional[List[MediaItem]] = None


class ImageAnalysisRequest(BaseModel):
    image_base64: str
    prompt: str = "Descreva esta imagem em detalhes"


class ImageGenerationRequest(BaseModel):
    prompt: str
    width: int = 1024
    height: int = 1024


class VideoGenerationRequest(BaseModel):
    prompt: str
    size: str = "1920x1080"
    fps: int = 30
    duration: int = 5
    quality: str = "quality"
    with_audio: bool = True


def _is_image_request(texto: str) -> bool:
    termos = [
        "imagem",
        "banner",
        "logo",
        "logotipo",
        "post",
        "flyer",
        "arte",
        "cartaz",
        "thumbnail",
        "capa",
    ]
    texto_lower = texto.lower()
    return any(t in texto_lower for t in termos)


def _sanitize_prompt(texto: str, max_len: int) -> str:
    texto_limpo = " ".join(texto.replace("\r", " ").split())
    if len(texto_limpo) <= max_len:
        return texto_limpo
    return texto_limpo[:max_len].rstrip() + "..."


def _mode_hint(modo: Optional[str]) -> Optional[str]:
    if not modo:
        return None

    hints = {
        "LOGO": "Crie uma imagem focada em logo e identidade visual.",
        "FC": "Crie uma imagem institucional para FC Soluções Financeiras.",
        "REZETA": "Crie uma imagem promocional para RezetaBrasil.",
        "CRIADORLANDPAGE": "Crie uma imagem para landing page.",
    }
    return hints.get(modo)


def _extract_image_url(result: Dict[str, Any]) -> Optional[str]:
    payload = result.get("data") if isinstance(result, dict) else None

    if isinstance(payload, dict):
        data_list = payload.get("data")
        if isinstance(data_list, list) and data_list:
            item = data_list[0]
            if isinstance(item, dict):
                if item.get("url"):
                    return item["url"]
                if item.get("b64_json"):
                    return f"data:image/png;base64,{item['b64_json']}"

        if isinstance(payload.get("url"), str):
            return payload["url"]
        if isinstance(payload.get("image_url"), str):
            return payload["image_url"]

    if isinstance(payload, list) and payload:
        item = payload[0]
        if isinstance(item, dict):
            if item.get("url"):
                return item["url"]
            if item.get("b64_json"):
                return f"data:image/png;base64,{item['b64_json']}"

    return None


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

        prompt_extra_raw = request.prompt_extra.strip() if request.prompt_extra else None
        prompt_extra_chat = _sanitize_prompt(prompt_extra_raw, 4000) if prompt_extra_raw else None
        prompt_extra_image = _sanitize_prompt(prompt_extra_raw, 1200) if prompt_extra_raw else None

        # Roteia intenção de imagem diretamente para o gerador
        if _is_image_request(request.mensagem):
            if not settings.ZAI_API_KEY:
                return ChatResponse(
                    resposta="A geração de imagens está indisponível no momento."
                )

            hint = _mode_hint(modo)
            prompt_parts: List[str] = []
            if prompt_extra_image:
                prompt_parts.append(prompt_extra_image)
            if hint:
                prompt_parts.append(hint)
            prompt_parts.append(f"Solicitação: {request.mensagem.strip()}")
            prompt = "\n".join(prompt_parts)

            resultado = await zai_service.generate_image(
                prompt=prompt,
                size="1024x1024",
            )
            if not resultado.get("success"):
                erro = resultado.get("error")
                if isinstance(erro, dict):
                    msg = erro.get("message", "Erro desconhecido")
                else:
                    msg = str(erro)
                return ChatResponse(
                    resposta=f"Erro ao gerar imagem: {msg}"
                )
            url = _extract_image_url(resultado)
            if url:
                return ChatResponse(
                    resposta="Imagem gerada com sucesso.",
                    midia=[MediaItem(tipo="imagem", url=url)],
                )

            return ChatResponse(
                resposta="A imagem foi solicitada, mas a API não retornou URL."
            )
        
        # Prioriza Z.AI (oficial). Fallback para OpenRouter e modo local.
        if settings.ZAI_API_KEY:
            messages = openrouter_service.build_messages(
                request.mensagem,
                request.contexto
            )
            if prompt_extra_chat:
                messages.insert(1, {"role": "system", "content": prompt_extra_chat})
            resposta = await zai_service.chat(messages)
        elif settings.OPENROUTER_API_KEY and settings.OPENROUTER_API_KEY != 'sk-or-v1-000000000000000000000000000000000000000000000000':
            messages = openrouter_service.build_messages(
                request.mensagem,
                request.contexto
            )
            if prompt_extra_chat:
                messages.insert(1, {"role": "system", "content": prompt_extra_chat})
            resposta = await openrouter_service.chat(messages)
        else:
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
        if not settings.ZAI_API_KEY:
            raise HTTPException(status_code=500, detail="ZAI_API_KEY não configurada")

        resultado = await zai_service.vision_base64(
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
        
        if not settings.ZAI_API_KEY:
            raise HTTPException(status_code=500, detail="ZAI_API_KEY não configurada")

        resultado = await zai_service.vision_base64(
            image_base64,
            prompt,
            mime_type=mime_type
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
        mime_type = file.content_type or "audio/wav"
        
        if not settings.ZAI_API_KEY:
            raise HTTPException(status_code=500, detail="ZAI_API_KEY não configurada")

        resultado = await zai_service.audio_transcribe_bytes(
            audio_bytes=contents,
            filename=file.filename or "audio.wav",
            content_type=mime_type
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
        if not settings.ZAI_API_KEY:
            raise HTTPException(status_code=500, detail="ZAI_API_KEY não configurada")

        size = f"{request.width}x{request.height}"
        resultado = await zai_service.generate_image(
            prompt=request.prompt,
            size=size
        )
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


# ============================================
# VÍDEO - Geração
# ============================================
@router.post("/video/generate")
async def generate_video(
    request: VideoGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Gera vídeo usando CogVideoX-3 (Z.AI)
    """
    try:
        if not settings.ZAI_API_KEY:
            raise HTTPException(status_code=500, detail="ZAI_API_KEY não configurada")

        resultado = await zai_service.generate_video(
            prompt=request.prompt,
            size=request.size,
            fps=request.fps,
            duration=request.duration,
            quality=request.quality,
            with_audio=request.with_audio,
        )
        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


@router.get("/video/result/{task_id}")
async def get_video_result(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Consulta resultado assíncrono de geração de vídeo
    """
    try:
        if not settings.ZAI_API_KEY:
            raise HTTPException(status_code=500, detail="ZAI_API_KEY não configurada")

        resultado = await zai_service.get_async_result(task_id)
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
    if settings.ZAI_API_KEY:
        return zai_service.get_status()
    if settings.OPENROUTER_API_KEY and settings.OPENROUTER_API_KEY != 'sk-or-v1-000000000000000000000000000000000000000000000000':
        return openrouter_service.get_status()
    else:
        return viva_local_service.get_status()
