import base64
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.api.deps import get_current_user
from app.api.v1.viva_schemas import ImageAnalysisRequest, ImageGenerationRequest, VideoGenerationRequest, TextToSpeechRequest
from app.config import settings
from app.models.user import User
from app.services.minimax_tts_service import minimax_tts_service
from app.services.openai_service import openai_service
from app.services.viva_local_service import viva_local_service
from app.services.viva_model_service import viva_model_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/vision")
async def analyze_image(
    request: ImageAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        if not settings.OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY nao configurada")

        resultado = await openai_service.vision_base64(
            request.image_base64,
            request.prompt,
        )
        return {"analise": resultado}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro: {str(exc)}")


@router.get("/tts/status")
async def tts_status(
    current_user: User = Depends(get_current_user),
):
    try:
        status = minimax_tts_service.get_status()
        if status.get("configured"):
            try:
                ok = await minimax_tts_service.test_connection()
                status["test"] = "success" if ok else "failed"
            except Exception as exc:
                status["test"] = "failed"
                status["error"] = str(exc)[:220]
        return status
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro status TTS: {str(exc)}")


@router.post("/vision/upload")
async def analyze_image_upload(
    file: UploadFile = File(...),
    prompt: str = Form("Descreva esta imagem"),
    current_user: User = Depends(get_current_user),
):
    try:
        contents = await file.read()
        image_base64 = base64.b64encode(contents).decode("utf-8")
        mime_type = file.content_type or "image/jpeg"

        if not settings.OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY nao configurada")

        resultado = await openai_service.vision_base64(
            image_base64,
            prompt,
            mime_type=mime_type,
        )
        return {"analise": resultado}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro: {str(exc)}")


@router.post("/audio/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    try:
        contents = await file.read()
        mime_type = file.content_type or "audio/wav"

        if not settings.OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY nao configurada")

        resultado = await viva_model_service.audio_transcribe_bytes(
            audio_bytes=contents,
            filename=file.filename or "audio.wav",
            content_type=mime_type,
        )
        if not resultado or resultado.strip().lower().startswith(("erro", "error")):
            raise HTTPException(status_code=502, detail=resultado or "Falha na transcricao")

        return {"transcricao": resultado}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro: {str(exc)}")


@router.post("/audio/speak")
async def speak_text(
    payload: TextToSpeechRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        audio_bytes, media_type = await minimax_tts_service.synthesize(payload.text)
        return Response(content=audio_bytes, media_type=media_type)
    except Exception as exc:
        logger.warning("viva_tts_failed: %s", str(exc)[:220])
        raise HTTPException(status_code=502, detail=f"Erro TTS: {str(exc)}")


@router.post("/image/generate")
async def generate_image(
    request: ImageGenerationRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        if not settings.OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY nao configurada")

        size = f"{request.width}x{request.height}"
        resultado = await openai_service.generate_image(
            prompt=request.prompt,
            size=size,
        )
        return resultado
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro: {str(exc)}")


@router.post("/video/generate")
async def generate_video(
    request: VideoGenerationRequest,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(
        status_code=501,
        detail="Geracao de video nao esta habilitada nesta versao OpenAI da VIVA.",
    )


@router.get("/video/result/{task_id}")
async def get_video_result(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(
        status_code=501,
        detail="Consulta de video nao esta habilitada nesta versao OpenAI da VIVA.",
    )


@router.get("/status")
async def viva_status(
    current_user: User = Depends(get_current_user),
):
    if settings.OPENAI_API_KEY:
        return {**viva_model_service.get_status(), "tts": minimax_tts_service.get_status()}
    return {**viva_local_service.get_status(), "tts": minimax_tts_service.get_status()}
