"""
NLU helpers for VIVA agenda flows.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import re
import unicodedata

from app.models.agenda import EventoTipo


def _normalize_key(texto: str) -> str:
    normalized = unicodedata.normalize("NFKD", (texto or ""))
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", without_accents.lower()).strip()


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
    if "ligar" in text or "ligacao" in text or "ligacao" in text:
        return EventoTipo.LIGACAO
    if "prazo" in text or "vencimento" in text:
        return EventoTipo.PRAZO
    if "reuniao" in text or "reuniao" in text:
        return EventoTipo.REUNIAO
    return EventoTipo.OUTRO


def parse_agenda_command(message: str) -> Optional[Dict[str, Any]]:
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


def _is_agenda_verb(text: str) -> bool:
    normalized = _normalize_key(text)
    return any(
        term in normalized
        for term in (
            "agenda",
            "agendamento",
            "agendamentos",
            "compromisso",
            "compromissos",
            "lembrete",
            "lembra",
            "lembrar",
        )
    )


def _is_simple_confirmation(text: str) -> bool:
    normalized = _normalize_key(text)
    return normalized in {
        "sim",
        "quero",
        "quero sim",
        "ok",
        "pode",
        "sim ja",
        "ja",
        "todos",
        "todos sem mais perguntas",
        "todos sem mais pergintas",
    }


def _has_recent_agenda_prompt(contexto: List[Dict[str, Any]]) -> bool:
    for msg in reversed(contexto[-8:]):
        if msg.get("tipo") != "ia":
            continue
        normalized = _normalize_key(str(msg.get("conteudo") or ""))
        if "agenda" in normalized or "compromiss" in normalized:
            return True
    return False


def is_agenda_query_intent(message: str, contexto: List[Dict[str, Any]]) -> bool:
    normalized = _normalize_key(message)

    create_terms = (
        "agendar",
        "marcar",
        "criar compromisso",
        "novo compromisso",
        "adicionar compromisso",
    )
    conclude_terms = ("concluir", "confirmar compromisso", "finalizar compromisso")

    if any(term in normalized for term in conclude_terms):
        return False
    if any(term in normalized for term in create_terms):
        return False

    query_terms = (
        "minha agenda",
        "como esta minha agenda",
        "como esta a agenda",
        "como esta minha agenda hj",
        "como ta minha agenda",
        "o que tenho",
        "quais compromissos",
        "listar agenda",
        "lista da agenda",
        "agendamentos de hoje",
        "agenda de hoje",
        "compromissos de hoje",
        "agenda hj",
        "agenda hoje",
        "agenda amanha",
    )

    if any(term in normalized for term in query_terms):
        return True

    if _is_agenda_verb(message):
        return True

    if _is_simple_confirmation(message) and _has_recent_agenda_prompt(contexto):
        return True

    return False


def agenda_window_from_text(message: str) -> Tuple[datetime, datetime, str]:
    normalized = _normalize_key(message)
    now = datetime.now()

    if "amanha" in normalized:
        start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return start, end, "de amanha"

    if "semana" in normalized:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
        return start, end, "dos proximos 7 dias"

    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return start, end, "de hoje"


def format_agenda_list(items: List[Any], period_label: str) -> str:
    if not items:
        return f"Voce nao tem compromissos {period_label}."

    ordered = sorted(items, key=lambda item: item.data_inicio)
    lines = [f"Seus compromissos {period_label}:"]
    for item in ordered:
        status = "Concluido" if item.concluido else "Pendente"
        horario = item.data_inicio.strftime("%H:%M")
        lines.append(f"- {horario} | {item.titulo} ({status})")

    return "\n".join(lines)


def parse_agenda_natural_create(message: str) -> Optional[Dict[str, Any]]:
    raw = (message or "").strip()
    if not raw:
        return None

    normalized = _normalize_key(raw)
    if not any(
        term in normalized
        for term in ("agendar", "marcar", "novo compromisso", "criar compromisso", "adicionar compromisso")
    ):
        return None

    if "|" in raw:
        return None

    time_match = re.search(r"\b(\d{1,2}:\d{2})\b", raw)
    if not time_match:
        return {"error": "Data/hora invalida"}

    hour, minute = [int(part) for part in time_match.group(1).split(":")]
    if hour > 23 or minute > 59:
        return {"error": "Data/hora invalida"}

    date_match = re.search(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b", raw)
    date_value: Optional[datetime] = None

    if date_match:
        for fmt in ("%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y"):
            try:
                parsed_date = datetime.strptime(date_match.group(1), fmt)
                date_value = parsed_date
                break
            except ValueError:
                continue
    elif "amanha" in normalized:
        date_value = datetime.now() + timedelta(days=1)
    elif "hoje" in normalized:
        date_value = datetime.now()

    if not date_value:
        return {"error": "Data/hora invalida"}

    date_time = date_value.replace(hour=hour, minute=minute, second=0, microsecond=0)

    title = raw
    title = re.sub(
        r"(?i)\b(agendar|agenda|marcar|marque|novo compromisso|criar compromisso|adicionar compromisso)\b",
        "",
        title,
    )
    title = title.replace(time_match.group(0), "")
    if date_match:
        title = title.replace(date_match.group(1), "")
    title = re.sub(r"(?i)\b(hoje|amanha|amanha|as|as|para|dia)\b", " ", title)
    title = re.sub(r"\s+", " ", title).strip(" -,:;")
    if not title:
        title = "Compromisso"

    return {
        "title": title,
        "date_time": date_time,
        "description": None,
        "tipo": _infer_event_type(title),
    }


def parse_agenda_conclude_command(message: str) -> Optional[Dict[str, Any]]:
    raw = (message or "").strip()
    if not raw:
        return None

    normalized = _normalize_key(raw)
    if not any(term in normalized for term in ("concluir", "confirmar", "finalizar")):
        return None

    uuid_match = re.search(
        r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b",
        raw,
    )
    if not uuid_match:
        text_query = re.sub(
            r"(?i)\b(concluir|confirmar|finalizar|compromisso|evento|agenda)\b",
            " ",
            raw,
        )
        text_query = re.sub(r"\s+", " ", text_query).strip(" -,:;")
        if text_query and len(text_query) >= 3:
            return {"search_text": text_query}
        return {"error": "ID ou titulo obrigatorio"}

    try:
        return {"evento_id": UUID(uuid_match.group(0))}
    except ValueError:
        return {"error": "ID invalido"}


def build_agenda_recovery_reply(message: str, errors: List[str]) -> str:
    normalized = _normalize_key(message)
    lower_errors = [str(err).lower() for err in (errors or [])]
    has_datetime_error = any("data/hora" in err for err in lower_errors)
    has_time_in_text = bool(re.search(r"\b\d{1,2}:\d{2}\b", message or ""))

    if has_datetime_error and not has_time_in_text:
        return (
            "Entendi. Me diga so quando deve acontecer (ex.: amanha 10:30) "
            "e o que voce quer agendar, que eu registro para voce."
        )

    if has_datetime_error:
        return (
            "Quase pronto. Me confirme so a data e horario do compromisso "
            "(pode ser em linguagem natural) que eu finalizo."
        )

    if "concluir" in normalized or "finalizar" in normalized:
        return (
            "Para concluir, me diga o titulo do compromisso ou o ID que aparece na agenda."
        )

    return (
        "Entendi que voce quer mexer na agenda. Me diga apenas o compromisso e quando ele acontece, "
        "do seu jeito, que eu cuido do resto."
    )


class VivaAgendaNluService:
    parse_agenda_command = staticmethod(parse_agenda_command)
    parse_agenda_natural_create = staticmethod(parse_agenda_natural_create)
    parse_agenda_conclude_command = staticmethod(parse_agenda_conclude_command)
    is_agenda_query_intent = staticmethod(is_agenda_query_intent)
    agenda_window_from_text = staticmethod(agenda_window_from_text)
    format_agenda_list = staticmethod(format_agenda_list)
    build_agenda_recovery_reply = staticmethod(build_agenda_recovery_reply)


viva_agenda_nlu_service = VivaAgendaNluService()

