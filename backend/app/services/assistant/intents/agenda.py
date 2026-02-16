"""Intent helpers for agenda queries in VIVA domain router.

Used for domain-level confirmation disambiguation and future extraction.
"""

from __future__ import annotations

from app.services.viva_shared_service import _normalize_key


def is_agenda_related_query(message: str) -> bool:
    normalized = _normalize_key(message or "")
    if not normalized:
        return False
    has_agenda = any(token in normalized for token in ("agenda", "compromisso", "compromissos", "agendamento"))
    has_query = any(token in normalized for token in ("listar", "liste", "lista", "quais", "mostrar", "mostra", "tem", "tenho"))
    return has_agenda and has_query
