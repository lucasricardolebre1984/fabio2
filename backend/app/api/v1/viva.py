"""
Chat direto com a VIVA - Assistente Virtual Interna
Usa OpenAI para Chat, Visao, Audio e Imagem
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
import base64
import json
import re
import unicodedata
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.agenda import EventoCreate
from app.services.agenda_service import AgendaService
from app.services.viva_local_service import viva_local_service
from app.services.viva_model_service import viva_model_service
from app.services.viva_concierge_service import viva_concierge_service
from app.services.viva_agenda_nlu_service import viva_agenda_nlu_service
from app.services.viva_handoff_service import viva_handoff_service
from app.services.viva_capabilities_service import viva_capabilities_service
from app.services.openai_service import openai_service
from app.config import settings

router = APIRouter()


class ChatRequest(BaseModel):
    mensagem: str
    contexto: List[Dict[str, Any]] = []
    prompt_extra: Optional[str] = None
    modo: Optional[str] = None
    session_id: Optional[UUID] = None


class MediaItem(BaseModel):
    tipo: str
    url: str
    nome: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    resposta: str
    midia: Optional[List[MediaItem]] = None
    session_id: Optional[UUID] = None


class ChatMessageItem(BaseModel):
    id: UUID
    tipo: str
    conteudo: str
    modo: Optional[str] = None
    anexos: List[Dict[str, Any]] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ChatSnapshotResponse(BaseModel):
    session_id: Optional[UUID] = None
    modo: Optional[str] = None
    messages: List[ChatMessageItem] = Field(default_factory=list)


class ChatSessionStartRequest(BaseModel):
    modo: Optional[str] = None


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


class VivaCapabilitiesResponse(BaseModel):
    items: List[Dict[str, Any]]


class HandoffScheduleRequest(BaseModel):
    cliente_numero: str
    mensagem: str
    scheduled_for: datetime
    cliente_nome: Optional[str] = None
    agenda_event_id: Optional[UUID] = None
    meta: Optional[Dict[str, Any]] = None


class HandoffItem(BaseModel):
    id: UUID
    user_id: UUID
    agenda_event_id: Optional[UUID] = None
    cliente_nome: Optional[str] = None
    cliente_numero: str
    mensagem: str
    scheduled_for: datetime
    status: str
    attempts: int = 0
    sent_at: Optional[datetime] = None
    last_error: Optional[str] = None
    meta_json: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None


class HandoffListResponse(BaseModel):
    items: List[HandoffItem]
    total: int
    page: int
    page_size: int


class HandoffProcessResponse(BaseModel):
    processed: int
    sent: int
    failed: int


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


def _build_viva_concierge_messages(
    mensagem: str,
    contexto: List[Dict[str, Any]],
    modo: Optional[str],
) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": viva_concierge_service.build_system_prompt(modo=modo)}
    ]
    for msg in contexto[-60:]:
        tipo = str(msg.get("tipo") or "")
        conteudo = str(msg.get("conteudo") or "").strip()
        if not conteudo:
            continue
        if tipo == "usuario":
            messages.append({"role": "user", "content": conteudo})
        elif tipo == "ia":
            messages.append({"role": "assistant", "content": conteudo})

    ultima_igual = (
        len(messages) > 1
        and messages[-1].get("role") == "user"
        and (messages[-1].get("content") or "").strip() == (mensagem or "").strip()
    )
    if not ultima_igual:
        messages.append({"role": "user", "content": mensagem})
    return messages


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


def _infer_mode_from_message(mensagem: str) -> Optional[str]:
    normalized = _normalize_key(mensagem or "")
    if not normalized:
        return None

    if "rezeta" in normalized:
        return "REZETA"
    if "fc" in normalized or "fc solucoes" in normalized or "fc solucoes financeiras" in normalized:
        return "FC"
    if "logo" in normalized or "logotipo" in normalized or "identidade visual" in normalized:
        return "LOGO"
    if "landing page" in normalized or "lp" in normalized:
        return "CRIADORLANDPAGE"
    return None


def _infer_mode_from_context(contexto: List[Dict[str, Any]]) -> Optional[str]:
    for msg in reversed(contexto or []):
        maybe_mode = _normalize_mode(msg.get("modo") if isinstance(msg, dict) else None)
        if maybe_mode:
            return maybe_mode
        conteudo = str(msg.get("conteudo") if isinstance(msg, dict) else "" or "")
        inferred = _infer_mode_from_message(conteudo)
        if inferred:
            return inferred
    return None


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


def _clean_extracted_value(value: str) -> str:
    cleaned = str(value or "").strip(" ,.;:-")
    cleaned = re.sub(r"\s+(a|o|e|de|do|da|para)$", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip(" ,.;:-")


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


def _is_direct_generation_intent(texto: str) -> bool:
    normalized = _normalize_key(texto)
    direct_patterns = (
        r"\b(gera|gerar|criar|produzir)\b.*\b(imagem|arte|post|banner|campanha)\b",
        r"\b(imagem|arte|post|banner|campanha)\b.*\b(gera|gerar|criar|produzir)\b",
        r"\bpode gerar\b",
        r"\bgerar agora\b",
    )
    return any(re.search(pattern, normalized) for pattern in direct_patterns)


def _campaign_gate_count(contexto: List[Dict[str, Any]]) -> int:
    count = 0
    for msg in contexto or []:
        if str(msg.get("tipo") or "") != "ia":
            continue
        content = _normalize_key(str(msg.get("conteudo") or ""))
        if (
            "so preciso fechar" in content
            or "sugestoes rapidas para sua campanha" in content
            or "responda 1 2 ou 3" in content
        ):
            count += 1
    return count


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
        "promocao": "oferta",
        "promo": "oferta",
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
        "objetivo": r"objetivo(?: da campanha)?(?: e| eh| =)? (.*?)(?= publico| formato| fortato| cta| tema| oferta| promocao| promo| desconto| headline| subheadline| cena|$)",
        "publico": r"publico(?: alvo)?(?: e| eh| =)? (.*?)(?= objetivo| formato| fortato| cta| tema| oferta| promocao| promo| desconto| headline| subheadline| cena|$)",
        "formato": r"(?:formato|fortato)(?: e| eh| =)? (.*?)(?= objetivo| publico| cta| tema| oferta| promocao| promo| desconto| headline| subheadline| cena|$)",
        "cta": r"cta(?: e| eh| =)? (.*?)(?= objetivo| publico| formato| fortato| tema| oferta| promocao| promo| desconto| headline| subheadline| cena|$)",
        "tema": r"tema(?: da campanha)?(?: e| eh| =)? (.*?)(?= objetivo| publico| formato| fortato| cta| oferta| promocao| promo| desconto| headline| subheadline| cena|$)",
        "oferta": r"(?:oferta|promocao|promo|desconto)(?: e| eh| =)? (.*?)(?= objetivo| publico| formato| fortato| cta| tema| headline| subheadline| cena|$)",
        "headline": r"headline(?: e| eh| =)? (.*?)(?= objetivo| publico| formato| fortato| cta| tema| oferta| promocao| promo| desconto| subheadline| cena|$)",
        "subheadline": r"subheadline(?: e| eh| =)? (.*?)(?= objetivo| publico| formato| fortato| cta| tema| oferta| promocao| promo| desconto| headline| cena|$)",
        "cena": r"cena(?: e| eh| =)? (.*?)(?= objetivo| publico| formato| fortato| cta| tema| oferta| promocao| promo| desconto| headline| subheadline|$)",
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
        fields[key] = _clean_extracted_value(value)

    if fields.get("formato"):
        fields["formato"] = _normalize_formato_value(fields["formato"])
    if fields.get("publico"):
        fields["publico"] = _normalize_publico_value(fields["publico"])
    for key in ("tema", "oferta", "headline", "subheadline", "cta", "cena"):
        if fields.get(key):
            fields[key] = _clean_extracted_value(fields[key])

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

    if not inferred.get("tema"):
        theme_match = re.search(
            r"tema(?: da campanha)?(?: e| eh| =)? (.*?)(?= objetivo| publico| formato| cta| oferta| promocao| promo| desconto|$)",
            normalized,
        )
        if theme_match and str(theme_match.group(1) or "").strip():
            inferred["tema"] = _clean_extracted_value(str(theme_match.group(1)))
        elif "carnaval" in normalized:
            inferred["tema"] = "carnaval sem dividas" if "sem divida" in normalized else "carnaval"

    discount_match_raw = re.search(r"(\d{1,2})\s*%", texto or "", flags=re.IGNORECASE)
    discount_match_words = re.search(r"\b(\d{1,2})\s+por cento\b", normalized)
    if discount_match_raw or discount_match_words:
        pct = (
            (discount_match_raw.group(1) if discount_match_raw else None)
            or (discount_match_words.group(1) if discount_match_words else None)
            or ""
        )
        service_match = re.search(
            r"\b(limpa nome|aumento de score|score|rating|diagnostico 360|renegociacao|quitacao|credito)\b",
            normalized,
        )
        if service_match:
            service = str(service_match.group(1)).strip()
            inferred["oferta"] = f"Desconto de {pct}% em {service}"
        else:
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
        collected.update(explicit)
        collected.update(inferred)
    return collected


def _missing_campaign_fields(fields: Dict[str, str]) -> List[str]:
    required = ["objetivo", "publico", "formato"]
    return [field for field in required if not fields.get(field)]


def _has_pending_campaign_brief(contexto: List[Dict[str, Any]]) -> bool:
    for msg in reversed(contexto or []):
        if msg.get("tipo") != "ia":
            continue
        content = _normalize_key(str(msg.get("conteudo") or ""))
        if (
            "brief da campanha" in content
            or "so preciso fechar" in content
            or "faltam" in content
            or "sugestoes rapidas para sua campanha" in content
            or "me diga 1 2 ou 3 e eu gero agora" in content
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


def _build_scene_seed(fields: Dict[str, str], modo: str) -> str:
    tema = str(fields.get("tema") or "").strip()
    objetivo = str(fields.get("objetivo") or "gerar leads").strip()
    publico = str(fields.get("publico") or "publico geral").strip()
    oferta = str(fields.get("oferta") or "").strip()

    if modo == "FC":
        brand_style = "estetica FC com azul e branco (#071c4a, #00a3ff, #f9feff)"
    else:
        brand_style = "estetica Rezeta com verde e azul (#3DAA7F, #1E3A5F)"

    scene_parts: List[str] = [
        f"cena publicitaria realista com {brand_style}",
        f"foco em {objetivo}",
        f"publico {publico}",
    ]
    if tema:
        scene_parts.append(f"tema {tema}")
    if oferta:
        scene_parts.append(f"mensagem visual de oferta {oferta}")

    merged = " | ".join(scene_parts)
    low = _normalize_key(merged)
    if "escritorio" not in low and "terno" not in low and "corporativo" not in low:
        merged += " | evitar homem de terno e escritorio como padrao"
    return _sanitize_prompt(merged, 240)


def _build_campaign_quick_plan(modo: str, fields: Dict[str, str]) -> str:
    brand = "FC Solucoes Financeiras" if modo == "FC" else "RezetaBrasil"
    tema = fields.get("tema") or "tema livre"
    objetivo = fields.get("objetivo") or "gerar leads"
    publico = fields.get("publico") or "Publico geral (PF)"
    formato = fields.get("formato") or "4:5"
    oferta = fields.get("oferta") or "Sem oferta explicita"
    cta = fields.get("cta") or ("Ver como funciona" if modo == "FC" else "Chamar no WhatsApp")

    return (
        f"Perfeito. Entendi sua campanha para {brand}.\n"
        f"Tema: {tema} | Objetivo: {objetivo} | Publico: {publico} | Formato: {formato} | Oferta: {oferta}\n\n"
        "Sugestoes rapidas para sua campanha:\n"
        f"1) Conversao direta: headline objetiva + promessa clara + CTA '{cta}'.\n"
        f"2) Dor e alivio: problema real do publico + prova social + CTA '{cta}'.\n"
        f"3) Oferta forte: destaque da promocao + urgencia leve + CTA '{cta}'.\n\n"
        "Me diga 1, 2 ou 3 e eu gero agora. Se preferir, escreva: gerar agora."
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


def _is_handoff_whatsapp_intent(texto: str) -> bool:
    normalized = _normalize_key(texto)
    terms = (
        "avisar cliente",
        "avise cliente",
        "avisar no whatsapp",
        "avise no whatsapp",
        "lembrar cliente no whatsapp",
        "chamar cliente no whatsapp",
        "viviane avisar",
        "viviane lembrar",
    )
    return any(term in normalized for term in terms)


def _extract_phone_candidate(texto: str) -> Optional[str]:
    match = re.search(r"(\+?\d[\d\-\s\(\)]{9,})", texto or "")
    if not match:
        return None
    digits = re.sub(r"\D", "", match.group(1))
    if len(digits) < 10:
        return None
    if len(digits) > 13:
        digits = digits[-13:]
    return digits


def _extract_cliente_nome(texto: str) -> Optional[str]:
    match = re.search(r"cliente\s+([A-Za-zÀ-ÿ0-9 ]{2,80})", texto or "", flags=re.IGNORECASE)
    if not match:
        return None
    raw = re.split(r"\b(amanha|hoje|as|às|no|na|dia|whatsapp)\b", match.group(1), flags=re.IGNORECASE)[0]
    cleaned = " ".join(raw.split()).strip(" -,:;")
    return cleaned if len(cleaned) >= 2 else None


def _extract_handoff_custom_message(texto: str) -> Optional[str]:
    match = re.search(r"mensagem\s*:\s*(.+)$", texto or "", flags=re.IGNORECASE)
    if not match:
        return None
    msg = str(match.group(1) or "").strip()
    return msg or None


def _build_viviane_handoff_message(
    cliente_nome: Optional[str],
    evento_titulo: str,
    data_inicio: datetime,
    modo: Optional[str],
) -> str:
    company = "FC Solucoes Financeiras" if modo != "REZETA" else "RezetaBrasil"
    saudacao = f"Oi {cliente_nome}," if cliente_nome else "Oi,"
    return (
        f"{saudacao} aqui e a Viviane, secretaria da {company}. "
        f"Lembrete do seu compromisso: {evento_titulo} em {data_inicio.strftime('%d/%m/%Y as %H:%M')}. "
        "Se precisar remarcar, me responda por aqui."
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
        overlay=_safe_json(row.overlay_json, {}),
        meta=_safe_json(row.meta_json, {}),
        created_at=row.created_at,
    )


def _handoff_row_to_item(row: Any) -> HandoffItem:
    if isinstance(row, dict):
        return HandoffItem(
            id=row["id"],
            user_id=row["user_id"],
            agenda_event_id=row.get("agenda_event_id"),
            cliente_nome=row.get("cliente_nome"),
            cliente_numero=row["cliente_numero"],
            mensagem=row["mensagem"],
            scheduled_for=row["scheduled_for"],
            status=row["status"],
            attempts=int(row.get("attempts") or 0),
            sent_at=row.get("sent_at"),
            last_error=row.get("last_error"),
            meta_json=_safe_json(row.get("meta_json"), {}),
            created_at=row["created_at"],
            updated_at=row.get("updated_at"),
        )

    return HandoffItem(
        id=row.id,
        user_id=row.user_id,
        agenda_event_id=row.agenda_event_id,
        cliente_nome=row.cliente_nome,
        cliente_numero=row.cliente_numero,
        mensagem=row.mensagem,
        scheduled_for=row.scheduled_for,
        status=row.status,
        attempts=int(row.attempts or 0),
        sent_at=row.sent_at,
        last_error=row.last_error,
        meta_json=_safe_json(row.meta_json, {}),
        created_at=row.created_at,
        updated_at=row.updated_at,
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


async def _ensure_chat_tables(db: AsyncSession) -> None:
    await db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS viva_chat_sessions (
                id UUID PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                modo VARCHAR(32),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                last_message_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    await db.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_viva_chat_sessions_user_updated
            ON viva_chat_sessions(user_id, updated_at DESC)
            """
        )
    )
    await db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS viva_chat_messages (
                id UUID PRIMARY KEY,
                session_id UUID NOT NULL REFERENCES viva_chat_sessions(id) ON DELETE CASCADE,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                tipo VARCHAR(16) NOT NULL,
                conteudo TEXT NOT NULL,
                modo VARCHAR(32),
                anexos_json JSONB NOT NULL DEFAULT '[]'::jsonb,
                meta_json JSONB NOT NULL DEFAULT '{}'::jsonb,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    await db.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_viva_chat_messages_session_created
            ON viva_chat_messages(session_id, created_at DESC)
            """
        )
    )


def _safe_json(value: Any, fallback: Any) -> Any:
    if value is None:
        return fallback
    if isinstance(value, type(fallback)):
        return value
    if isinstance(fallback, dict) and isinstance(value, dict):
        return value
    if isinstance(fallback, list) and isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(fallback, dict) and isinstance(parsed, dict):
                return parsed
            if isinstance(fallback, list) and isinstance(parsed, list):
                return parsed
        except Exception:
            return fallback
    return fallback


def _serialize_media_items(items: Optional[List[MediaItem]]) -> List[Dict[str, Any]]:
    if not items:
        return []
    payload: List[Dict[str, Any]] = []
    for item in items:
        if isinstance(item, MediaItem):
            payload.append(item.model_dump(exclude_none=True))
        elif isinstance(item, dict):
            payload.append(item)
    return payload


async def _create_chat_session(db: AsyncSession, user_id: UUID, modo: Optional[str]) -> UUID:
    session_id = uuid4()
    now = datetime.now(timezone.utc)
    await db.execute(
        text(
            """
            INSERT INTO viva_chat_sessions (id, user_id, modo, created_at, updated_at, last_message_at)
            VALUES (:id, :user_id, :modo, :created_at, :updated_at, :last_message_at)
            """
        ),
        {
            "id": str(session_id),
            "user_id": str(user_id),
            "modo": _normalize_mode(modo),
            "created_at": now,
            "updated_at": now,
            "last_message_at": now,
        },
    )
    return session_id


async def _get_latest_chat_session_row(db: AsyncSession, user_id: UUID) -> Optional[Any]:
    result = await db.execute(
        text(
            """
            SELECT id, modo
            FROM viva_chat_sessions
            WHERE user_id = :user_id
            ORDER BY updated_at DESC
            LIMIT 1
            """
        ),
        {"user_id": str(user_id)},
    )
    return result.first()


async def _resolve_chat_session(
    db: AsyncSession,
    user_id: UUID,
    requested_session_id: Optional[UUID],
    modo: Optional[str],
) -> UUID:
    normalized_mode = _normalize_mode(modo)

    if requested_session_id:
        result = await db.execute(
            text(
                """
                SELECT id
                FROM viva_chat_sessions
                WHERE id = :id AND user_id = :user_id
                LIMIT 1
                """
            ),
            {"id": str(requested_session_id), "user_id": str(user_id)},
        )
        row = result.first()
        if row:
            await db.execute(
                text(
                    """
                    UPDATE viva_chat_sessions
                    SET modo = COALESCE(:modo, modo),
                        updated_at = NOW()
                    WHERE id = :id
                    """
                ),
                {"id": str(requested_session_id), "modo": normalized_mode},
            )
            return requested_session_id

    latest = await _get_latest_chat_session_row(db, user_id)
    if latest:
        await db.execute(
            text(
                """
                UPDATE viva_chat_sessions
                SET modo = COALESCE(:modo, modo),
                    updated_at = NOW()
                WHERE id = :id
                """
            ),
            {"id": str(latest.id), "modo": normalized_mode},
        )
        return latest.id

    return await _create_chat_session(db, user_id, normalized_mode)


async def _append_chat_message(
    db: AsyncSession,
    session_id: UUID,
    user_id: UUID,
    tipo: str,
    conteudo: str,
    modo: Optional[str] = None,
    anexos: Optional[List[Dict[str, Any]]] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    normalized_mode = _normalize_mode(modo)
    await db.execute(
        text(
            """
            INSERT INTO viva_chat_messages (
                id, session_id, user_id, tipo, conteudo, modo, anexos_json, meta_json, created_at
            )
            VALUES (
                :id, :session_id, :user_id, :tipo, :conteudo, :modo,
                CAST(:anexos_json AS JSONB), CAST(:meta_json AS JSONB), NOW()
            )
            """
        ),
        {
            "id": str(uuid4()),
            "session_id": str(session_id),
            "user_id": str(user_id),
            "tipo": tipo,
            "conteudo": conteudo,
            "modo": normalized_mode,
            "anexos_json": json.dumps(anexos or [], ensure_ascii=False),
            "meta_json": json.dumps(meta or {}, ensure_ascii=False),
        },
    )
    await db.execute(
        text(
            """
            UPDATE viva_chat_sessions
            SET modo = COALESCE(:modo, modo),
                updated_at = NOW(),
                last_message_at = NOW()
            WHERE id = :id AND user_id = :user_id
            """
        ),
        {
            "id": str(session_id),
            "user_id": str(user_id),
            "modo": normalized_mode,
        },
    )


def _chat_message_from_row(row: Any) -> ChatMessageItem:
    return ChatMessageItem(
        id=row.id,
        tipo=row.tipo,
        conteudo=row.conteudo,
        modo=row.modo,
        anexos=_safe_json(row.anexos_json, []),
        meta=_safe_json(row.meta_json, {}),
        created_at=row.created_at,
    )


async def _load_chat_snapshot(
    db: AsyncSession,
    user_id: UUID,
    session_id: UUID,
    limit: int,
) -> ChatSnapshotResponse:
    result = await db.execute(
        text(
            """
            SELECT id, modo
            FROM viva_chat_sessions
            WHERE id = :session_id AND user_id = :user_id
            LIMIT 1
            """
        ),
        {"session_id": str(session_id), "user_id": str(user_id)},
    )
    session_row = result.first()
    if not session_row:
        return ChatSnapshotResponse(session_id=None, modo=None, messages=[])

    safe_limit = min(max(limit, 1), 250)
    messages_result = await db.execute(
        text(
            """
            SELECT id, tipo, conteudo, modo, anexos_json, meta_json, created_at
            FROM (
                SELECT m.id, m.tipo, m.conteudo, m.modo, m.anexos_json, m.meta_json, m.created_at
                FROM viva_chat_messages m
                WHERE m.session_id = :session_id AND m.user_id = :user_id
                ORDER BY m.created_at DESC
                LIMIT :limit
            ) recent
            ORDER BY created_at ASC
            """
        ),
        {
            "session_id": str(session_id),
            "user_id": str(user_id),
            "limit": safe_limit,
        },
    )
    messages = [_chat_message_from_row(row) for row in messages_result.fetchall()]
    return ChatSnapshotResponse(session_id=session_row.id, modo=session_row.modo, messages=messages)


def _context_from_snapshot(snapshot: ChatSnapshotResponse) -> List[Dict[str, Any]]:
    contexto: List[Dict[str, Any]] = []
    for item in snapshot.messages:
        contexto.append(
            {
                "id": str(item.id),
                "tipo": item.tipo,
                "conteudo": item.conteudo,
                "modo": item.modo,
                "anexos": item.anexos,
                "meta": item.meta,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
        )
    return contexto


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
    bullet_lines = [ln for ln in lines if re.match(r"^([*+-]|[0-9]+\.)\s", ln)]
    explicit = _extract_campaign_brief_fields(texto)
    inferred = _infer_campaign_fields_from_free_text(texto)
    fields = _apply_campaign_defaults({**explicit, **inferred})

    headline = (
        str(fields.get("headline") or "").strip()
        or next((ln for ln in lines if ln not in bullet_lines), "")
        or "Resolva suas dividas com estrategia clara"
    )
    subheadline = (
        str(fields.get("subheadline") or "").strip()
        or next((ln for ln in lines[1:] if ln not in bullet_lines), "")
        or "Plano objetivo para organizar seu credito com seguranca"
    )
    offer = str(fields.get("oferta") or "").strip()
    cta = str(fields.get("cta") or "").strip() or (
        "CHAMAR NO WHATSAPP" if modo == "REZETA" else "VER COMO FUNCIONA"
    )

    default_bullets = [
        "Diagnostico rapido e objetivo",
        "Plano de acao adaptado ao seu perfil",
        "Acompanhamento claro do inicio ao fim",
    ]
    if offer:
        default_bullets[0] = offer

    scene = str(fields.get("cena") or "").strip() or _build_scene_seed(fields, modo)
    quote = next((ln for ln in lines if ln.startswith('"')), "")

    return {
        "brand": modo,
        "headline": _sanitize_prompt(headline, 90),
        "subheadline": _sanitize_prompt(subheadline, 130),
        "bullets": [_sanitize_prompt(item, 80) for item in (bullet_lines[:5] or default_bullets)],
        "quote": _sanitize_prompt(quote, 120) if quote else "",
        "cta": _sanitize_prompt(cta, 40),
        "scene": _sanitize_prompt(scene, 240),
    }


async def _generate_campaign_copy(
    mensagem: str,
    prompt_extra_image: Optional[str],
    modo: str,
) -> Dict[str, Any]:
    fonte = _sanitize_prompt(_extract_overlay_source(mensagem), 5000)
    baseline = _fallback_copy(fonte, modo)

    explicit = _extract_campaign_brief_fields(fonte)
    inferred = _infer_campaign_fields_from_free_text(fonte)
    fields = _apply_campaign_defaults({**explicit, **inferred})
    scene_seed = _build_scene_seed(fields, modo)

    if modo == "REZETA":
        guardrail = (
            "Marca RezetaBrasil. Paleta obrigatoria: #1E3A5F, #3DAA7F, #2A8B68, #FFFFFF. "
            "Tom humano e acessivel."
        )
    else:
        guardrail = (
            "Marca FC Solucoes Financeiras. Paleta obrigatoria: #071c4a, #00a3ff, #010a1c, #f9feff. "
            "Tom premium e consultivo."
        )

    system = (
        f"{guardrail}\n"
        "Voce e diretor(a) de criacao de campanhas financeiras. "
        "Responda apenas JSON valido e siga o brief. "
        "Nunca imponha homem de terno ou escritorio como padrao, "
        "a menos que o brief peca isso explicitamente."
    )

    brand_reference = _sanitize_prompt(prompt_extra_image or "", 1800)
    user = (
        "Brief da campanha:\n"
        f"{fonte}\n\n"
        f"Campos inferidos: objetivo={fields.get('objetivo')}; publico={fields.get('publico')}; "
        f"formato={fields.get('formato')}; tema={fields.get('tema')}; oferta={fields.get('oferta')}; cta={fields.get('cta')}.\n"
        f"Seed de cena: {scene_seed}\n"
        f"Referencia de marca: {brand_reference or 'nao informada'}\n\n"
        "Retorne JSON com chaves exatas:\n"
        "headline, subheadline, bullets (array 3-5), quote, cta, scene.\n"
        "scene deve refletir o tema/oferta do brief sem texto na imagem."
    )

    resposta = await openai_service.chat(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.35,
        max_tokens=800,
    )

    parsed = _extract_json_block(resposta)
    if not parsed:
        return baseline

    bullets = parsed.get("bullets") if isinstance(parsed.get("bullets"), list) else []
    bullets = [str(item).strip() for item in bullets if str(item).strip()][:5]

    return {
        "brand": modo,
        "headline": _sanitize_prompt(str(parsed.get("headline") or baseline["headline"]), 90),
        "subheadline": _sanitize_prompt(str(parsed.get("subheadline") or baseline["subheadline"]), 130),
        "bullets": bullets or baseline["bullets"],
        "quote": _sanitize_prompt(str(parsed.get("quote") or baseline.get("quote") or ""), 120),
        "cta": _sanitize_prompt(str(parsed.get("cta") or baseline["cta"]), 40),
        "scene": _sanitize_prompt(str(parsed.get("scene") or baseline["scene"]), 240),
    }


def _build_branded_background_prompt(modo: str, campaign_copy: Dict[str, Any]) -> str:
    scene = _sanitize_prompt(str(campaign_copy.get("scene") or ""), 240)
    normalized_scene = _normalize_key(scene)
    avoid_corporate_stereotype = (
        " Evitar estereotipo de homem de terno em escritorio, salvo se a cena pedir explicitamente."
        if ("terno" not in normalized_scene and "escritorio" not in normalized_scene)
        else ""
    )
    if modo == "FC":
        return (
            "Fotografia publicitaria realista para campanha financeira no Brasil. "
            "Identidade FC: azul e branco (#071c4a, #00a3ff, #010a1c, #f9feff). "
            "Sem texto, sem letras, sem logotipo. "
            f"{avoid_corporate_stereotype} Cena principal: {scene}"
        )
    return (
        "Fotografia publicitaria realista para campanha financeira no Brasil. "
        "Identidade Rezeta: verde e azul (#3DAA7F, #1E3A5F, #2A8B68, #FFFFFF). "
        "Sem texto, sem letras, sem logotipo. "
        f"{avoid_corporate_stereotype} Cena principal: {scene}"
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


# ============================================`r`n# CHAT`r`n# ============================================
@router.post("/chat", response_model=ChatResponse)
async def chat_with_viva(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Chat direto com a VIVA usando OpenAI como provedor institucional."""
    try:
        await _ensure_chat_tables(db)

        modo = (
            _normalize_mode(request.modo)
            or _infer_mode_from_message(request.mensagem)
            or _infer_mode_from_context(request.contexto)
        )

        session_id = await _resolve_chat_session(
            db=db,
            user_id=current_user.id,
            requested_session_id=request.session_id,
            modo=modo,
        )

        async def finalize(
            resposta: str,
            midia: Optional[List[MediaItem]] = None,
            meta: Optional[Dict[str, Any]] = None,
        ) -> ChatResponse:
            await _append_chat_message(
                db=db,
                session_id=session_id,
                user_id=current_user.id,
                tipo="ia",
                conteudo=resposta,
                modo=modo,
                anexos=_serialize_media_items(midia),
                meta=meta or {},
            )
            return ChatResponse(resposta=resposta, midia=midia, session_id=session_id)

        await _append_chat_message(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
            tipo="usuario",
            conteudo=request.mensagem,
            modo=modo,
            meta={"contexto_len": len(request.contexto or [])},
        )

        snapshot = await _load_chat_snapshot(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
            limit=180,
        )
        contexto_efetivo = _context_from_snapshot(snapshot)
        if not modo:
            modo = _normalize_mode(snapshot.modo) or _infer_mode_from_context(contexto_efetivo)

        service = AgendaService(db)
        agenda_query_intent = viva_agenda_nlu_service.is_agenda_query_intent(request.mensagem, contexto_efetivo)
        agenda_command = viva_agenda_nlu_service.parse_agenda_command(request.mensagem)
        agenda_natural_command = viva_agenda_nlu_service.parse_agenda_natural_create(request.mensagem)
        agenda_errors: List[str] = []
        agenda_create_payload: Optional[Dict[str, Any]] = None

        if agenda_command is not None:
            if agenda_command.get("error"):
                agenda_errors.append(str(agenda_command["error"]))
            else:
                agenda_create_payload = agenda_command

        if not agenda_create_payload and agenda_natural_command is not None:
            if agenda_natural_command.get("error"):
                agenda_errors.append(str(agenda_natural_command["error"]))
            else:
                agenda_create_payload = agenda_natural_command

        if agenda_create_payload:
            evento = await service.create(
                EventoCreate(
                    titulo=agenda_create_payload["title"],
                    descricao=agenda_create_payload.get("description"),
                    tipo=agenda_create_payload["tipo"],
                    data_inicio=agenda_create_payload["date_time"],
                    data_fim=None,
                    cliente_id=None,
                    contrato_id=None,
                ),
                current_user.id,
            )
            if _is_handoff_whatsapp_intent(request.mensagem):
                numero = _extract_phone_candidate(request.mensagem)
                cliente_nome = _extract_cliente_nome(request.mensagem)
                if not numero:
                    return await finalize(
                        resposta=(
                            "Agendamento criado com sucesso: "
                            f"{evento.titulo} em {evento.data_inicio.strftime('%d/%m/%Y %H:%M')}.\n"
                            "Para eu acionar a Viviane no horario, me passe o WhatsApp do cliente com DDD."
                        )
                    )

                handoff_msg = (
                    _extract_handoff_custom_message(request.mensagem)
                    or _build_viviane_handoff_message(
                        cliente_nome=cliente_nome,
                        evento_titulo=evento.titulo,
                        data_inicio=evento.data_inicio,
                        modo=modo,
                    )
                )
                task_id = await viva_handoff_service.schedule_task(
                    db=db,
                    user_id=current_user.id,
                    cliente_nome=cliente_nome,
                    cliente_numero=numero,
                    mensagem=handoff_msg,
                    scheduled_for=evento.data_inicio,
                    agenda_event_id=evento.id,
                    meta=json.dumps({"source": "viva_chat", "session_id": str(session_id)}, ensure_ascii=False),
                )
                return await finalize(
                    resposta=(
                        "Agendamento criado com sucesso: "
                        f"{evento.titulo} em {evento.data_inicio.strftime('%d/%m/%Y %H:%M')}.\n"
                        f"Handoff para Viviane agendado no WhatsApp (ID: {task_id})."
                    )
                )

            return await finalize(
                resposta=(
                    "Agendamento criado com sucesso: "
                    f"{evento.titulo} em {evento.data_inicio.strftime('%d/%m/%Y %H:%M')}."
                )
            )

        conclude_command = viva_agenda_nlu_service.parse_agenda_conclude_command(request.mensagem)
        if conclude_command is not None:
            if conclude_command.get("error"):
                return await finalize(
                    resposta=(
                        "Para concluir um compromisso, informe ID ou parte do titulo. "
                        "Exemplo: concluir reuniao com Fabio."
                    )
                )

            target_event_id: Optional[UUID] = conclude_command.get("evento_id")
            search_text = str(conclude_command.get("search_text") or "").strip()
            if not target_event_id and search_text:
                agenda_data = await service.list(
                    inicio=None,
                    fim=None,
                    concluido=False,
                    user_id=current_user.id,
                    page=1,
                    page_size=120,
                )
                items = list(agenda_data.get("items", []))
                normalized_search = _normalize_key(search_text)
                matches = [
                    item for item in items
                    if normalized_search in _normalize_key(getattr(item, "titulo", ""))
                ]
                if len(matches) == 1:
                    target_event_id = matches[0].id
                elif len(matches) > 1:
                    sugestoes = "\n".join(
                        f"- {m.titulo} ({m.data_inicio.strftime('%d/%m %H:%M')})"
                        for m in matches[:3]
                    )
                    return await finalize(
                        resposta=(
                            "Encontrei mais de um compromisso parecido. Me diga qual deseja concluir:\n"
                            f"{sugestoes}"
                        )
                    )

            if not target_event_id:
                return await finalize(resposta="Nao encontrei esse compromisso para concluir na sua agenda.")

            evento = await service.concluir(target_event_id, user_id=current_user.id)
            if not evento:
                return await finalize(resposta="Nao encontrei esse compromisso para concluir na sua agenda.")
            return await finalize(
                resposta=(
                    "Compromisso concluido com sucesso: "
                    f"{evento.titulo} ({evento.data_inicio.strftime('%d/%m/%Y %H:%M')})."
                )
            )

        if agenda_query_intent:
            inicio, fim, period_label = viva_agenda_nlu_service.agenda_window_from_text(request.mensagem)
            agenda_data = await service.list(
                inicio=inicio,
                fim=fim,
                concluido=None,
                user_id=current_user.id,
                page=1,
                page_size=120,
            )
            items = list(agenda_data.get("items", []))
            return await finalize(resposta=viva_agenda_nlu_service.format_agenda_list(items, period_label))

        if agenda_errors and (agenda_command is not None or agenda_natural_command is not None):
            return await finalize(
                resposta=viva_agenda_nlu_service.build_agenda_recovery_reply(
                    request.mensagem,
                    agenda_errors,
                )
            )

        campaign_flow_requested = False
        campaign_fields: Dict[str, str] = {}
        campaign_missing_fields: List[str] = []
        campaign_prompt_source = request.mensagem
        pending_brief = _has_pending_campaign_brief(contexto_efetivo)
        campaign_gate_count = _campaign_gate_count(contexto_efetivo)
        logo_request = _is_logo_request(request.mensagem)
        generation_confirmation = _is_generation_confirmation(request.mensagem)
        direct_generation_intent = _is_direct_generation_intent(request.mensagem)
        option_publico: Optional[str] = None

        if modo in ("FC", "REZETA") and not logo_request:
            campaign_fields = _collect_campaign_fields_from_context(contexto_efetivo)
            inferred_fields = _infer_campaign_fields_from_free_text(request.mensagem)
            explicit_fields = _extract_campaign_brief_fields(request.mensagem)
            option_publico = _extract_publico_option(request.mensagem)
            if option_publico:
                campaign_fields["publico"] = option_publico
            campaign_fields.update(explicit_fields)
            campaign_fields.update(inferred_fields)
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

        if (
            modo in ("FC", "REZETA")
            and campaign_flow_requested
            and not logo_request
            and not generation_confirmation
            and not direct_generation_intent
            and campaign_gate_count < 3
            and not _is_image_request(request.mensagem)
        ):
            return await finalize(resposta=_build_campaign_quick_plan(modo, campaign_fields))

        should_generate_image = _is_image_request(request.mensagem) or (
            campaign_flow_requested
            and (
                generation_confirmation
                or direct_generation_intent
                or bool(option_publico)
                or campaign_gate_count >= 3
                or not campaign_missing_fields
            )
        )

        if should_generate_image:
            if not settings.OPENAI_API_KEY:
                return await finalize(resposta="A geracao de imagens esta indisponivel no momento.")

            effective_mode = "LOGO" if logo_request else modo
            hint = _mode_hint(effective_mode)
            campaign_copy: Optional[Dict[str, Any]] = None

            if effective_mode in ("FC", "REZETA"):
                campaign_copy = await _generate_campaign_copy(
                    campaign_prompt_source,
                    None,
                    effective_mode,
                )
                prompt = _build_branded_background_prompt(effective_mode, campaign_copy)
            else:
                prompt = _build_image_prompt(None, hint, request.mensagem)
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
                            return await finalize(
                                resposta=resposta_texto,
                                midia=[media],
                                meta={"effective_mode": effective_mode, "fallback": True},
                            )
                        return await finalize(resposta="A imagem foi solicitada, mas a API nao retornou URL.")

                msg = erro.get("message", "Erro desconhecido") if isinstance(erro, dict) else str(erro)
                return await finalize(resposta=f"Erro ao gerar imagem: {msg}")

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
                return await finalize(
                    resposta=resposta_texto,
                    midia=[media],
                    meta={"effective_mode": effective_mode, "fallback": False},
                )
            return await finalize(resposta="A imagem foi solicitada, mas a API nao retornou URL.")

        if not settings.OPENAI_API_KEY:
            messages = viva_local_service.build_messages(request.mensagem, contexto_efetivo)
            resposta = await viva_local_service.chat(messages, modo)
        else:
            messages = _build_viva_concierge_messages(
                mensagem=request.mensagem,
                contexto=contexto_efetivo,
                modo=modo,
            )
            resposta = await viva_model_service.chat(
                messages=messages,
                temperature=0.58,
                max_tokens=700,
            )
            if not resposta or resposta.strip().lower().startswith(("erro", "error")):
                messages_local = viva_local_service.build_messages(request.mensagem, contexto_efetivo)
                resposta = await viva_local_service.chat(messages_local, modo)

        resposta = _sanitize_fake_asset_delivery_reply(resposta, modo)
        resposta = _ensure_fabio_greeting(request.mensagem, resposta)
        return await finalize(resposta=resposta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


@router.get("/chat/snapshot", response_model=ChatSnapshotResponse)
async def get_chat_snapshot(
    session_id: Optional[UUID] = None,
    limit: int = 120,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retorna sessao atual/mais recente com historico de mensagens da VIVA."""
    try:
        await _ensure_chat_tables(db)
        target_session_id = session_id
        if not target_session_id:
            latest = await _get_latest_chat_session_row(db, current_user.id)
            target_session_id = latest.id if latest else None

        if not target_session_id:
            return ChatSnapshotResponse(session_id=None, modo=None, messages=[])

        return await _load_chat_snapshot(
            db=db,
            user_id=current_user.id,
            session_id=target_session_id,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar historico: {str(e)}")


@router.post("/chat/session/new", response_model=ChatSnapshotResponse)
async def create_chat_session(
    payload: ChatSessionStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Inicia nova sessao de chat para limpar contexto sem perder historico anterior."""
    try:
        await _ensure_chat_tables(db)
        session_id = await _create_chat_session(db, current_user.id, payload.modo)
        return ChatSnapshotResponse(session_id=session_id, modo=_normalize_mode(payload.modo), messages=[])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar sessao: {str(e)}")


@router.get("/capabilities", response_model=VivaCapabilitiesResponse)
async def get_capabilities(
    current_user: User = Depends(get_current_user),
):
    """Retorna o catalogo de capacidades operacionais da VIVA."""
    return VivaCapabilitiesResponse(items=viva_capabilities_service.get_capabilities())


@router.post("/handoff/schedule", response_model=HandoffItem)
async def schedule_handoff(
    payload: HandoffScheduleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        task_id = await viva_handoff_service.schedule_task(
            db=db,
            user_id=current_user.id,
            cliente_nome=payload.cliente_nome,
            cliente_numero=payload.cliente_numero,
            mensagem=payload.mensagem,
            scheduled_for=payload.scheduled_for,
            agenda_event_id=payload.agenda_event_id,
            meta=payload.meta or {},
        )
        rows = await db.execute(
            text(
                """
                SELECT id, user_id, agenda_event_id, cliente_nome, cliente_numero, mensagem,
                       scheduled_for, status, attempts, sent_at, last_error, meta_json, created_at, updated_at
                FROM viva_handoff_tasks
                WHERE id = :id AND user_id = :user_id
                """
            ),
            {"id": str(task_id), "user_id": str(current_user.id)},
        )
        row = rows.first()
        if not row:
            raise HTTPException(status_code=500, detail="Falha ao agendar handoff.")
        return _handoff_row_to_item(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao agendar handoff: {str(e)}")


@router.get("/handoff", response_model=HandoffListResponse)
async def list_handoff(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        data = await viva_handoff_service.list_tasks(
            db=db,
            user_id=current_user.id,
            status=status,
            page=max(1, page),
            page_size=max(1, min(page_size, 200)),
        )
        return HandoffListResponse(
            items=[_handoff_row_to_item(row) for row in data["items"]],
            total=int(data["total"]),
            page=int(data["page"]),
            page_size=int(data["page_size"]),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar handoff: {str(e)}")


@router.post("/handoff/process-due", response_model=HandoffProcessResponse)
async def process_handoff_due(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await viva_handoff_service.process_due_tasks(db=db, limit=limit)
        return HandoffProcessResponse(
            processed=int(result["processed"]),
            sent=int(result["sent"]),
            failed=int(result["failed"]),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar handoff: {str(e)}")


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










