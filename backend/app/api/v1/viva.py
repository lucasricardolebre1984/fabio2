"""
Chat direto com a VIVA - Assistente Virtual Interna
Usa OpenAI para Chat, Visao, Audio e Imagem
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import base64
import json
import re

from app.api.deps import get_current_user
from app.models.user import User
from app.services.viva_local_service import viva_local_service
from app.services.viva_model_service import viva_model_service
from app.services.openai_service import openai_service
from app.services.openrouter_service import openrouter_service
from app.config import settings

router = APIRouter()


class ChatRequest(BaseModel):
    mensagem: str
    contexto: List[Dict[str, Any]] = []
    prompt_extra: Optional[str] = None


class MediaItem(BaseModel):
    tipo: str
    url: str
    meta: Optional[Dict[str, Any]] = None


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


def _is_greeting(texto: str) -> bool:
    lower = texto.lower().strip()
    termos = ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]
    return any(lower.startswith(t) for t in termos)


def _preferred_greeting(texto: str) -> str:
    lower = texto.lower()
    if "boa noite" in lower:
        return "Boa noite Fabio!"
    if "boa tarde" in lower:
        return "Boa tarde Fabio!"
    if "bom dia" in lower:
        return "Bom dia Fabio!"
    return "Olá Fabio!"


def _ensure_fabio_greeting(user_text: str, resposta: str) -> str:
    if not _is_greeting(user_text):
        return resposta

    if "fabio" in resposta.lower():
        return resposta

    greeting = _preferred_greeting(user_text)
    atualizado = re.sub(
        r"^(boa\s+noite|boa\s+tarde|bom\s+dia|ol[aá]|oi)[!,.\s-]*",
        f"{greeting} ",
        resposta,
        flags=re.IGNORECASE,
    )

    if atualizado == resposta:
        return f"{greeting} {resposta}"
    return atualizado


def _sanitize_prompt(texto: str, max_len: int) -> str:
    texto_limpo = " ".join(texto.replace("\r", " ").split())
    if len(texto_limpo) <= max_len:
        return texto_limpo
    return texto_limpo[:max_len].rstrip() + "..."


def _mode_hint(modo: Optional[str]) -> Optional[str]:
    if not modo:
        return None

    hints = {
        "LOGO": "Fundo clean, moderno e neutro para identidade visual.",
        "FC": "Fundo corporativo moderno. Paleta dominante azul institucional (#071c4a) e destaque #00a3ff.",
        "REZETA": "Fundo promocional moderno. Paleta azul marinho (#1E3A5F) e verde esmeralda (#3DAA7F).",
        "CRIADORLANDPAGE": "Fundo clean e moderno para landing page.",
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


def _is_stackoverflow_error(erro: Any) -> bool:
    if not erro:
        return False
    if isinstance(erro, dict):
        msg = str(erro.get("message") or erro.get("error") or "")
    else:
        msg = str(erro)
    return "StackOverflowError" in msg or "stack overflow" in msg.lower()


def _build_image_prompt(prompt_extra_image: Optional[str], hint: Optional[str], mensagem: str) -> str:
    subject = _extract_subject(mensagem)
    parts: List[str] = []
    if prompt_extra_image:
        parts.append(prompt_extra_image)
    if hint:
        parts.append(hint)
    parts.append(f"Contexto: {subject}")
    return "\n".join(parts)


def _build_fallback_image_prompt(hint: Optional[str], mensagem: str) -> str:
    subject = _extract_subject(mensagem)
    parts: List[str] = []
    if hint:
        parts.append(hint)
    parts.append(f"Contexto: {subject}")
    return "\n".join(parts)


def _extract_overlay_source(texto: str) -> str:
    texto_limpo = texto.replace("\r", "")
    lower = texto_limpo.lower()
    markers = [
        "segue o texto a ser vinculado",
        "segue o texto",
        "texto a ser vinculado",
        "texto:",
    ]

    for marker in markers:
        idx = lower.find(marker)
        if idx >= 0:
            payload = texto_limpo[idx + len(marker):].lstrip(" :\n")
            if payload.strip():
                return payload.strip()

    return texto_limpo.strip()


def _brand_guardrail(modo: str) -> str:
    if modo == "FC":
        return (
            "Marca FC Soluções Financeiras. Paleta obrigatória: #071c4a, #00a3ff, #010a1c, #f9feff. "
            "Não usar verde. Tom corporativo premium."
        )
    return (
        "Marca RezetaBrasil. Paleta obrigatória: #1E3A5F, #3DAA7F, #2A8B68, #FFFFFF. "
        "Tom humano, confiável e promocional."
    )


def _extract_json_block(raw: str) -> Optional[Dict[str, Any]]:
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        return None
    return None


def _fallback_copy(texto: str, modo: str) -> Dict[str, Any]:
    lines = [ln.strip() for ln in texto.splitlines() if ln.strip()]
    bullet_lines = [ln for ln in lines if re.match(r"^(✅|❌|⚠️|•|-)", ln)]
    headline = next((ln for ln in lines if ln not in bullet_lines), "Destrave seu crédito com estratégia")
    subheadline = next((ln for ln in lines[1:] if ln not in bullet_lines), "Diagnóstico claro e plano de ação objetivo")
    quote = next((ln for ln in lines if ln.startswith('"') or ln.startswith('“')), "")

    return {
        "brand": modo,
        "headline": _sanitize_prompt(headline, 90),
        "subheadline": _sanitize_prompt(subheadline, 130),
        "bullets": bullet_lines[:5] or [
            "✅ Diagnóstico completo",
            "✅ Plano de melhoria estruturado",
            "✅ Acompanhamento estratégico",
        ],
        "quote": _sanitize_prompt(quote, 120) if quote else "",
        "cta": "CHAMAR NO WHATSAPP" if modo == "REZETA" else "VER COMO FUNCIONA",
        "scene": "Pessoa em ambiente profissional moderno, expressão confiante, contexto financeiro",
    }


async def _generate_campaign_copy(
    mensagem: str,
    prompt_extra_image: Optional[str],
    modo: str,
) -> Dict[str, Any]:
    """
    Gera copy estruturada combinando o prompt mestre (REZETA.md ou FC.md) 
    com o brief específico do usuário.
    """
    fonte = _sanitize_prompt(_extract_overlay_source(mensagem), 5000)
    
    # Se temos o prompt_extra (conteúdo do REZETA.md ou FC.md), usamos ele como base
    prompt_mestre = prompt_extra_image or ""
    
    # Guardrails específicos por marca
    if modo == "REZETA":
        guardrail = (
            "Você é um diretor de arte especialista em campanhas RezetaBrasil. "
            "Use as diretrizes visuais da marca: azul marinho (#1E3A5F), verde esmeralda (#3DAA7F), "
            "layout com overlay branco superior e verde inferior, fotografia realista de pessoas."
        )
    else:  # FC
        guardrail = (
            "Você é um diretor de arte especialista em campanhas FC Soluções Financeiras. "
            "Use as diretrizes visuais da marca: azul escuro (#071c4a), azul claro (#00a3ff), "
            "layout institucional corporativo, fotografia realista profissional."
        )

    system = (
        f"{guardrail}\n\n"
        "Você deve analisar o brief do cliente e extrair/copy estruturada. "
        "Responda SOMENTE JSON válido, sem markdown."
    )
    
    user = (
        "ANÁLISE DO BRIEF DE CAMPANHA:\n\n"
        f"{fonte}\n\n"
        "---\n\n"
        "DIRETRIZES VISUAIS DA MARCA (use como referência):\n\n"
        f"{prompt_mestre[:3000]}\n\n"  # Limita para não ultrapassar tokens
        "---\n\n"
        "INSTRUÇÃO:\n"
        "Com base no brief acima e nas diretrizes visuais da marca, "
        "extraia/devolva um JSON com as chaves exatas:\n"
        "- headline: título principal impactante (6-10 palavras)\n"
        "- subheadline: subtítulo de apoio (8-16 palavras)\n"
        "- bullets: array com 3-5 bullets curtos destacando benefícios\n"
        "- quote: depoimento ou frase de impacto (opcional)\n"
        "- cta: call-to-action curto e direto (2-5 palavras)\n"
        "- scene: descrição detalhada da cena fotográfica para o fundo (sem texto, sem logo)\n\n"
        "O headline e subheadline devem capturar a essência do problema/solução do brief.\n"
        "A scene deve descrever uma fotografia realista de pessoa em contexto financeiro."
    )

    resposta = await openai_service.chat(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.4,
        max_tokens=800,
    )

    parsed = _extract_json_block(resposta)
    if not parsed:
        return _fallback_copy(fonte, modo)

    bullets = parsed.get("bullets") if isinstance(parsed.get("bullets"), list) else []
    bullets = [str(item).strip() for item in bullets if str(item).strip()][:5]

    copy = {
        "brand": modo,
        "headline": _sanitize_prompt(str(parsed.get("headline") or "Destrave seu crédito com estratégia"), 90),
        "subheadline": _sanitize_prompt(str(parsed.get("subheadline") or "Diagnóstico claro e pleno de ação objetivo"), 130),
        "bullets": bullets or _fallback_copy(fonte, modo)["bullets"],
        "quote": _sanitize_prompt(str(parsed.get("quote") or ""), 120),
        "cta": _sanitize_prompt(str(parsed.get("cta") or ("CHAMAR NO WHATSAPP" if modo == "REZETA" else "VER COMO FUNCIONA")), 40),
        "scene": _sanitize_prompt(str(parsed.get("scene") or "Pessoa em ambiente profissional moderno, expressão confiante, contexto financeiro"), 240),
    }
    return copy


def _build_branded_background_prompt(modo: str, campaign_copy: Dict[str, Any]) -> str:
    scene = campaign_copy.get("scene", "")
    if modo == "FC":
        return (
            "Fotografia publicitária corporativa premium, contexto financeiro no Brasil, "
            "escritório moderno, iluminação natural, composição clean, tons azul institucional "
            "(#071c4a, #00a3ff, #010a1c), sem verde, sem texto, sem letras, sem logotipo. "
            f"Cena: {scene}"
        )
    return (
        "Fotografia publicitária realista e humanizada para campanha de crédito no Brasil, "
        "ambiente moderno e acolhedor, tom de confiança e esperança, cores com presença de "
        "azul marinho e verde esmeralda (#1E3A5F, #3DAA7F, #2A8B68), sem texto, sem letras, sem logotipo. "
        f"Cena: {scene}"
    )


BACKGROUND_ONLY_SUFFIX = "Apenas fundo fotografico. Nao inclua palavras, letras ou logotipos."


def _extract_subject(texto: str) -> str:
    texto_limpo = " ".join(texto.replace("\r", " ").split())
    lower = texto_limpo.lower()
    markers = [
        "segue o texto a ser vinculado",
        "segue o texto",
        "texto a ser vinculado",
        "texto:"
    ]
    idx = None
    for marker in markers:
        pos = lower.find(marker)
        if pos >= 0:
            idx = pos
            break
    if idx is not None:
        texto_limpo = texto_limpo[:idx].strip()

    if not texto_limpo:
        return "Imagem promocional institucional"

    return _sanitize_prompt(texto_limpo, 300)


# ============================================
# CHAT
# ============================================
@router.post("/chat", response_model=ChatResponse)
async def chat_with_viva(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Chat direto com a VIVA usando OpenAI como provedor institucional."""
    try:
        modo = None
        for msg in reversed(request.contexto):
            if msg.get("modo"):
                modo = msg.get("modo")
                break

        prompt_extra_raw = request.prompt_extra.strip() if request.prompt_extra else None
        prompt_extra_chat = _sanitize_prompt(prompt_extra_raw, 4000) if prompt_extra_raw else None
        prompt_extra_image = _sanitize_prompt(prompt_extra_raw, 1200) if prompt_extra_raw else None

        if _is_image_request(request.mensagem):
            if not settings.OPENAI_API_KEY:
                return ChatResponse(resposta="A geracao de imagens esta indisponivel no momento.")

            hint = _mode_hint(modo)
            campaign_copy: Optional[Dict[str, Any]] = None

            if modo in ("FC", "REZETA"):
                campaign_copy = await _generate_campaign_copy(
                    request.mensagem,
                    prompt_extra_image,
                    modo,
                )
                prompt = _build_branded_background_prompt(modo, campaign_copy)
            else:
                prompt = _build_image_prompt(prompt_extra_image, hint, request.mensagem)
                prompt = f"{prompt}\n{BACKGROUND_ONLY_SUFFIX}"

            resultado = await openai_service.generate_image(prompt=prompt, size="1024x1024")
            if not resultado.get("success"):
                erro = resultado.get("error")
                if _is_stackoverflow_error(erro):
                    fallback_prompt = _build_fallback_image_prompt(hint, request.mensagem)
                    fallback_prompt = f"{fallback_prompt}\n{BACKGROUND_ONLY_SUFFIX}"
                    resultado = await openai_service.generate_image(
                        prompt=fallback_prompt,
                        size="1024x1024",
                    )
                    if resultado.get("success"):
                        url = _extract_image_url(resultado)
                        if url:
                            media = MediaItem(tipo="imagem", url=url)
                            if campaign_copy:
                                media.meta = {"overlay": campaign_copy}
                            return ChatResponse(resposta="Imagem gerada com sucesso.", midia=[media])
                        return ChatResponse(resposta="A imagem foi solicitada, mas a API nao retornou URL.")

                msg = erro.get("message", "Erro desconhecido") if isinstance(erro, dict) else str(erro)
                return ChatResponse(resposta=f"Erro ao gerar imagem: {msg}")

            url = _extract_image_url(resultado)
            if url:
                media_meta = {"overlay": campaign_copy} if campaign_copy else None
                media = MediaItem(tipo="imagem", url=url, meta=media_meta)
                return ChatResponse(resposta="Imagem gerada com sucesso.", midia=[media])
            return ChatResponse(resposta="A imagem foi solicitada, mas a API nao retornou URL.")

        if not settings.OPENAI_API_KEY:
            messages = viva_local_service.build_messages(request.mensagem, request.contexto)
            resposta = await viva_local_service.chat(messages, modo)
        else:
            messages = openrouter_service.build_messages(request.mensagem, request.contexto)
            if prompt_extra_chat:
                messages.insert(1, {"role": "system", "content": prompt_extra_chat})
            resposta = await viva_model_service.chat(
                messages=messages,
                temperature=0.58,
                max_tokens=700,
            )
            if not resposta or resposta.strip().lower().startswith(("erro", "error")):
                messages_local = viva_local_service.build_messages(request.mensagem, request.contexto)
                resposta = await viva_local_service.chat(messages_local, modo)

        resposta = _ensure_fabio_greeting(request.mensagem, resposta)
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
    """Analisa imagem usando modelo de visao da OpenAI."""
    try:
        if not settings.OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY nao configurada")

        resultado = await openai_service.vision_base64(
            request.image_base64,
            request.prompt,
        )
        return {"analise": resultado}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/vision/upload")
