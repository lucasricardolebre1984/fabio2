"""Domain helpers for VIVA chat orchestration.

Modulo extraido de `viva_core` para reduzir acoplamento da camada de rota.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

import hashlib
import json
import logging
import re

from app.config import settings
from app.services.openai_service import openai_service
from app.services.viva_agent_profile_service import viva_agent_profile_service
from app.services.viva_concierge_service import viva_concierge_service
from app.services.viva_chat_runtime_helpers_service import _extract_overlay_source
from app.services.viva_shared_service import (
    _extract_subject,
    _normalize_key,
    _normalize_mode,
    _sanitize_prompt,
)

logger = logging.getLogger(__name__)

def _is_image_request(texto: str) -> bool:
    """Heuristica para pedido de GERAR imagem.

    Importante: mencionar "imagem" nao significa solicitar geracao. Ex.: "o que foi essa imagem?"
    """

    normalized = _normalize_key(texto or "")
    if not normalized:
        return False

    keywords = (
        "imagem",
        "banner",
        "post",
        "flyer",
        "arte",
        "cartaz",
        "thumbnail",
        "capa",
        "logo",
        "logotipo",
    )
    if not any(k in normalized for k in keywords):
        return False

    # Evita falso positivo quando o usuario esta se referindo a uma imagem ja gerada.
    # Se nao houver verbo de acao, nao tratamos como geracao.
    if any(
        phrase in normalized
        for phrase in (
            "o que foi essa imagem",
            "o que e essa imagem",
            "por que essa imagem",
            "essa imagem",
            "esta imagem",
            "a imagem",
            "aquela imagem",
            "essa arte",
            "esta arte",
        )
    ) and not re.search(r"\b(gera|gerar|cria|criar|fazer|faz|produzir|produz)\b", normalized):
        return False

    # Intencao explicita (gerar/criar/fazer) ou desejo ("quero/preciso") com asset.
    if re.search(r"\b(gera|gerar|cria|criar|fazer|faz|produzir|produz)\b", normalized):
        return True
    if re.search(r"\b(quero|preciso|pode|consegue|manda|envia)\b", normalized):
        # Caso "quero um banner", "preciso de um post", etc.
        return True

    # Frases curtas do tipo "imagem de carnaval", "banner para rezeta".
    if normalized.startswith(("imagem ", "banner ", "post ", "arte ", "flyer ", "cartaz ", "thumbnail ", "capa ")):
        return True

    return False


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


def _has_campaign_signal(texto: str) -> bool:
    normalized = _normalize_key(texto)
    if not normalized:
        return False

    if _is_image_request(texto) or _is_campaign_request(texto) or _is_direct_generation_intent(texto):
        return True

    field_terms = (
        "objetivo",
        "publico",
        "persona",
        "formato",
        "fortato",
        "headline",
        "subheadline",
        "cta",
        "oferta",
        "promocao",
        "promo",
        "desconto",
        "cena",
    )
    return any(term in normalized for term in field_terms)


def _is_greeting(texto: str) -> bool:
    normalized = _normalize_key(texto or "")
    normalized = re.sub(r"^\s*viva\s+", "", normalized).strip()
    termos = ("oi", "ola", "bom dia", "boa tarde", "boa noite")
    return any(normalized.startswith(t) for t in termos)


def _preferred_greeting(texto: str) -> str:
    normalized = _normalize_key(texto or "")
    normalized = re.sub(r"^\s*viva\s+", "", normalized).strip()
    if normalized.startswith("boa noite"):
        return "Boa noite Fabio!"
    if normalized.startswith("boa tarde"):
        return "Boa tarde Fabio!"
    if normalized.startswith("bom dia"):
        return "Bom dia Fabio!"
    return "Ola Fabio!"


def _ensure_fabio_greeting(user_text: str, resposta: str) -> str:
    if not _is_greeting(user_text):
        return resposta

    if "fabio" in resposta.lower():
        return resposta

    greeting = _preferred_greeting(user_text)
    atualizado = re.sub(
        r"^(boa\s+noite|boa\s+tarde|bom\s+dia|ola|oi)[!,.\s-]*",
        f"{greeting} ",
        resposta,
        flags=re.IGNORECASE,
    )

    if atualizado == resposta:
        return f"{greeting} {resposta}"
    return atualizado


def _build_viva_concierge_messages(
    mensagem: str,
    contexto: List[Dict[str, Any]],
    modo: Optional[str],
    memory_context: Optional[str] = None,
) -> List[Dict[str, str]]:
    agent_status = viva_agent_profile_service.get_profile_status()
    persona_sha = str(agent_status.get("persona_sha256") or "")
    persona_sha_short = persona_sha[:12] if persona_sha else "n/a"
    persona_source = str(agent_status.get("persona_file") or "COFRE/persona-skills/viva/AGENT.md")
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": viva_concierge_service.build_system_prompt(modo=modo)},
        {
            "role": "system",
            "content": (
                "Ancora de persona ativa no runtime: "
                f"{persona_source} (sha256:{persona_sha_short}). "
                "Nao usar persona paralela nem inventar regras fora do AGENT canonico."
            ),
        },
    ]
    if memory_context:
        messages.append(
            {
                "role": "system",
                "content": (
                    "Contexto de memoria para continuidade da conversa. "
                    "Use apenas se for relevante e nunca invente fatos.\n"
                    f"{memory_context}"
                ),
            }
        )
    for msg in contexto[-25:]:
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
    }
    return hints.get(modo)


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
    cleaned = re.sub(r"\s+(a|o|e|de|do|da|para|pra|com)$", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip(" ,.;:-")


def _extract_unstructured_theme(texto: str) -> Optional[str]:
    raw = str(texto or "").strip()
    if not raw:
        return None

    # Primeiro, tenta capturar trecho natural apos "campanha de/do/da/para ...".
    campaign_match = re.search(
        r"campanha\s+(?:de|do|da|para)\s+(.{3,140}?)(?=\s+(?:com|objetivo|publico|formato|cta|oferta|promocao|promo|desconto)\b|[,\n|;:.]|$)",
        raw,
        flags=re.IGNORECASE,
    )
    if campaign_match:
        candidate = _clean_extracted_value(str(campaign_match.group(1)))
        if len(candidate.split()) >= 2:
            return candidate

    noise = {
        "vou", "quero", "preciso", "fazer", "criar", "gerar", "campanha", "imagem", "arte",
        "post", "banner", "um", "uma", "de", "do", "da", "para", "pra", "com", "por",
        "objetivo", "publico", "formato", "cta", "oferta", "promocao", "promo", "desconto",
        "marca", "fc", "rezeta", "solucoes", "financeiras", "brasil", "agora", "hoje",
    }
    segments = re.split(r"[|\n;,]+", raw)
    for segment in segments:
        normalized = _normalize_key(segment)
        if not normalized:
            continue
        if any(
            f"{label} " in f"{normalized} "
            for label in ("objetivo", "publico", "formato", "cta", "oferta")
        ):
            continue
        normalized = re.sub(r"\b\d{1,2}\s*%\b.*", "", normalized).strip()
        tokens = [tok for tok in normalized.split() if tok not in noise]
        if len(tokens) >= 2:
            return _clean_extracted_value(" ".join(tokens[:8]))

    return None


def _is_affirmative(texto: str) -> bool:
    normalized = _normalize_key(texto)
    return normalized in {
        "sim",
        "ok",
        "pode",
        "pode sim",
        "confirmo",
        "usar cta padrao",
        "usar cta padrÃƒÂ£o",
        "cta padrao",
        "cta padrÃƒÂ£o",
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


def _is_campaign_reset_intent(texto: str) -> bool:
    normalized = _normalize_key(texto)
    if not normalized:
        return False
    triggers = (
        "reset memoria campanha",
        "resetar memoria campanha",
        "limpar memoria campanha",
        "limpar padrao campanha",
        "reset padrao campanha",
        "reset imagem campanha",
        "limpar historico campanha",
        "zerar historico campanha",
        "reset de campanha",
        "reset campanhas",
        "resetar campanhas",
    )
    return any(trigger in normalized for trigger in triggers)


def _extract_cast_preference(texto: str) -> Optional[str]:
    normalized = _normalize_key(texto)
    if not normalized:
        return None

    if "apenas mulher" in normalized or "somente mulher" in normalized or "so mulher" in normalized:
        return "feminino"
    if "apenas homem" in normalized or "somente homem" in normalized or "so homem" in normalized:
        return "masculino"
    if "duas mulheres" in normalized or "dupla feminina" in normalized:
        return "dupla_feminina"
    if "casal" in normalized or "homem e mulher" in normalized:
        return "casal"
    if "grupo" in normalized or "equipe" in normalized:
        return "grupo"
    if "mulher" in normalized or "feminina" in normalized:
        return "feminino"
    if "homem" in normalized or "masculino" in normalized:
        return "masculino"
    return None


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
    has_signal = _has_campaign_signal(texto)
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

    if has_signal and not inferred.get("tema"):
        theme_match = re.search(
            r"tema(?: da campanha)?(?: e| eh| =)? (.*?)(?= objetivo| publico| formato| cta| oferta| promocao| promo| desconto| headline| subheadline| cena|$)",
            texto or "",
            flags=re.IGNORECASE,
        )
        if theme_match and str(theme_match.group(1) or "").strip():
            inferred["tema"] = _clean_extracted_value(str(theme_match.group(1)))
        else:
            campaign_theme_match = re.search(
                r"campanha\s+(?:de|do|da|para)\s+(.{3,120}?)(?=\s+\d{1,2}\s*%|\s+(?:objetivo|publico|formato|cta|oferta|promocao|promo|desconto|headline|subheadline|cena)\b|[,\n|;:.]|$)",
                texto or "",
                flags=re.IGNORECASE,
            )
            if campaign_theme_match and str(campaign_theme_match.group(1) or "").strip():
                inferred["tema"] = _clean_extracted_value(str(campaign_theme_match.group(1)))
            else:
                inferred_theme = _extract_unstructured_theme(texto)
                if inferred_theme:
                    inferred["tema"] = inferred_theme

    discount_match_raw = re.search(r"(\d{1,2})\s*%", texto or "", flags=re.IGNORECASE)
    discount_match_words = re.search(r"\b(\d{1,2})\s+por cento\b", normalized)
    if discount_match_raw or discount_match_words:
        pct = (
            (discount_match_raw.group(1) if discount_match_raw else None)
            or (discount_match_words.group(1) if discount_match_words else None)
            or ""
        )
        offer_phrase = re.search(
            r"(\d{1,2}\s*%\s*(?:de|em|no|na)?\s*[^,\n|;:.]{2,90}?)(?=\s+(?:objetivo|publico|formato|cta|tema|headline|subheadline|cena)\b|[,\n|;:.]|$)",
            texto or "",
            flags=re.IGNORECASE,
        )
        if offer_phrase and str(offer_phrase.group(1) or "").strip():
            inferred["oferta"] = _clean_extracted_value(str(offer_phrase.group(1)))
        else:
            inferred["oferta"] = f"Desconto de {pct}%"

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
        inferred = _infer_campaign_fields_from_free_text(content) if _has_campaign_signal(content) else {}
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


def _theme_scene_hint(tema: str, objetivo: str, oferta: str) -> str:
    tema_clean = _sanitize_prompt(str(tema or "").strip(), 120)
    objetivo_clean = _sanitize_prompt(str(objetivo or "").strip(), 120)
    oferta_clean = _sanitize_prompt(str(oferta or "").strip(), 120)
    if tema_clean:
        return (
            f"cena autentica e realista alinhada ao tema '{tema_clean}', "
            "com identidade brasileira, sem estereotipo corporativo repetitivo"
        )
    if oferta_clean:
        return (
            f"cena focada na proposta comercial '{oferta_clean}', com narrativa visual humana e objetiva"
        )
    if objetivo_clean:
        return (
            f"cena orientada ao objetivo '{objetivo_clean}', com contexto cotidiano e credibilidade"
        )
    return "cena autentica no contexto brasileiro, sem estereotipo corporativo repetitivo"

def _audience_scene_hint(publico: str) -> str:
    normalized = _normalize_key(publico)
    if "mei" in normalized or "microempreendedor" in normalized:
        return "personagem principal com perfil empreendedor, ambiente comercial real e dinamico"
    if "jovens" in normalized or "18 35" in normalized:
        return "personagens jovens adultos em ambiente urbano cotidiano e natural"
    if "empresarios" in normalized or "gestores" in normalized:
        return "personagens de perfil executivo moderno, sem rigidez de terno obrigatorio"
    return "personagens brasileiros diversos (genero, faixa etaria e etnia) com expressao natural"


def _composition_variant(seed: str) -> str:
    variants = [
        "plano medio horizontal com profundidade de campo suave",
        "close-up emocional com luz natural e fundo desfocado",
        "plano americano em ambiente real com movimento sutil",
        "enquadramento dinamico levemente angular, visual editorial",
        "cena ampla contextual com personagem em acao principal",
        "composicao centrada limpa com elementos de apoio da oferta",
    ]
    idx = abs(sum(ord(ch) for ch in seed)) % len(variants)
    return variants[idx]


def _appearance_variant(seed: str) -> str:
    variants = [
        "roupa casual elegante, sem figurino repetitivo de banco de imagens",
        "visual moderno com textura de tecido e cores da marca em destaque",
        "estilo cotidiano premium, expressao natural e postura espontanea",
        "apresentacao humanizada com detalhes visuais brasileiros contemporaneos",
        "linguagem visual diversa, sem repetir corte de cabelo/rosto de pecas anteriores",
    ]
    return _stable_pick(seed, "appearance", variants)


def _stable_pick(seed: str, salt: str, options: List[str]) -> str:
    if not options:
        return ""
    digest = hashlib.sha256(f"{seed}|{salt}".encode("utf-8", errors="ignore")).hexdigest()
    idx = int(digest[:12], 16) % len(options)
    return options[idx]


def _cast_profile_pool(publico: str) -> List[Dict[str, str]]:
    normalized = _normalize_key(publico)
    if "mei" in normalized or "microempreendedor" in normalized:
        return [
            {"id": "mei_f_01", "prompt": "mulher empreendedora, cerca de 35 anos, pele morena clara, cabelo cacheado preso, avental de trabalho"},
            {"id": "mei_m_01", "prompt": "homem empreendedor, cerca de 40 anos, pele parda, camisa casual, organizando caixa e estoque"},
            {"id": "mei_dupla_01", "prompt": "dupla de socios, homem e mulher, perfis brasileiros diversos, em rotina real de pequeno negocio"},
            {"id": "mei_f_02", "prompt": "mulher madura empreendedora, cerca de 50 anos, postura confiante, atendimento no balcao"},
            {"id": "mei_m_02", "prompt": "homem jovem empreendedor, cerca de 28 anos, estilo casual, usando celular e caderno de pedidos"},
            {"id": "mei_dupla_02", "prompt": "duas mulheres socias, perfis diferentes, ambiente de loja com movimento"},
        ]
    if "empresario" in normalized or "gestor" in normalized or "pj" in normalized:
        return [
            {"id": "pj_f_01", "prompt": "gestora executiva, cerca de 38 anos, blazer azul, liderando reuniao com equipe diversa"},
            {"id": "pj_m_01", "prompt": "gestor comercial, cerca de 45 anos, camisa social sem gravata, analisando indicadores"},
            {"id": "pj_dupla_01", "prompt": "casal de socios em decisao estrategica, aparencia brasileira contemporanea"},
            {"id": "pj_f_02", "prompt": "lider feminina negra, cerca de 42 anos, ambiente corporativo moderno com quadro de planejamento"},
            {"id": "pj_m_02", "prompt": "lider masculino pardo, cerca de 33 anos, postura colaborativa com time ao fundo"},
            {"id": "pj_grupo_01", "prompt": "grupo executivo diverso em ambiente moderno, foco em colaboracao e resultado"},
        ]
    return [
        {"id": "pf_f_01", "prompt": "mulher jovem adulta, cerca de 29 anos, cabelo castanho curto, visual casual, revisando contas"},
        {"id": "pf_m_01", "prompt": "homem adulto, cerca de 34 anos, pele negra, camiseta clara, atitude de recomeco financeiro"},
        {"id": "pf_f_02", "prompt": "mulher madura, cerca de 47 anos, cabelo ondulado, expressao de alivio e confianca"},
        {"id": "pf_casal_01", "prompt": "casal brasileiro de faixa etaria entre 30 e 40 anos, planejando vida financeira"},
        {"id": "pf_grupo_01", "prompt": "grupo de tres pessoas brasileiras diversas em consultoria financeira humanizada"},
        {"id": "pf_f_03", "prompt": "mulher negra, cerca de 31 anos, sorriso discreto, comemorando conquista de credito"},
        {"id": "pf_m_02", "prompt": "homem pardo, cerca de 41 anos, postura serena, organizando documentos e celular"},
        {"id": "pf_f_04", "prompt": "mulher de perfil nordestino, cerca de 36 anos, ambiente domestico acolhedor, atitude otimista"},
    ]


def _select_cast_profile(
    seed: str,
    publico: str,
    recent_cast_ids: Optional[List[str]] = None,
    cast_preference: Optional[str] = None,
) -> Dict[str, str]:
    pool = _cast_profile_pool(publico)
    if not pool:
        return {"id": "default_cast", "prompt": "pessoa brasileira diversa em contexto financeiro real"}

    preference = str(cast_preference or "").strip().lower()
    if preference:
        preferred_pool: List[Dict[str, str]] = []
        for profile in pool:
            raw = f"{profile.get('id') or ''} {profile.get('prompt') or ''}"
            normalized = _normalize_key(raw)
            if preference == "feminino" and (
                "mulher" in normalized or "feminina" in normalized or "gestora" in normalized
            ):
                preferred_pool.append(profile)
            elif preference == "masculino" and (
                "homem" in normalized or "masculino" in normalized or "gestor" in normalized
            ):
                preferred_pool.append(profile)
            elif preference == "casal" and (
                "casal" in normalized or "homem e mulher" in normalized
            ):
                preferred_pool.append(profile)
            elif preference == "dupla_feminina" and (
                "duas mulheres" in normalized or "socias" in normalized or "dupla feminina" in normalized
            ):
                preferred_pool.append(profile)
            elif preference == "grupo" and (
                "grupo" in normalized or "equipe" in normalized
            ):
                preferred_pool.append(profile)
        if preferred_pool:
            pool = preferred_pool

    recent_order = [str(item).strip() for item in (recent_cast_ids or []) if str(item).strip()]
    recent = set(recent_order)
    fresh_pool = [profile for profile in pool if str(profile.get("id") or "") not in recent]
    if fresh_pool:
        candidates = fresh_pool
    else:
        cooldown = set(recent_order[:2])
        cooled_pool = [profile for profile in pool if str(profile.get("id") or "") not in cooldown]
        candidates = cooled_pool or pool

    ids = [str(item.get("id") or "") for item in candidates]
    selected_id = _stable_pick(seed, "cast_profile", ids)
    for profile in candidates:
        if str(profile.get("id") or "") == selected_id:
            return profile
    return candidates[0]


def _scene_profile_pool(publico: str) -> List[Dict[str, str]]:
    normalized = _normalize_key(publico)
    if "mei" in normalized or "microempreendedor" in normalized:
        return [
            {"id": "scene_mei_balcao", "prompt": "cena em balcao de pequeno comercio com atendimento real e fluxo de clientes"},
            {"id": "scene_mei_estoque", "prompt": "cena de organizacao de estoque e controle financeiro de loja de bairro"},
            {"id": "scene_mei_servico", "prompt": "cena de prestador de servicos em atividade com materiais de trabalho reais"},
            {"id": "scene_mei_parceria", "prompt": "cena de socios discutindo estrategia de crescimento em negocio local"},
            {"id": "scene_mei_delivery", "prompt": "cena de pequena operacao de delivery com controle de pedidos e caixa"},
            {"id": "scene_mei_feira", "prompt": "cena de empreendedor em ponto de venda popular com atendimento humano"},
            {"id": "scene_mei_contabilidade", "prompt": "cena de revisao de contas e pagamentos em escritorio simples de microempresa"},
            {"id": "scene_mei_consultoria", "prompt": "cena de microempreendedor recebendo orientacao financeira pratica"},
        ]
    if "empresario" in normalized or "gestor" in normalized or "pj" in normalized:
        return [
            {"id": "scene_pj_reuniao", "prompt": "cena de reuniao executiva com equipe diversa e decisao de negocio"},
            {"id": "scene_pj_planejamento", "prompt": "cena de planejamento estrategico com indicadores e quadro de metas"},
            {"id": "scene_pj_negociacao", "prompt": "cena de negociacao comercial em ambiente corporativo moderno"},
            {"id": "scene_pj_colaboracao", "prompt": "cena de colaboracao entre liderancas em espaco de negocios contemporaneo"},
            {"id": "scene_pj_operacao", "prompt": "cena de lider acompanhando operacao de equipe em ambiente empresarial ativo"},
            {"id": "scene_pj_financeiro", "prompt": "cena de tomada de decisao financeira com documentos e dashboard real"},
            {"id": "scene_pj_parceria", "prompt": "cena de handshake comercial em ambiente profissional sem estereotipo rigido"},
            {"id": "scene_pj_salao", "prompt": "cena de encontro de socios em espaco de coworking com foco em expansao"},
        ]
    return [
        {"id": "scene_pf_residencial", "prompt": "cena residencial brasileira organizada com foco em reorganizacao financeira"},
        {"id": "scene_pf_consultoria", "prompt": "cena de atendimento de consultoria financeira humanizada com relacao de confianca"},
        {"id": "scene_pf_comercio", "prompt": "cena de rotina urbana com pequenos gastos e planejamento de pagamento"},
        {"id": "scene_pf_recomeco", "prompt": "cena de recomeÃ§o financeiro com expressao de alivio e objetivo claro"},
        {"id": "scene_pf_familia", "prompt": "cena familiar planejando objetivos financeiros e retomada de credito"},
        {"id": "scene_pf_autonomo", "prompt": "cena de trabalhador autonomo organizando contas e cobrancas no celular"},
        {"id": "scene_pf_bairro", "prompt": "cena em comercio de bairro com cliente resolvendo pendencias financeiras"},
        {"id": "scene_pf_planejamento", "prompt": "cena de pessoa montando planejamento mensal com caderno e app financeiro"},
    ]


def _select_scene_profile(seed: str, publico: str, recent_scene_ids: Optional[List[str]] = None) -> Dict[str, str]:
    pool = _scene_profile_pool(publico)
    if not pool:
        return {"id": "scene_default", "prompt": "cena financeira brasileira autentica e humana"}

    recent_order = [str(item).strip() for item in (recent_scene_ids or []) if str(item).strip()]
    recent = set(recent_order)
    fresh_pool = [profile for profile in pool if str(profile.get("id") or "") not in recent]
    if fresh_pool:
        candidates = fresh_pool
    else:
        cooldown = set(recent_order[:2])
        cooled_pool = [profile for profile in pool if str(profile.get("id") or "") not in cooldown]
        candidates = cooled_pool or pool

    ids = [str(item.get("id") or "") for item in candidates]
    selected_id = _stable_pick(seed, "scene_profile", ids)
    for profile in candidates:
        if str(profile.get("id") or "") == selected_id:
            return profile
    return candidates[0]


def _persona_scene_variant(seed: str, publico: str, cast_preference: Optional[str] = None) -> str:
    normalized = _normalize_key(publico)
    if "mei" in normalized or "microempreendedor" in normalized:
        personas = [
            "mulher empreendedora de bairro gerindo caixa e atendimento",
            "homem empreendedor local organizando estoque e financeiro",
            "dupla de socios de pequeno negocio em rotina real",
            "empreendedora madura com foco em reestruturacao do negocio",
        ]
        ambientes = [
            "pequeno comercio brasileiro em horario de atendimento",
            "loja de rua com movimento moderado",
            "balcao de servicos com materiais de trabalho reais",
            "ambiente de oficina ou atelie com atividade em andamento",
        ]
    elif "empresario" in normalized or "gestor" in normalized or "pj" in normalized:
        personas = [
            "gestora de empresa em reuniao objetiva com equipe diversa",
            "gestor comercial analisando indicadores com apoio de time",
            "casal de socios em decisao estrategica no escritorio moderno",
            "lider executivo com equipe multidisciplinar em ambiente corporativo contemporaneo",
        ]
        ambientes = [
            "sala de reuniao com luz natural e clima colaborativo",
            "espaco corporativo moderno sem estereotipo rigido",
            "ambiente profissional com quadro de planejamento e time em acao",
            "hub de negocios com atmosfera dinamica e realista",
        ]
    else:
        personas = [
            "mulher jovem adulta confiante revisando contas e metas pessoais",
            "homem adulto em recomeÃƒÂ§o financeiro com postura otimista",
            "casal brasileiro planejando organizacao financeira da familia",
            "pessoa negra em destaque celebrando conquista de credito",
            "mulher madura com documentos organizados e expressao de alivio",
            "grupo diverso de pessoas em orientacao financeira pratica",
        ]
        ambientes = [
            "ambiente residencial brasileiro organizado e acolhedor",
            "mesa de atendimento com consultoria financeira humanizada",
            "espaco urbano cotidiano com elementos financeiros discretos",
            "ambiente comercial neutro com foco em atendimento humano",
            "cenario de rotina real com documentos e celular em uso",
        ]

    # Forca coerencia com preferencia explicita do usuario quando fornecida.
    pref = _normalize_key(str(cast_preference or ""))
    if pref:
        if pref in {"feminino", "dupla feminina"}:
            filtered = [p for p in personas if "mulher" in _normalize_key(p) or "lider feminina" in _normalize_key(p)]
            personas = filtered or personas
        elif pref == "masculino":
            filtered = []
            for p in personas:
                key = _normalize_key(p)
                if "mulher" in key or "feminina" in key:
                    continue
                if "homem" in key or "gestor" in key or "empreendedor" in key or "lider" in key:
                    filtered.append(p)
            personas = filtered or personas
        elif pref == "casal":
            filtered = [p for p in personas if "casal" in _normalize_key(p) or "homem e mulher" in _normalize_key(p)]
            personas = filtered or personas
        elif pref == "grupo":
            filtered = [p for p in personas if "grupo" in _normalize_key(p) or "equipe" in _normalize_key(p)]
            personas = filtered or personas

    acoes = [
        "interagindo com documentos e celular de forma natural",
        "conversando com consultor em postura colaborativa",
        "celebrando resultado financeiro com linguagem corporal autentica",
        "planejando proximo passo com foco e tranquilidade",
    ]

    persona = _stable_pick(seed, "persona", personas)
    ambiente = _stable_pick(seed, "ambiente", ambientes)
    acao = _stable_pick(seed, "acao", acoes)
    return f"{persona}; {ambiente}; {acao}"


def _resolve_image_size_from_format(formato: str) -> str:
    normalized = _normalize_formato_value(formato or "4:5")
    if normalized in ("4:5", "9:16"):
        return "1024x1536"
    if normalized == "16:9":
        return "1536x1024"
    return "1024x1024"


def _build_scene_seed(fields: Dict[str, str], modo: str, variation_id: str = "") -> str:
    tema = str(fields.get("tema") or "").strip()
    objetivo = str(fields.get("objetivo") or "gerar leads").strip()
    publico = str(fields.get("publico") or "publico geral").strip()
    oferta = str(fields.get("oferta") or "").strip()

    if modo == "FC":
        brand_style = "estetica FC com azul e branco (#071c4a, #00a3ff, #f9feff)"
    else:
        brand_style = "estetica Rezeta com verde e azul (#3DAA7F, #1E3A5F)"

    theme_hint = _theme_scene_hint(tema, objetivo, oferta)
    audience_hint = _audience_scene_hint(publico)
    salt = str(variation_id or "").strip()
    seed = f"{modo}|{tema}|{objetivo}|{publico}|{oferta}|{salt}" if salt else f"{modo}|{tema}|{objetivo}|{publico}|{oferta}"
    persona_variant = _persona_scene_variant(seed, publico)
    composition_variant = _composition_variant(seed)
    scene_parts: List[str] = [
        f"cena publicitaria realista com {brand_style}",
        f"foco em {objetivo}",
        f"publico {publico}",
    ]

    if tema:
        scene_parts.append(f"tema central obrigatorio {tema}")
    if oferta:
        scene_parts.append(f"mensagem visual de oferta {oferta}")
    scene_parts.append(f"direcao visual {theme_hint}")
    scene_parts.append(f"perfil humano {audience_hint}")
    scene_parts.append(f"elenco sugerido {persona_variant}")
    scene_parts.append(f"enquadramento sugerido {composition_variant}")

    merged = " | ".join(scene_parts)
    low = _normalize_key(merged)
    if "escritorio" not in low and "terno" not in low and "corporativo" not in low:
        merged += " | evitar homem de terno e escritorio como padrao visual"
    return _sanitize_prompt(merged, 420)


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


def _fallback_copy(texto: str, modo: Optional[str]) -> Dict[str, Any]:
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
    if modo == "REZETA":
        default_cta = "CHAMAR NO WHATSAPP"
    elif modo == "FC":
        default_cta = "VER COMO FUNCIONA"
    else:
        default_cta = "SAIBA MAIS"
    cta = str(fields.get("cta") or "").strip() or default_cta

    default_bullets = [
        "Diagnostico rapido e objetivo",
        "Plano de acao adaptado ao seu perfil",
        "Acompanhamento claro do inicio ao fim",
    ]
    if offer:
        default_bullets[0] = offer

    scene = str(fields.get("cena") or "").strip() or _build_scene_seed(fields, modo)
    quote = next((ln for ln in lines if ln.startswith('"')), "")
    cast_preference = _extract_cast_preference(texto)

    return {
        "brand": modo,
        "formato": _normalize_formato_value(str(fields.get("formato") or "4:5")),
        "tema": _sanitize_prompt(str(fields.get("tema") or ""), 120),
        "publico": _sanitize_prompt(str(fields.get("publico") or "Publico geral (PF)"), 120),
        "objetivo": _sanitize_prompt(str(fields.get("objetivo") or "Geracao de leads"), 120),
        "oferta": _sanitize_prompt(str(fields.get("oferta") or ""), 120),
        "headline": _sanitize_prompt(headline, 90),
        "subheadline": _sanitize_prompt(subheadline, 130),
        "bullets": [_sanitize_prompt(item, 80) for item in (bullet_lines[:5] or default_bullets)],
        "quote": _sanitize_prompt(quote, 120) if quote else "",
        "cta": _sanitize_prompt(cta, 40),
        "scene": _sanitize_prompt(scene, 420),
        "cast_user_preference": cast_preference or "",
    }


async def _generate_campaign_copy(
    mensagem: str,
    prompt_extra_image: Optional[str],
    modo: Optional[str],
    variation_id: str = "",
) -> Dict[str, Any]:
    fonte = _sanitize_prompt(_extract_overlay_source(mensagem), 5000)
    baseline = _fallback_copy(fonte, modo)

    explicit = _extract_campaign_brief_fields(fonte)
    inferred = _infer_campaign_fields_from_free_text(fonte)
    fields = _apply_campaign_defaults({**explicit, **inferred})
    scene_seed = _build_scene_seed(fields, modo, variation_id=variation_id)
    human_seed = _persona_scene_variant(f"{modo}|{fonte}", str(fields.get("publico") or ""))
    cast_preference = _extract_cast_preference(fonte)
    campaign_skill_prompt = viva_agent_profile_service.get_campaign_skill_prompt(max_chars=2200)

    if modo == "REZETA":
        guardrail = (
            "Marca RezetaBrasil. Paleta obrigatoria: #1E3A5F, #3DAA7F, #2A8B68, #FFFFFF. "
            "Tom humano e acessivel."
        )
    elif modo == "FC":
        guardrail = (
            "Marca FC Solucoes Financeiras. Paleta obrigatoria: #071c4a, #00a3ff, #010a1c, #f9feff. "
            "Tom premium e consultivo."
        )
    else:
        guardrail = (
            "Campanha neutra (sem marca fixa). "
            "Use tom claro, direto e objetivo, alinhado ao pedido atual do usuario."
        )

    system = (
        f"{guardrail}\n"
        "Use a skill oficial abaixo como regra de execucao.\n"
        f"{campaign_skill_prompt}\n"
        "Responda apenas JSON valido e siga o brief atual. "
        "Nao imponha padrao fixo de personagem/cenario; a prioridade e o pedido atual do usuario."
    )

    brand_reference = _sanitize_prompt(prompt_extra_image or "", 1800)
    user = (
        "Brief da campanha:\n"
        f"{fonte}\n\n"
        f"Campos inferidos: objetivo={fields.get('objetivo')}; publico={fields.get('publico')}; "
        f"formato={fields.get('formato')}; tema={fields.get('tema')}; oferta={fields.get('oferta')}; cta={fields.get('cta')}.\n"
        f"Seed de cena: {scene_seed}\n"
        f"Seed humana obrigatoria: {human_seed}\n"
        f"Referencia de marca: {brand_reference or 'nao informada'}\n\n"
        "Retorne JSON com chaves exatas:\n"
        "headline, subheadline, bullets (array 3-5), quote, cta, scene.\n"
        "scene deve refletir o tema/oferta do brief sem texto na imagem."
    )
    if cast_preference:
        user += f"\nPreferencia obrigatoria de personagem: {cast_preference}."

    try:
        resposta = await openai_service.chat(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.6,
            max_tokens=800,
        )
    except Exception as exc:
        logger.warning("viva_campaign_copy_fallback_exception: %s", repr(exc))
        return baseline

    if str(resposta or "").strip().lower().startswith("erro openai chat:"):
        logger.warning("viva_campaign_copy_fallback_model_error: %s", str(resposta)[:280])
        return baseline

    parsed = _extract_json_block(resposta)
    if not parsed:
        return baseline

    bullets = parsed.get("bullets") if isinstance(parsed.get("bullets"), list) else []
    bullets = [str(item).strip() for item in bullets if str(item).strip()][:5]

    return {
        "brand": modo,
        "formato": _normalize_formato_value(str(fields.get("formato") or baseline.get("formato") or "4:5")),
        "tema": _sanitize_prompt(str(fields.get("tema") or baseline.get("tema") or ""), 120),
        "publico": _sanitize_prompt(str(fields.get("publico") or baseline.get("publico") or "Publico geral (PF)"), 120),
        "objetivo": _sanitize_prompt(str(fields.get("objetivo") or baseline.get("objetivo") or "Geracao de leads"), 120),
        "oferta": _sanitize_prompt(str(fields.get("oferta") or baseline.get("oferta") or ""), 120),
        "headline": _sanitize_prompt(str(parsed.get("headline") or baseline["headline"]), 90),
        "subheadline": _sanitize_prompt(str(parsed.get("subheadline") or baseline["subheadline"]), 130),
        "bullets": bullets or baseline["bullets"],
        "quote": _sanitize_prompt(str(parsed.get("quote") or baseline.get("quote") or ""), 120),
        "cta": _sanitize_prompt(str(parsed.get("cta") or baseline["cta"]), 40),
        "scene": _sanitize_prompt(str(parsed.get("scene") or baseline["scene"]), 420),
        "cast_user_preference": cast_preference or str(baseline.get("cast_user_preference") or ""),
    }


def _build_branded_background_prompt(modo: str, campaign_copy: Dict[str, Any], variation_id: str) -> str:
    scene = _sanitize_prompt(str(campaign_copy.get("scene") or ""), 420)
    tema = _sanitize_prompt(str(campaign_copy.get("tema") or ""), 120)
    publico = _sanitize_prompt(str(campaign_copy.get("publico") or ""), 120)
    oferta = _sanitize_prompt(str(campaign_copy.get("oferta") or ""), 120)
    formato = _normalize_formato_value(str(campaign_copy.get("formato") or "4:5"))
    objective = _sanitize_prompt(str(campaign_copy.get("objetivo") or ""), 120)

    theme_hint = _theme_scene_hint(tema, objective, oferta)
    audience_hint = _audience_scene_hint(publico)
    visual_seed = f"{variation_id}|{tema}|{publico}|{oferta}|{scene}"
    visual_variant = _composition_variant(visual_seed)
    cast_preference = _sanitize_prompt(str(campaign_copy.get("cast_user_preference") or "").strip(), 160).lower()
    persona_variant = _persona_scene_variant(visual_seed, publico, cast_preference=cast_preference)
    appearance_variant = _appearance_variant(visual_seed)
    mood_variant = _stable_pick(
        visual_seed,
        "mood",
        [
            "clima de conquista e alivio",
            "energia de recomeÃƒÂ§o com confianca",
            "postura colaborativa e orientada a resultado",
            "tom humano acolhedor com credibilidade",
        ],
    )
    normalized_scene = _normalize_key(scene)
    # Nao usar perfis persistidos (cast/scene profiles) para nao herdar padrao visual antigo.
    # A variacao deve ser guiada pelo brief + seeds deterministicas por campaign.
    cast_guardrail = ""
    if cast_preference in {"feminino", "dupla_feminina", "dupla feminina"}:
        cast_guardrail = "Personagem principal obrigatoriamente mulher; nao usar homem como protagonista. "
    elif cast_preference == "masculino":
        cast_guardrail = "Personagem principal obrigatoriamente homem. "
    elif cast_preference == "casal":
        cast_guardrail = "Composicao obrigatoria com homem e mulher em destaque conjunto. "
    elif cast_preference == "grupo":
        cast_guardrail = "Composicao obrigatoria de grupo diverso em colaboracao. "
    anti_repeat_history = ""
    anti_repeat_scene_history = ""
    avoid_corporate_stereotype = (
        " Evitar estereotipo de homem de terno em escritorio, salvo se a cena pedir explicitamente."
        if ("terno" not in normalized_scene and "escritorio" not in normalized_scene)
        else ""
    )
    anti_repeat_stereotype = (
        "Evite repetir composicoes genericas de banco de imagem (homem sorrindo sozinho em notebook, "
        "pessoa segurando dinheiro na mao, retrato corporativo padrao sem relacao com o tema). "
    )
    theme_anchor = (
        f"Tema central obrigatorio: {tema}. " if tema else "Tema central obrigatorio: contexto humano de reorganizacao financeira. "
    )
    offer_anchor = (
        f"Oferta/gancho visual obrigatorio: {oferta}. " if oferta else ""
    )
    scene_anchor = (
        f"Cena principal obrigatoria: {scene}. " if scene else ""
    )
    if modo == "FC":
        return (
            "Fotografia publicitaria realista para campanha financeira no Brasil. "
            "Identidade FC: azul e branco (#071c4a, #00a3ff, #010a1c, #f9feff). "
            f"Formato final: {formato}. "
            "Distribuicao de cor: azul/branco dominante, evitando verde como cor principal. "
            "Sem texto, sem letras, sem logotipo. "
            "Nao repetir personagem de geracoes anteriores; crie rosto, cabelo, faixa etaria e composicao novos nesta imagem. "
            f"{cast_guardrail}{anti_repeat_history}{anti_repeat_scene_history}"
            f"{anti_repeat_stereotype}"
            f"{avoid_corporate_stereotype} "
            f"{theme_anchor}{offer_anchor}{scene_anchor}"
            f"Direcao de tema: {theme_hint}. Perfil do publico: {audience_hint}. "
            f"Diretriz de elenco: {persona_variant}. Aparencia obrigatoria: {appearance_variant}. "
            f"Variacao de enquadramento: {visual_variant}. "
            f"Humor visual: {mood_variant}. "
            f"Codigo de variacao: {variation_id}"
        )
    return (
        "Fotografia publicitaria realista para campanha financeira no Brasil. "
        "Identidade Rezeta: verde e azul (#3DAA7F, #1E3A5F, #2A8B68, #FFFFFF). "
        f"Formato final: {formato}. "
        "Distribuicao de cor: verde/azul dominante, com contraste limpo e humano. "
        "Sem texto, sem letras, sem logotipo. "
        "Nao repetir personagem de geracoes anteriores; crie rosto, cabelo, faixa etaria e composicao novos nesta imagem. "
        f"{cast_guardrail}{anti_repeat_history}{anti_repeat_scene_history}"
        f"{anti_repeat_stereotype}"
        f"{avoid_corporate_stereotype} "
        f"{theme_anchor}{offer_anchor}{scene_anchor}"
        f"Direcao de tema: {theme_hint}. Perfil do publico: {audience_hint}. "
        f"Diretriz de elenco: {persona_variant}. Aparencia obrigatoria: {appearance_variant}. "
        f"Variacao de enquadramento: {visual_variant}. "
        f"Humor visual: {mood_variant}. "
        f"Codigo de variacao: {variation_id}"
    )


def _build_branded_background_prompt_compact(modo: str, campaign_copy: Dict[str, Any], variation_id: str) -> str:
    tema = _sanitize_prompt(str(campaign_copy.get("tema") or ""), 100)
    oferta = _sanitize_prompt(str(campaign_copy.get("oferta") or ""), 100)
    publico = _sanitize_prompt(str(campaign_copy.get("publico") or ""), 100)
    scene = _sanitize_prompt(str(campaign_copy.get("scene") or ""), 180)
    formato = _normalize_formato_value(str(campaign_copy.get("formato") or "4:5"))
    cast_preference = _sanitize_prompt(str(campaign_copy.get("cast_user_preference") or "").strip(), 80).lower()

    # Nao usar perfis persistidos para evitar heranca de padrao visual antigo.
    cast_profile_prompt = ""
    scene_profile_prompt = ""

    if cast_preference in {"feminino", "dupla_feminina"}:
        cast_guardrail = "Personagem principal obrigatoriamente mulher; nao usar homem como protagonista."
    elif cast_preference == "masculino":
        cast_guardrail = "Personagem principal obrigatoriamente homem."
    elif cast_preference == "casal":
        cast_guardrail = "Composicao obrigatoria com homem e mulher em destaque conjunto."
    elif cast_preference == "grupo":
        cast_guardrail = "Composicao obrigatoria de grupo diverso em colaboracao."
    else:
        cast_guardrail = "Elenco humano brasileiro diverso e autentico, sem estereotipo de banco de imagem."

    brand_block = (
        "Paleta FC (azul e branco: #071c4a, #00a3ff, #010a1c, #f9feff)."
        if modo == "FC"
        else "Paleta Rezeta (verde e azul: #3DAA7F, #1E3A5F, #2A8B68, #FFFFFF)."
    )
    return (
        "Fotografia publicitaria realista no Brasil, sem texto e sem logotipo. "
        f"Formato {formato}. {brand_block} "
        f"Tema: {tema or 'reorganizacao financeira humana'}. Oferta: {oferta or 'consultoria financeira'}. "
        f"Publico: {publico or 'publico geral'}. "
        f"Cena obrigatoria: {scene or 'atendimento financeiro humanizado em contexto real'}. "
        "Elenco obrigatorio: pessoa brasileira em contexto financeiro real. "
        f"{cast_guardrail} "
        "Nao repetir personagem padrao masculino de escritorio; variar rosto, cabelo, idade e enquadramento. "
        f"Variacao: {variation_id}."
    )


BACKGROUND_ONLY_SUFFIX = "Apenas fundo fotografico. Nao inclua palavras, letras ou logotipos."


# ============================================`r`n# CHAT`r`n# ============================================

