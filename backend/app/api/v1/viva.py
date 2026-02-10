"""
Chat direto com a VIVA - Assistente Virtual Interna
Usa OpenAI para Chat, Visao, Audio e Imagem
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import base64
import json
import re
import unicodedata
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.agenda import EventoTipo
from app.schemas.agenda import EventoCreate
from app.services.agenda_service import AgendaService
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
    modo: Optional[str] = None


class MediaItem(BaseModel):
    tipo: str
    url: str
    meta: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    resposta: str
    midia: Optional[List[MediaItem]] = None


class CampanhaSaveRequest(BaseModel):
    modo: str
    image_url: str
    titulo: Optional[str] = None
    briefing: Optional[str] = None
    mensagem_original: Optional[str] = None
    overlay: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


class CampanhaItem(BaseModel):
    id: UUID
    modo: str
    titulo: str
    briefing: Optional[str] = None
    mensagem_original: Optional[str] = None
    image_url: str
    overlay: Dict[str, Any] = {}
    meta: Dict[str, Any] = {}
    created_at: datetime


class CampanhaListResponse(BaseModel):
    items: List[CampanhaItem]
    total: int


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


def _is_campaign_request(texto: str) -> bool:
    terms = [
        "campanha",
        "mockup",
        "criativo",
        "criativa",
        "copy",
        "headline",
        "subheadline",
        "cta",
        "publico",
        "publico alvo",
        "persona",
        "formato",
        "feed",
        "stories",
        "story",
        "carrossel",
        "anuncio",
        "ads",
        "trafego",
        "a b",
        "a/b",
        "teste a/b",
    ]
    normalized = _normalize_key(texto)
    return any(term in normalized for term in terms)


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


def _normalize_mode(modo: Optional[str]) -> Optional[str]:
    if not modo:
        return None
    normalized = str(modo).strip().upper()
    allowed = {
        "LOGO",
        "FC",
        "REZETA",
        "CRIADORLANDPAGE",
        "CRIADORPROMPT",
        "CRIADORWEB",
    }
    return normalized if normalized in allowed else None


def _normalize_key(texto: str) -> str:
    normalized = unicodedata.normalize("NFKD", (texto or ""))
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", without_accents.lower()).strip()


def _normalize_formato_value(value: str) -> str:
    normalized = _normalize_key(value)
    if "9 16" in normalized or "stories" in normalized or "story" in normalized:
        return "9:16"
    if "4 5" in normalized or "feed" in normalized:
        return "4:5"
    if "1 1" in normalized or "quadrado" in normalized or "square" in normalized:
        return "1:1"
    if "16 9" in normalized or "banner" in normalized:
        return "16:9"
    return value.strip()


def _normalize_publico_value(value: str) -> str:
    normalized = _normalize_key(value)
    if any(term in normalized for term in ("pf", "pessoa fisica", "pessoas fisicas", "publico geral", "geral")):
        return "Publico geral (PF)"
    if any(term in normalized for term in ("mei", "microempreendedor", "micro empreendedor")):
        return "Microempreendedores (MEI)"
    if any(term in normalized for term in ("empresarios", "gestores", "pequenas empresas", "pj")):
        return "Empresarios e gestores"
    return value.strip()


def _is_affirmative(texto: str) -> bool:
    normalized = _normalize_key(texto)
    return normalized in {
        "sim",
        "ok",
        "pode",
        "pode sim",
        "confirmo",
        "usar cta padrao",
        "usar cta padrão",
        "cta padrao",
        "cta padrão",
    }


def _is_logo_request(texto: str) -> bool:
    normalized = _normalize_key(texto)
    logo_terms = (
        "logo",
        "logotipo",
        "identidade visual",
        "marca",
    )
    return any(term in normalized for term in logo_terms)


def _is_generation_confirmation(texto: str) -> bool:
    normalized = _normalize_key(texto)
    if normalized in {
        "sim",
        "ok",
        "pode",
        "pode gerar",
        "gerar",
        "gera",
        "versao final",
        "versao final png",
        "png",
        "jpg",
        "jpeg",
        "manda",
        "enviar",
    }:
        return True
    return bool(re.search(r"\b(gera|gerar|final|png|jpg)\b", normalized))


def _extract_publico_option(texto: str) -> Optional[str]:
    normalized = _normalize_key(texto)
    if normalized == "1":
        return "Publico geral (PF)"
    if normalized == "2":
        return "Microempreendedores (MEI)"
    if normalized == "3":
        return "Jovens 18-35 com credito e cartao"
    return None


def _apply_campaign_defaults(fields: Dict[str, str]) -> Dict[str, str]:
    normalized = dict(fields or {})
    normalized.setdefault("objetivo", "Geracao de leads")
    normalized.setdefault("publico", "Publico geral (PF)")
    normalized.setdefault("formato", "4:5")
    normalized.setdefault("cta", "Saiba mais")
    return normalized


def _extract_campaign_brief_fields(texto: str) -> Dict[str, str]:
    lines = [line.strip() for line in (texto or "").splitlines() if ":" in line]
    mapping = {
        "objetivo": "objetivo",
        "objetivo da campanha": "objetivo",
        "publico": "publico",
        "publico alvo": "publico",
        "persona": "publico",
        "formato": "formato",
        "fortato": "formato",
        "headline": "headline",
        "titulo": "headline",
        "titulo principal": "headline",
        "subheadline": "subheadline",
        "subtitulo": "subheadline",
        "subtitulo apoio": "subheadline",
        "cta": "cta",
        "chamada": "cta",
        "call to action": "cta",
        "oferta": "oferta",
        "desconto": "oferta",
        "tema": "tema",
        "campanha": "tema",
        "cena": "cena",
        "descricao da cena": "cena",
    }

    fields: Dict[str, str] = {}
    for line in lines:
        raw_key, raw_value = line.split(":", 1)
        value = raw_value.strip()
        if not value:
            continue
        normalized_key = _normalize_key(raw_key)
        mapped = mapping.get(normalized_key)
        if mapped:
            fields[mapped] = value

    # Extract from free sentence style:
    # "objetivo da campanha e ... publico ... formato feed ..."
    normalized_sentence = _normalize_key(texto or "")
    sentence_patterns = {
        "objetivo": r"objetivo(?: da campanha)?(?: e| eh| =)? (.*?)(?= publico| formato| fortato| cta| tema| oferta| headline| subheadline| cena|$)",
        "publico": r"publico(?: alvo)?(?: e| eh| =)? (.*?)(?= objetivo| formato| fortato| cta| tema| oferta| headline| subheadline| cena|$)",
        "formato": r"(?:formato|fortato)(?: e| eh| =)? (.*?)(?= objetivo| publico| cta| tema| oferta| headline| subheadline| cena|$)",
        "cta": r"cta(?: e| eh| =)? (.*?)(?= objetivo| publico| formato| fortato| tema| oferta| headline| subheadline| cena|$)",
        "tema": r"tema(?: e| eh| =)? (.*?)(?= objetivo| publico| formato| fortato| cta| oferta| headline| subheadline| cena|$)",
        "oferta": r"oferta(?: e| eh| =)? (.*?)(?= objetivo| publico| formato| fortato| cta| tema| headline| subheadline| cena|$)",
        "headline": r"headline(?: e| eh| =)? (.*?)(?= objetivo| publico| formato| fortato| cta| tema| oferta| subheadline| cena|$)",
        "subheadline": r"subheadline(?: e| eh| =)? (.*?)(?= objetivo| publico| formato| fortato| cta| tema| oferta| headline| cena|$)",
        "cena": r"cena(?: e| eh| =)? (.*?)(?= objetivo| publico| formato| fortato| cta| tema| oferta| headline| subheadline|$)",
    }

    for key, pattern in sentence_patterns.items():
        if fields.get(key):
            continue
        match = re.search(pattern, normalized_sentence)
        if not match:
            continue
        value = (match.group(1) or "").strip(" ,.;")
        if not value:
            continue
        fields[key] = value

    if fields.get("formato"):
        fields["formato"] = _normalize_formato_value(fields["formato"])
    if fields.get("publico"):
        fields["publico"] = _normalize_publico_value(fields["publico"])

    return fields


def _infer_campaign_fields_from_free_text(texto: str) -> Dict[str, str]:
    normalized = _normalize_key(texto)
    inferred: Dict[str, str] = {}

    if "9 16" in normalized or "stories" in normalized or "story" in normalized:
        inferred["formato"] = "9:16"
    elif "4 5" in normalized or "feed" in normalized:
        inferred["formato"] = "4:5"
    elif "1 1" in normalized or "quadrado" in normalized or "square" in normalized:
        inferred["formato"] = "1:1"
    elif "16 9" in normalized or "banner" in normalized:
        inferred["formato"] = "16:9"

    if (
        "publico geral" in normalized
        or "pessoas fisicas" in normalized
        or "pessoa fisica" in normalized
        or "pf em geral" in normalized
        or "pf geral" in normalized
    ):
        inferred["publico"] = "Publico geral (PF)"
    elif "microempreendedor" in normalized or "mei" in normalized:
        inferred["publico"] = "Microempreendedores (MEI)"
    elif "pequenas empresas" in normalized or "gestores" in normalized or "empresarios" in normalized:
        inferred["publico"] = "Empresarios e gestores"

    cta_candidates = [
        "saiba mais",
        "conheca como",
        "ver como funciona",
        "quero meu nome limpo",
        "comecar agora",
    ]
    for candidate in cta_candidates:
        if candidate in normalized:
            inferred["cta"] = candidate.title()
            break

    if "lead" in normalized or "captacao" in normalized:
        inferred["objetivo"] = "Geracao de leads"
    elif "convers" in normalized or "fechamento" in normalized or "venda" in normalized:
        inferred["objetivo"] = "Conversao"
    elif "reconhecimento" in normalized or "awareness" in normalized:
        inferred["objetivo"] = "Reconhecimento de marca"

    if "carnaval" in normalized:
        inferred["tema"] = "Campanha de Carnaval"

    discount_match = re.search(r"(\d{1,2})\s*%|\b(\d{1,2})\s+por cento\b", normalized)
    if discount_match:
        pct = discount_match.group(1) or discount_match.group(2)
        inferred["oferta"] = f"Desconto de {pct}% no servico"

    return inferred


def _collect_campaign_fields_from_context(contexto: List[Dict[str, Any]]) -> Dict[str, str]:
    collected: Dict[str, str] = {}
    for msg in contexto or []:
        if str(msg.get("tipo") or "") != "usuario":
            continue
        content = str(msg.get("conteudo") or "").strip()
        if not content:
            continue
        explicit = _extract_campaign_brief_fields(content)
        inferred = _infer_campaign_fields_from_free_text(content)
        collected.update(inferred)
        collected.update(explicit)
    return collected


def _missing_campaign_fields(fields: Dict[str, str]) -> List[str]:
    required = ["objetivo", "publico", "formato"]
    return [field for field in required if not fields.get(field)]


def _has_pending_campaign_brief(contexto: List[Dict[str, Any]]) -> bool:
    for msg in reversed(contexto or []):
        if msg.get("tipo") != "ia":
            continue
        content = str(msg.get("conteudo") or "").lower()
        if (
            "brief da campanha" in content
            or "so preciso fechar" in content
            or "faltam:" in content
        ):
            return True
    return False


def _compose_campaign_brief_text(mensagem: str, fields: Dict[str, str], modo: str) -> str:
    brand = "FC Solucoes Financeiras" if modo == "FC" else "RezetaBrasil"
    cta = fields.get("cta") or "Saiba mais"
    parts: List[str] = [
        f"Marca: {brand}",
        f"Tema: {fields.get('tema') or _extract_subject(mensagem)}",
        f"Objetivo: {fields.get('objetivo')}",
        f"Publico: {fields.get('publico')}",
        f"Formato: {fields.get('formato')}",
        f"CTA: {cta}",
    ]
    if fields.get("headline"):
        parts.append(f"Headline: {fields.get('headline')}")
    if fields.get("subheadline"):
        parts.append(f"Subheadline: {fields.get('subheadline')}")
    if fields.get("oferta"):
        parts.append(f"Oferta: {fields.get('oferta')}")
    if fields.get("cena"):
        parts.append(f"Cena: {fields.get('cena')}")
    return "\n".join(parts)


def _build_campaign_brief_reply(modo: str, missing_fields: List[str]) -> str:
    labels = {
        "objetivo": "objetivo da campanha",
        "publico": "publico-alvo",
        "formato": "formato da arte",
    }
    missing_text = ", ".join(labels.get(field, field) for field in missing_fields)
    brand = "FC" if modo == "FC" else "Rezeta"
    return (
        f"Modo {brand} confirmado. Para gerar a campanha com qualidade, so preciso fechar: {missing_text}.\n\n"
        "Pode responder em texto natural (sem formato fixo). Exemplo:\n"
        "`objetivo: gerar leads | publico: PF geral | formato: 4:5`.\n"
        "Se quiser, eu uso CTA padrao automaticamente."
    )


def _sanitize_fake_asset_delivery_reply(resposta: str, modo: Optional[str]) -> str:
    if modo not in ("FC", "REZETA"):
        return resposta

    lower = (resposta or "").lower()
    normalized = _normalize_key(resposta or "")
    has_fake_signal = (
        "http://" in lower
        or "https://" in lower
        or "marketing > campanhas" in lower
        or "files." in lower
        or "link de download" in normalized
        or "publiquei" in normalized
        or "publiquei os arquivos" in normalized
        or "enviei ao projeto" in normalized
        or "subi no projeto" in normalized
    )
    if not has_fake_signal:
        return resposta

    return (
        "Nao consigo publicar arquivos nem gerar links externos diretamente pelo chat. "
        "Consigo gerar a imagem aqui no fluxo da VIVA e anexar no proprio chat para revisao/download."
    )


def _derive_campaign_title(
    modo: str,
    campaign_copy: Optional[Dict[str, Any]] = None,
    fallback_message: Optional[str] = None,
) -> str:
    if campaign_copy and str(campaign_copy.get("headline") or "").strip():
        return _sanitize_prompt(str(campaign_copy.get("headline")), 120)

    subject = _extract_subject(fallback_message or "")
    brand = "FC" if modo == "FC" else "Rezeta"
    if subject and subject.lower() != "imagem promocional institucional":
        return _sanitize_prompt(f"{brand} - {subject}", 120)
    return f"Campanha {brand}"


async def _ensure_campaigns_table(db: AsyncSession) -> None:
    await db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS viva_campanhas (
                id UUID PRIMARY KEY,
                user_id UUID REFERENCES users(id) ON DELETE SET NULL,
                modo VARCHAR(32) NOT NULL,
                titulo VARCHAR(255) NOT NULL,
                briefing TEXT,
                mensagem_original TEXT,
                image_url TEXT NOT NULL,
                overlay_json JSONB NOT NULL DEFAULT '{}'::jsonb,
                meta_json JSONB NOT NULL DEFAULT '{}'::jsonb,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ
            )
            """
        )
    )
    await db.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_viva_campanhas_created_at
            ON viva_campanhas(created_at DESC)
            """
        )
    )
    await db.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_viva_campanhas_user_id
            ON viva_campanhas(user_id)
            """
        )
    )
    await db.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_viva_campanhas_modo
            ON viva_campanhas(modo)
            """
        )
    )


def _campaign_row_to_item(row: Any) -> CampanhaItem:
    return CampanhaItem(
        id=row.id,
        modo=row.modo,
        titulo=row.titulo,
        briefing=row.briefing,
        mensagem_original=row.mensagem_original,
        image_url=row.image_url,
        overlay=row.overlay_json or {},
        meta=row.meta_json or {},
        created_at=row.created_at,
    )


async def _save_campaign_record(
    db: AsyncSession,
    user_id: Optional[UUID],
    modo: str,
    image_url: str,
    titulo: Optional[str],
    briefing: Optional[str],
    mensagem_original: Optional[str],
    overlay: Optional[Dict[str, Any]],
    meta: Optional[Dict[str, Any]],
) -> Optional[UUID]:
    if not image_url:
        return None

    await _ensure_campaigns_table(db)
    campaign_id = uuid4()
    now = datetime.now(timezone.utc)
    await db.execute(
        text(
            """
            INSERT INTO viva_campanhas (
                id, user_id, modo, titulo, briefing, mensagem_original, image_url,
                overlay_json, meta_json, created_at, updated_at
            )
            VALUES (
                :id, :user_id, :modo, :titulo, :briefing, :mensagem_original, :image_url,
                CAST(:overlay_json AS JSONB), CAST(:meta_json AS JSONB), :created_at, :updated_at
            )
            """
        ),
        {
            "id": str(campaign_id),
            "user_id": str(user_id) if user_id else None,
            "modo": modo,
            "titulo": _sanitize_prompt(titulo or f"Campanha {modo}", 255),
            "briefing": briefing,
            "mensagem_original": mensagem_original,
            "image_url": image_url,
            "overlay_json": json.dumps(overlay or {}, ensure_ascii=False),
            "meta_json": json.dumps(meta or {}, ensure_ascii=False),
            "created_at": now,
            "updated_at": now,
        },
    )
    return campaign_id


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
    scene_lower = str(scene).lower()
    carnaval_hint = (
        " Elementos de carnaval devem ser sutis e elegantes (confetes em azul, atmosfera alegre sem fantasia caricata)."
        if "carnaval" in scene_lower
        else ""
    )
    if modo == "FC":
        return (
            "Fotografia publicitária corporativa premium, contexto financeiro no Brasil, "
            "escritório moderno, iluminação natural, composição clean, tons azul institucional "
            "(#071c4a, #00a3ff, #010a1c), sem verde, sem texto, sem letras, sem logotipo. "
            f"{carnaval_hint} Cena: {scene}"
        )
    return (
        "Fotografia publicitária realista e humanizada para campanha de crédito no Brasil, "
        "ambiente moderno e acolhedor, tom de confiança e esperança, cores com presença de "
        "azul marinho e verde esmeralda (#1E3A5F, #3DAA7F, #2A8B68), sem texto, sem letras, sem logotipo."
        f"{carnaval_hint} Cena: {scene}"
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


def _parse_datetime_input(raw: str) -> Optional[datetime]:
    value = " ".join((raw or "").replace(",", " ").split())
    formats = (
        "%d/%m/%Y %H:%M",
        "%d/%m/%y %H:%M",
        "%Y-%m-%d %H:%M",
        "%d-%m-%Y %H:%M",
    )
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _infer_event_type(title: str) -> EventoTipo:
    text = (title or "").lower()
    if "ligar" in text or "ligacao" in text or "ligação" in text:
        return EventoTipo.LIGACAO
    if "prazo" in text or "vencimento" in text:
        return EventoTipo.PRAZO
    if "reuniao" in text or "reunião" in text:
        return EventoTipo.REUNIAO
    return EventoTipo.OUTRO


def _parse_agenda_command(message: str) -> Optional[Dict[str, Any]]:
    text = (message or "").strip()
    if not text:
        return None

    lower = text.lower()
    if not (lower.startswith("agendar") or lower.startswith("agenda")):
        return None

    payload = re.sub(r"^(agendar|agenda)\s*:?\s*", "", text, flags=re.IGNORECASE).strip()
    if not payload:
        return {"error": "Formato vazio"}

    title = ""
    date_time_raw = ""
    description = None

    if "|" in payload:
        parts = [p.strip() for p in payload.split("|") if p.strip()]
        if len(parts) < 2:
            return {"error": "Formato incompleto"}
        title = parts[0]
        date_time_raw = parts[1]
        description = parts[2] if len(parts) >= 3 else None
    else:
        match = re.search(
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s+\d{1,2}:\d{2}|\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2})",
            payload,
        )
        if not match:
            return {"error": "Sem data/hora valida"}
        date_time_raw = match.group(1)
        title = payload.replace(date_time_raw, "").strip(" -")

    date_time = _parse_datetime_input(date_time_raw)
    if not date_time:
        return {"error": "Data/hora invalida"}

    if not title:
        title = "Compromisso com cliente"

    return {
        "title": title,
        "date_time": date_time,
        "description": description,
        "tipo": _infer_event_type(title),
    }


# ============================================
# CHAT
# ============================================
@router.post("/chat", response_model=ChatResponse)
async def chat_with_viva(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Chat direto com a VIVA usando OpenAI como provedor institucional."""
    try:
        agenda_command = _parse_agenda_command(request.mensagem)
        if agenda_command:
            if agenda_command.get("error"):
                return ChatResponse(
                    resposta=(
                        "Para agendar, use: "
                        "agendar TITULO | DD/MM/AAAA HH:MM | descricao opcional"
                    )
                )

            service = AgendaService(db)
            evento = await service.create(
                EventoCreate(
                    titulo=agenda_command["title"],
                    descricao=agenda_command.get("description"),
                    tipo=agenda_command["tipo"],
                    data_inicio=agenda_command["date_time"],
                    data_fim=None,
                    cliente_id=None,
                    contrato_id=None,
                ),
                current_user.id,
            )
            return ChatResponse(
                resposta=(
                    "Agendamento criado com sucesso: "
                    f"{evento.titulo} em {evento.data_inicio.strftime('%d/%m/%Y %H:%M')}."
                )
            )

        modo = _normalize_mode(request.modo)
        if not modo:
            for msg in reversed(request.contexto):
                maybe_mode = _normalize_mode(msg.get("modo"))
                if maybe_mode:
                    modo = maybe_mode
                    break

        prompt_extra_raw = request.prompt_extra.strip() if request.prompt_extra else None
        prompt_extra_chat = _sanitize_prompt(prompt_extra_raw, 4000) if prompt_extra_raw else None
        prompt_extra_image = _sanitize_prompt(prompt_extra_raw, 1200) if prompt_extra_raw else None

        campaign_flow_requested = False
        campaign_fields: Dict[str, str] = {}
        campaign_missing_fields: List[str] = []
        campaign_prompt_source = request.mensagem
        pending_brief = _has_pending_campaign_brief(request.contexto)
        logo_request = _is_logo_request(request.mensagem)
        generation_confirmation = _is_generation_confirmation(request.mensagem)

        if modo in ("FC", "REZETA") and not logo_request:
            campaign_fields = _collect_campaign_fields_from_context(request.contexto)
            inferred_fields = _infer_campaign_fields_from_free_text(request.mensagem)
            explicit_fields = _extract_campaign_brief_fields(request.mensagem)
            option_publico = _extract_publico_option(request.mensagem)
            if option_publico:
                campaign_fields["publico"] = option_publico
            campaign_fields.update(inferred_fields)
            campaign_fields.update(explicit_fields)
            message_campaign_related = (
                _is_image_request(request.mensagem)
                or _is_campaign_request(request.mensagem)
                or bool(inferred_fields)
                or bool(explicit_fields)
                or bool(option_publico)
            )
            campaign_flow_requested = (
                message_campaign_related
                or (pending_brief and (generation_confirmation or bool(option_publico)))
            )
            if campaign_flow_requested:
                campaign_fields = _apply_campaign_defaults(campaign_fields)
                campaign_missing_fields = _missing_campaign_fields(campaign_fields)
                campaign_prompt_source = _compose_campaign_brief_text(
                    request.mensagem,
                    campaign_fields,
                    modo,
                )

        should_generate_image = _is_image_request(request.mensagem) or (
            campaign_flow_requested and (not campaign_missing_fields or generation_confirmation)
        )

        if should_generate_image:
            if not settings.OPENAI_API_KEY:
                return ChatResponse(resposta="A geracao de imagens esta indisponivel no momento.")

            effective_mode = "LOGO" if logo_request else modo
            prompt_extra_image_effective = None if logo_request else prompt_extra_image
            hint = _mode_hint(effective_mode)
            campaign_copy: Optional[Dict[str, Any]] = None

            if effective_mode in ("FC", "REZETA"):
                campaign_copy = await _generate_campaign_copy(
                    campaign_prompt_source,
                    prompt_extra_image_effective,
                    effective_mode,
                )
                prompt = _build_branded_background_prompt(effective_mode, campaign_copy)
            else:
                prompt = _build_image_prompt(prompt_extra_image_effective, hint, request.mensagem)
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
                            media_meta = {"overlay": campaign_copy} if campaign_copy else {}
                            resposta_texto = "Imagem gerada com sucesso."
                            if effective_mode in ("FC", "REZETA"):
                                saved_id = await _save_campaign_record(
                                    db=db,
                                    user_id=current_user.id,
                                    modo=effective_mode,
                                    image_url=url,
                                    titulo=_derive_campaign_title(effective_mode, campaign_copy, request.mensagem),
                                    briefing=campaign_prompt_source,
                                    mensagem_original=request.mensagem,
                                    overlay=campaign_copy or {},
                                    meta={
                                        "source": "viva_chat",
                                        "size": "1024x1024",
                                        "fallback": True,
                                    },
                                )
                                if saved_id:
                                    media_meta["campanha_id"] = str(saved_id)
                                    resposta_texto = "Imagem gerada com sucesso e salva em Campanhas."
                            media = MediaItem(tipo="imagem", url=url, meta=media_meta or None)
                            return ChatResponse(resposta=resposta_texto, midia=[media])
                        return ChatResponse(resposta="A imagem foi solicitada, mas a API nao retornou URL.")

                msg = erro.get("message", "Erro desconhecido") if isinstance(erro, dict) else str(erro)
                return ChatResponse(resposta=f"Erro ao gerar imagem: {msg}")

            url = _extract_image_url(resultado)
            if url:
                media_meta = {"overlay": campaign_copy} if campaign_copy else {}
                resposta_texto = "Imagem gerada com sucesso."
                if effective_mode in ("FC", "REZETA"):
                    saved_id = await _save_campaign_record(
                        db=db,
                        user_id=current_user.id,
                        modo=effective_mode,
                        image_url=url,
                        titulo=_derive_campaign_title(effective_mode, campaign_copy, request.mensagem),
                        briefing=campaign_prompt_source,
                        mensagem_original=request.mensagem,
                        overlay=campaign_copy or {},
                        meta={
                            "source": "viva_chat",
                            "size": "1024x1024",
                            "fallback": False,
                        },
                    )
                    if saved_id:
                        media_meta["campanha_id"] = str(saved_id)
                        resposta_texto = "Imagem gerada com sucesso e salva em Campanhas."
                media = MediaItem(tipo="imagem", url=url, meta=media_meta)
                return ChatResponse(resposta=resposta_texto, midia=[media])
            return ChatResponse(resposta="A imagem foi solicitada, mas a API nao retornou URL.")

        if not settings.OPENAI_API_KEY:
            messages = viva_local_service.build_messages(request.mensagem, request.contexto)
            resposta = await viva_local_service.chat(messages, modo)
        else:
            messages = openrouter_service.build_messages(request.mensagem, request.contexto)
            should_inject_prompt = bool(prompt_extra_chat) and (
                modo not in ("FC", "REZETA")
                or campaign_flow_requested
                or _is_image_request(request.mensagem)
                or _is_campaign_request(request.mensagem)
            )
            if should_inject_prompt:
                messages.insert(1, {"role": "system", "content": prompt_extra_chat})
            resposta = await viva_model_service.chat(
                messages=messages,
                temperature=0.58,
                max_tokens=700,
            )
            if not resposta or resposta.strip().lower().startswith(("erro", "error")):
                messages_local = viva_local_service.build_messages(request.mensagem, request.contexto)
                resposta = await viva_local_service.chat(messages_local, modo)

        resposta = _sanitize_fake_asset_delivery_reply(resposta, modo)
        resposta = _ensure_fabio_greeting(request.mensagem, resposta)
        return ChatResponse(resposta=resposta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


@router.post("/campanhas", response_model=CampanhaItem)
async def save_campanha(
    payload: CampanhaSaveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    modo = _normalize_mode(payload.modo)
    if modo not in ("FC", "REZETA"):
        raise HTTPException(status_code=400, detail="Modo de campanha invalido.")

    try:
        title = payload.titulo or _derive_campaign_title(
            modo,
            payload.overlay or {},
            payload.mensagem_original or payload.briefing or "",
        )
        campaign_id = await _save_campaign_record(
            db=db,
            user_id=current_user.id,
            modo=modo,
            image_url=payload.image_url,
            titulo=title,
            briefing=payload.briefing,
            mensagem_original=payload.mensagem_original,
            overlay=payload.overlay or {},
            meta=payload.meta or {},
        )
        if not campaign_id:
            raise HTTPException(status_code=400, detail="URL da imagem obrigatoria.")

        result = await db.execute(
            text(
                """
                SELECT id, modo, titulo, briefing, mensagem_original, image_url, overlay_json, meta_json, created_at
                FROM viva_campanhas
                WHERE id = :id
                """
            ),
            {"id": str(campaign_id)},
        )
        row = result.first()
        if not row:
            raise HTTPException(status_code=500, detail="Falha ao salvar campanha.")
        return _campaign_row_to_item(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar campanha: {str(e)}")


@router.get("/campanhas", response_model=CampanhaListResponse)
async def list_campanhas(
    modo: Optional[str] = None,
    limit: int = 30,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    safe_limit = min(max(limit, 1), 200)
    safe_offset = max(offset, 0)
    normalized_mode = _normalize_mode(modo) if modo else None

    try:
        await _ensure_campaigns_table(db)
        params: Dict[str, Any] = {
            "user_id": str(current_user.id),
            "limit": safe_limit,
            "offset": safe_offset,
        }

        where_clause = "WHERE user_id = :user_id"
        if normalized_mode in ("FC", "REZETA"):
            where_clause += " AND modo = :modo"
            params["modo"] = normalized_mode

        rows_result = await db.execute(
            text(
                f"""
                SELECT id, modo, titulo, briefing, mensagem_original, image_url, overlay_json, meta_json, created_at
                FROM viva_campanhas
                {where_clause}
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        )
        items = [_campaign_row_to_item(row) for row in rows_result.fetchall()]

        count_result = await db.execute(
            text(
                f"""
                SELECT COUNT(*) AS total
                FROM viva_campanhas
                {where_clause}
                """
            ),
            {k: v for k, v in params.items() if k in ("user_id", "modo")},
        )
        total = int(count_result.scalar() or 0)
        return CampanhaListResponse(items=items, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar campanhas: {str(e)}")


@router.get("/campanhas/{campanha_id}", response_model=CampanhaItem)
async def get_campanha(
    campanha_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await _ensure_campaigns_table(db)
        result = await db.execute(
            text(
                """
                SELECT id, modo, titulo, briefing, mensagem_original, image_url, overlay_json, meta_json, created_at
                FROM viva_campanhas
                WHERE id = :id AND user_id = :user_id
                """
            ),
            {"id": str(campanha_id), "user_id": str(current_user.id)},
        )
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Campanha nao encontrada.")
        return _campaign_row_to_item(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar campanha: {str(e)}")

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