async def analyze_image_upload(
    file: UploadFile = File(...),
    prompt: str = Form("Descreva esta imagem"),
    current_user: User = Depends(get_current_user)
):
    """Faz upload e analisa imagem com OpenAI."""
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
    """Transcreve audio usando OpenAI."""
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
    """Gera imagem usando OpenAI Images."""
    try:
        if not settings.OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY nao configurada")

        size = f"{request.width}x{request.height}"
        resultado = await openai_service.generate_image(
            prompt=request.prompt,
            size=size,
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
    """Video generation nao habilitada no provedor OpenAI deste projeto."""
    raise HTTPException(
        status_code=501,
        detail="Geracao de video nao esta habilitada nesta versao OpenAI da VIVA.",
    )

@router.get("/video/result/{task_id}")
async def get_video_result(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Consulta de video nao habilitada no provedor OpenAI deste projeto."""
    raise HTTPException(
        status_code=501,
        detail="Consulta de video nao esta habilitada nesta versao OpenAI da VIVA.",
    )

# ============================================
# STATUS
# ============================================
@router.get("/status")
async def viva_status(
    current_user: User = Depends(get_current_user)
):
    """Verifica status da VIVA."""
    if settings.OPENAI_API_KEY:
        return viva_model_service.get_status()
    return viva_local_service.get_status()








