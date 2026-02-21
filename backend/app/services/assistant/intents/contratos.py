"""Intent helpers for contract queries in VIVA domain router."""

from __future__ import annotations

import re
from typing import Optional

from app.services.viva_shared_service import _normalize_key


def is_contract_list_intent(message: str) -> bool:
    normalized = _normalize_key(message or "")
    if not normalized:
        return False
    has_contract = any(token in normalized for token in ("contrato", "contratos"))
    has_list_signal = any(
        token in normalized
        for token in ("listar", "liste", "lista", "quais", "titulos", "todos", "registrados", "executamos", "mostre", "list")
    )
    return has_contract and has_list_signal


def is_contract_templates_intent(message: str) -> bool:
    normalized = _normalize_key(message or "")
    if not normalized:
        return False
    has_contract = ("contrato" in normalized) or ("contratos" in normalized)
    has_template_signal = any(
        token in normalized
        for token in ("executamos", "tipos", "modelos", "modolos", "modolo", "templates", "template", "modelo", "modulo", "modulos")
    )
    return has_contract and has_template_signal


def is_contracts_by_client_intent(message: str) -> bool:
    normalized = _normalize_key(message or "")
    if not normalized:
        return False
    has_contract = "contrato" in normalized or "contratos" in normalized
    has_client = "cliente" in normalized or "para " in normalized or "pro " in normalized
    return has_contract and has_client


def extract_client_name_for_contract_query(message: str) -> Optional[str]:
    raw = str(message or "").strip()
    if not raw:
        return None

    patterns = [
        r"(?:pro|para|pra)\s+(.+)$",
        r"(?:pro|para|do|da|de)\s+cliente\s+(.+)$",
        r"cliente\s+(.+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, raw, flags=re.IGNORECASE)
        if match:
            name = re.sub(r"[\]\[\)\(\.,;:!?]+$", "", match.group(1).strip())
            name = re.sub(r"\s+", " ", name).strip()
            if name and _normalize_key(name) not in {"ele", "ela", "dele", "dela"}:
                return name
    return None
