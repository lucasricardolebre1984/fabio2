"""
NLU helpers for VIVA agenda flows.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from zoneinfo import ZoneInfo

import re
import unicodedata

from app.models.agenda import EventoTipo


BRT_TZ = ZoneInfo("America/Sao_Paulo")


def _now_brt() -> datetime:
    """Retorna datetime aware no fuso de Brasilia para consistencia em toda agenda."""
    return datetime.now(BRT_TZ)


def _to_brt_aware(value: datetime) -> datetime:
    """Normaliza datetime para timezone America/Sao_Paulo."""
    if value.tzinfo is None:
        return value.replace(tzinfo=BRT_TZ)
    return value.astimezone(BRT_TZ)


def _normalize_key(texto: str) -> str:
    normalized = unicodedata.normalize("NFKD", (texto or ""))
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", without_accents.lower()).strip()


def _has_phrase(normalized: str, phrase: str) -> bool:
    haystack = f" {normalized.strip()} "
    needle = f" {phrase.strip()} "
    return needle in haystack


def _has_any_phrase(normalized: str, phrases: Tuple[str, ...]) -> bool:
    return any(_has_phrase(normalized, phrase) for phrase in phrases)


def _has_create_imperative(normalized: str) -> bool:
    imperative_phrases = (
        "agendar",
        "agende",
        "marcar",
        "marca",
        "marque",
        "criar",
        "crie",
        "criar compromisso",
        "crie compromisso",
        "novo compromisso",
        "adicionar compromisso",
        "adicionar um compromisso",
        "adicione compromisso",
        "adicione um compromisso",
        "adiciona compromisso",
        "adiciona um compromisso",
        # Natural variants commonly used by operators.
        "coloque na agenda",
        "coloca na agenda",
        "mande para a agenda",
        "manda para a agenda",
        "me avise",
        "me lembre",
        "me lembra",
    )
    return _has_any_phrase(normalized, imperative_phrases)


def _has_query_existence_intent(normalized: str) -> bool:
    agenda_tokens = ("agenda", "agendamento", "agendamentos", "compromisso", "compromissos", "obrigacao", "obrigacoes")
    has_agenda_token = any(_has_phrase(normalized, token) for token in agenda_tokens)

    # Frases fortes de existencia de agendamento (podem aparecer sem "agenda" explicita).
    strong_agenda_phrases = (
        "eu marquei",
        "se eu marquei",
        "ja marquei",
    )
    if _has_any_phrase(normalized, strong_agenda_phrases):
        return True

    # Frases genericas de confirmacao so valem quando houver contexto de agenda.
    generic_confirmation_phrases = (
        "tem algum",
        "tem alguma",
        "ha algum",
        "ha alguma",
        "existe algum",
        "existe alguma",
        "me confirma",
        "me confirme",
        "confirma se",
        "confirme se",
        "verifica se",
        "verifique se",
        "verifique a agenda",
        "verificar agenda",
        "consulte agenda",
        "consultar agenda",
        "conferir agenda",
        "confere agenda",
    )
    if has_agenda_token and _has_any_phrase(normalized, generic_confirmation_phrases):
        return True

    query_tokens = (
        "tenho",
        "tem",
        "ha",
        "havera",
        "existe",
        "quais",
        "listar",
        "liste",
        "lite",
        "lista",
        "mostrar",
        "mostra",
        "consultar",
    )
    has_query_token = any(_has_phrase(normalized, token) for token in query_tokens)
    return has_agenda_token and has_query_token


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
            return _to_brt_aware(datetime.strptime(value, fmt))
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

    # Permite wake-word no inicio sem quebrar comandos de agenda.
    text = re.sub(r"(?i)^\s*viva\b[:,]?\s*", "", text).strip()
    lower = text.lower()
    if not (
        lower.startswith("agendar")
        or lower.startswith("agende")
        or lower.startswith("agenda")
        or lower.startswith("marcar")
        or lower.startswith("marca")
        or lower.startswith("marque")
        or lower.startswith("adicionar")
        or lower.startswith("adicione")
        or lower.startswith("adiciona")
    ):
        return None

    payload = re.sub(
        r"^(agendar|agende|agenda|marcar|marca|marque|adicionar|adicione|adiciona)\s*:?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
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
    if "compromiss" in normalized or "promisso" in normalized:
        return True
    return any(
        term in normalized
        for term in (
            "agenda",
            "agendamento",
            "agendamentos",
            "compromisso",
            "cpompromisso",
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
    }


def _has_recent_agenda_prompt(contexto: List[Dict[str, Any]]) -> bool:
    for msg in reversed(contexto[-2:]):
        if msg.get("tipo") != "ia":
            continue
        normalized = _normalize_key(str(msg.get("conteudo") or ""))
        has_agenda_token = ("agenda" in normalized) or ("compromiss" in normalized)
        has_question_prompt = any(
            phrase in normalized
            for phrase in (
                "quer que eu liste",
                "deseja que eu liste",
                "posso listar",
                "me confirme se quer",
                "sim ou nao",
                "de hoje ou amanha",
                "quer detalhes",
                "listar os proximos 7 dias",
                "listar os proximos",
            )
        )
        if has_agenda_token and has_question_prompt:
            return True
    return False


def is_agenda_query_intent(message: str, contexto: List[Dict[str, Any]]) -> bool:
    normalized = _normalize_key(message)

    conclude_terms = ("concluir", "confirmar compromisso", "finalizar compromisso")

    if any(term in normalized for term in conclude_terms):
        return False

    # Strong create imperative must win, even if the message also asks for verification.
    if _has_create_imperative(normalized):
        return False

    # Consulta de existencia tem prioridade sobre criacao para evitar falso positivo:
    # "eu marquei algo amanha?" nao deve cair no fluxo de criar compromisso.
    if _has_query_existence_intent(normalized):
        return True

    query_terms = (
        "minha agenda",
        "como esta minha agenda",
        "como esta a agenda",
        "como esta minha agenda hj",
        "como ta minha agenda",
        "o que tem na agenda",
        "o que tem na minha agenda",
        "o que tenho",
        "quais compromissos",
        "listar agenda",
        "liste agenda",
        "lite agenda",
        "lista da agenda",
        "agendamentos de hoje",
        "agenda de hoje",
        "compromissos de hoje",
        "agenda hj",
        "agenda hoje",
        "agenda de ontem",
        "agenda ontem",
        "agenda amanha",
        "verifique a agenda",
        "consultar agenda",
        "consulte agenda",
        "confira agenda",
    )

    if any(term in normalized for term in query_terms):
        return True

    if _is_agenda_verb(message) and any(
        term in normalized
        for term in (
            "quais",
            "listar",
            "list",
            "liste",
            "lite",
            "lista",
            "mostrar",
            "mostra",
            "como esta",
            "como ta",
            "o que tenho",
            "o que tem",
            "o que temos",
            "tenho",
            "temos",
            "consultar",
            "consulta",
            "ver minha",
        )
    ):
        return True

    if _is_simple_confirmation(message) and _has_recent_agenda_prompt(contexto):
        return True

    if _has_recent_agenda_prompt(contexto) and any(
        term in normalized
        for term in ("hoje", "h9je", "amanha", "semana", "7 dias", "proximos", "nada")
    ):
        return True

    return False


def agenda_window_from_text(message: str) -> Tuple[datetime, datetime, str]:
    normalized = _normalize_key(message)
    now = _now_brt()

    explicit_dt_match = re.search(
        r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\D+(\d{1,2}):(\d{2})(?::\d{2})?\b",
        message or "",
    )
    if explicit_dt_match:
        raw_date = explicit_dt_match.group(1)
        hour = int(explicit_dt_match.group(2))
        minute = int(explicit_dt_match.group(3))
        parsed_date: Optional[datetime] = None
        for fmt in ("%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y"):
            try:
                parsed_date = datetime.strptime(raw_date, fmt)
                break
            except ValueError:
                continue
        if parsed_date is not None and 0 <= hour <= 23 and 0 <= minute <= 59:
            start = _to_brt_aware(parsed_date.replace(hour=hour, minute=minute, second=0, microsecond=0))
            end = start + timedelta(minutes=1)
            return start, end, f"em {start.strftime('%d/%m/%Y %H:%M')}"

    explicit_date_match = re.search(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b", message or "")
    if explicit_date_match:
        raw_date = explicit_date_match.group(1)
        parsed_date = None
        for fmt in ("%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y"):
            try:
                parsed_date = datetime.strptime(raw_date, fmt)
                break
            except ValueError:
                continue
        if parsed_date is not None:
            start = _to_brt_aware(parsed_date.replace(hour=0, minute=0, second=0, microsecond=0))
            end = start + timedelta(days=1)
            return start, end, f"de {start.strftime('%d/%m/%Y')}"

    if "ontem" in normalized:
        start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return start, end, "de ontem"

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
        horario = _to_brt_aware(item.data_inicio).strftime("%H:%M")
        lines.append(f"- {horario} | {item.titulo} ({status})")

    return "\n".join(lines)


def parse_agenda_natural_create(message: str) -> Optional[Dict[str, Any]]:
    raw = (message or "").strip()
    if not raw:
        return None

    # Permite wake-word no inicio sem atrapalhar reconhecimento natural.
    raw = re.sub(r"(?i)^\s*viva\b[:,]?\s*", "", raw).strip()
    normalized = _normalize_key(raw)
    if not _has_create_imperative(normalized):
        return None

    # Messages can legitimately combine creation + verification, e.g.:
    # "coloque na agenda ... hoje 18h, verifique se o Google Calendar esta conectado".
    # In that case, we should still create the event and let the orchestrator answer the verification part.
    if _has_query_existence_intent(normalized) and not _has_phrase(normalized, "coloque na agenda") and not _has_phrase(normalized, "coloca na agenda"):
        return None

    if "|" in raw:
        return None

    time_token = ""
    hour = 0
    minute = 0
    relative_delta: Optional[timedelta] = None
    has_tomorrow_hint = bool(re.search(r"\bamanh\w*\b", normalized))
    has_today_hint = bool(re.search(r"\bhoj\w*\b", normalized))

    # Suporta linguagem natural relativa: "daqui duas horas", "daqui 2h", "daqui 30 minutos".
    word_to_number = {
        "um": 1,
        "uma": 1,
        "dois": 2,
        "duas": 2,
        "tres": 3,
        "quatro": 4,
        "cinco": 5,
        "seis": 6,
        "sete": 7,
        "oito": 8,
        "nove": 9,
        "dez": 10,
        "onze": 11,
        "doze": 12,
    }
    relative_match = re.search(
        r"\bdaqui\s+(?:(\d+)|(um|uma|dois|duas|tres|quatro|cinco|seis|sete|oito|nove|dez|onze|doze)|(meia|meio))\s*"
        r"(hora|horas|h|minuto|minutos|min)\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if relative_match:
        amount = 0
        if relative_match.group(1):
            amount = int(relative_match.group(1))
        elif relative_match.group(2):
            amount = int(word_to_number.get(str(relative_match.group(2)).lower(), 0))
        elif relative_match.group(3):
            amount = 30
        unit = str(relative_match.group(4) or "").lower()
        if unit in ("hora", "horas", "h"):
            if relative_match.group(3):
                relative_delta = timedelta(minutes=30)
            elif amount > 0:
                relative_delta = timedelta(hours=amount)
        elif amount > 0:
            relative_delta = timedelta(minutes=amount)

    explicit_time_detected = False
    hh_mm_match = re.search(r"\b(\d{1,2}):(\d{2})\b", raw)
    if hh_mm_match:
        hour = int(hh_mm_match.group(1))
        minute = int(hh_mm_match.group(2))
        time_token = hh_mm_match.group(0)
        explicit_time_detected = True
    else:
        short_hour_match = re.search(r"\b(?:as|a|s)\s*(\d{1,2})(?:h(\d{2})?)?\b", normalized)
        if short_hour_match:
            hour = int(short_hour_match.group(1))
            minute = int(short_hour_match.group(2)) if short_hour_match.group(2) else 0
            time_token = ""
            explicit_time_detected = True
        else:
            compact_hour_match = re.search(r"(?i)\b(\d{1,2})h(\d{2})?\b", raw)
            if compact_hour_match:
                hour = int(compact_hour_match.group(1))
                minute = int(compact_hour_match.group(2)) if compact_hour_match.group(2) else 0
                time_token = compact_hour_match.group(0)
                explicit_time_detected = True
            else:
                fallback_hour_match = re.search(r"\b(\d{1,2})(?:h(\d{2})?)?\b", normalized)
                if fallback_hour_match and (has_tomorrow_hint or has_today_hint):
                    hour = int(fallback_hour_match.group(1))
                    minute = int(fallback_hour_match.group(2)) if fallback_hour_match.group(2) else 0
                    time_token = ""
                    explicit_time_detected = True
                else:
                    if relative_delta is None:
                        return {"error": "Data/hora invalida"}

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
    elif has_tomorrow_hint:
        date_value = _now_brt() + timedelta(days=1)
    elif has_today_hint:
        date_value = _now_brt()

    if relative_delta is not None:
        date_time = _now_brt() + relative_delta
        date_time = date_time.replace(second=0, microsecond=0)
    else:
        # Se o operador informou apenas horario (sem data), assume hoje;
        # caso horario ja tenha passado e nao tenha "hoje", agenda para amanha.
        if date_value is None and explicit_time_detected:
            now_brt = _now_brt()
            candidate = now_brt.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if not has_today_hint and candidate < now_brt:
                date_value = now_brt + timedelta(days=1)
            else:
                date_value = now_brt

        if not date_value:
            return {"error": "Data/hora invalida"}
        date_time = date_value.replace(hour=hour, minute=minute, second=0, microsecond=0)
    date_time = _to_brt_aware(date_time)

    # Trim verification clause from title to keep it clean (ex.: "... verifique se google agenda ...")
    title_source = raw
    if any(token in normalized for token in ("google", "calendar", "calendario")) and any(
        phrase in normalized for phrase in ("verifique", "verifica", "confirme", "confirma", "cheque", "checar", "veja")
    ):
        title_source = re.split(r"(?i)\b(verifique|verifica|confirme|confirma|cheque|checar|veja)\b", raw, maxsplit=1)[0].strip()

    title = title_source
    verb_match = re.search(
        r"(?i)\b(agendar|agende|agenda|marcar|marca|marque|criar|crie|novo compromisso|criar compromisso|crie compromisso|adicionar compromisso|adicionar um compromisso|adicione compromisso|adicione um compromisso|adiciona compromisso|adiciona um compromisso)\b",
        title,
    )
    if verb_match:
        title = title[verb_match.end():].strip()

    title = re.split(
        r"(?i)\b(mande para a agenda|manda para a agenda|coloque na agenda|coloca na agenda|me avise|me lembra|me lembre)\b",
        title,
    )[0].strip()

    if time_token:
        title = title.replace(time_token, "")
    title = re.sub(r"(?i)\b\d{1,2}(?::\d{2})?\b|\b\d{1,2}h\d{0,2}\b", " ", title)
    if date_match:
        title = title.replace(date_match.group(1), "")
    title = re.sub(
        r"(?i)\b(hoje|hoj\w*|amanha|amanhã|amanh\w*|as|às|s|para|pra|dia|de|do|da|no|na|mim|comigo|daqui|hora|horas|minuto|minutos|um|uma|dois|duas|tres|quatro|cinco|seis|sete|oito|nove|dez)\b",
        " ",
        title,
    )
    title = re.sub(r"[^0-9A-Za-zÀ-ÿ\s-]+", " ", title)
    title = re.sub(r"(?i)\b(o|a|os|as|um|uma)\b", " ", title)
    title = re.sub(r"\s+", " ", title).strip(" -,:;.")

    if title.lower().startswith("compromisso "):
        title = title[len("compromisso "):].strip()

    if len(title.split()) > 8:
        title = " ".join(title.split()[:8]).strip()
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
    if not any(term in normalized for term in ("agenda", "compromisso", "evento")):
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
    has_time_in_text = bool(
        re.search(r"\b\d{1,2}:\d{2}\b", message or "")
        or re.search(r"(?i)\b\d{1,2}h(?:\d{2})?\b", message or "")
    )

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

