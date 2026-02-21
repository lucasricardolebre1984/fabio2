"""Runtime helpers for VIVA chat orchestration.

Centraliza utilitarios de handoff/imagem e regras de sanitizacao de resposta.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.viva_shared_service import _extract_subject, _normalize_key, _sanitize_prompt


def _sanitize_idle_confirmations(resposta: str) -> str:
    """Remove confirmacoes "ociosas" que deixam a conversa artificial.

    Regra: nunca dizer "Confirmo que nenhuma acao foi executada" (nao agrega).
    """

    if not resposta:
        return resposta

    # Evita bugs de encoding: filtra por linha usando normalizacao ASCII.
    cleaned_lines: List[str] = []
    for line in str(resposta).splitlines():
        norm = _normalize_key(line)
        if not norm:
            cleaned_lines.append(line)
            continue
        if "confirmo que nenhuma acao foi executada" in norm:
            continue
        if "nao executei nenhuma acao" in norm or "nao realizei nenhuma acao" in norm:
            continue
        cleaned_lines.append(line)
    resposta = "\n".join(cleaned_lines)

    # Se sobrar duplo espaco/linhas, normaliza.
    resposta = re.sub(r"\n{3,}", "\n\n", resposta).strip()
    return resposta


def _sanitize_unsolicited_capability_menu(user_texto: str, resposta: str) -> str:
    """Remove "menus" de capacidades nao solicitados (ex.: 'Posso, por exemplo: ...').

    O usuario quer interacao natural: cumprimentou -> 1 frase + 1 pergunta objetiva,
    sem listar opcoes por default. Se o usuario pedir explicitamente "o que voce pode fazer",
    nao sanitizamos.
    """

    if not resposta:
        return resposta

    user_norm = _normalize_key(user_texto or "")
    if any(
        term in user_norm
        for term in (
            "o que voce pode",
            "oq voce pode",
            "o que vc pode",
            "oq vc pode",
            "como voce pode ajudar",
            "como vc pode ajudar",
            "o que voce faz",
            "oq voce faz",
            "o que vc faz",
            "oq vc faz",
            "quais funcoes",
            "quais tarefas",
            "o que tem ai",
        )
    ):
        return resposta

    # Remove bloco "Posso, por exemplo:" + itens subsequentes.
    # Aceita bullets '-', '*', '•' e enumeracoes simples.
    resposta = re.sub(
        r"(?is)\n*\s*posso\s*(?:,\s*)?(?:por\s*exemplo|ex\.)\s*:?\s*(?:\n\s*(?:[-*]|â€¢|\d+\.)\s+.*)+",
        "",
        resposta,
    )
    # Remove linha "Posso, por exemplo:" isolada.
    resposta = re.sub(
        r"(?im)^\s*posso\s*(?:,\s*)?(?:por\s*exemplo|ex\.)\s*:?\s*$",
        "",
        resposta,
    )

    resposta = re.sub(r"\n{3,}", "\n\n", resposta).strip()
    return resposta


def _sanitize_fake_asset_delivery_reply(resposta: str, modo: Optional[str]) -> str:
    if modo not in ("FC", "REZETA"):
        return resposta

    lower = (resposta or "").lower()
    normalized = _normalize_key(resposta or "")
    has_fake_campaign_delivery = (
        "campanha criada" in normalized
        and any(
            token in normalized
            for token in (
                "formatos gerados",
                "local salvo",
                "campanhas fc",
                "campanhas rezeta",
            )
        )
    )
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
        or has_fake_campaign_delivery
    )
    if not has_fake_signal:
        return resposta

    return (
        "Ainda nao confirmei criacao real da campanha no SaaS por este texto. "
        "Para gerar e salvar de verdade agora, me diga: 'gere a campanha agora'."
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


def _is_viviane_handoff_query_intent(texto: str) -> bool:
    normalized = _normalize_key(texto)
    if not normalized:
        return False
    if "handoff" in normalized:
        return True

    has_viviane = "viviane" in normalized
    handoff_terms = (
        "lembrete",
        "lembretes",
        "pedido",
        "pedidos",
        "aviso",
        "avisos",
        "whatsapp",
        "mensagem",
        "mensagens",
        "fila",
        "tarefas",
    )
    return has_viviane and any(term in normalized for term in handoff_terms)


def _handoff_status_from_text(texto: str) -> Optional[str]:
    normalized = _normalize_key(texto)
    if any(term in normalized for term in ("falhou", "falharam", "erro", "erros")):
        return "failed"
    if any(term in normalized for term in ("enviado", "enviados", "concluido", "concluidos")):
        return "sent"
    if any(term in normalized for term in ("todos", "historico", "historia", "geral")):
        return None
    return "pending"


def _normalize_any_datetime(value: Any) -> Optional[datetime]:
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None
    else:
        return None

    if dt.tzinfo is not None:
        return dt.astimezone().replace(tzinfo=None)
    return dt


def _format_viviane_handoff_list(
    items: List[Dict[str, Any]],
    period_label: str,
    status_filter: Optional[str],
) -> str:
    if not items:
        return f"Nao encontrei pedidos de lembrete para a Viviane {period_label}."

    status_label = {
        "pending": "Pendente",
        "sent": "Enviado",
        "failed": "Falhou",
    }
    if status_filter:
        header = f"Pedidos para a Viviane {period_label} ({status_label.get(status_filter, status_filter)}):"
    else:
        header = f"Pedidos para a Viviane {period_label}:"

    ordered = sorted(
        items,
        key=lambda item: _normalize_any_datetime(item.get("scheduled_for")) or datetime.max,
    )
    lines = [header]
    for item in ordered:
        scheduled_for = _normalize_any_datetime(item.get("scheduled_for"))
        horario = scheduled_for.strftime("%H:%M") if scheduled_for else "--:--"
        status = status_label.get(str(item.get("status") or "").lower(), str(item.get("status") or "Pendente"))
        cliente_nome = str(item.get("cliente_nome") or "").strip()
        cliente_numero = str(item.get("cliente_numero") or "").strip()
        cliente = cliente_nome or cliente_numero or "cliente nao identificado"
        mensagem = str(item.get("mensagem") or "").strip()
        resumo_msg = _sanitize_prompt(mensagem, 90) if mensagem else "sem texto definido"
        lines.append(f"- {horario} | {cliente} ({status}) | {resumo_msg}")
    return "\n".join(lines)


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
    match = re.search(
        r"cliente\s+([A-Za-z\u00C0-\u00FF0-9 ]{2,80})",
        texto or "",
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    raw = re.split(
        r"\b(amanha|amanh\u00e3|hoje|as|\u00e0s|no|na|dia|whatsapp)\b",
        match.group(1),
        flags=re.IGNORECASE,
    )[0]
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
    texto_limpo = (texto or "").replace("\r", "")
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
            payload = texto_limpo[idx + len(marker) :].lstrip(" :\n")
            if payload.strip():
                return payload.strip()

    return texto_limpo.strip()


def _brand_guardrail(modo: str) -> str:
    if modo == "FC":
        return (
            "Marca FC Solucoes Financeiras. Paleta obrigatoria: #071c4a, #00a3ff, #010a1c, #f9feff. "
            "Nao usar verde. Tom corporativo premium."
        )
    return (
        "Marca RezetaBrasil. Paleta obrigatoria: #1E3A5F, #3DAA7F, #2A8B68, #FFFFFF. "
        "Tom humano, confiavel e promocional."
    )


