"""Intent helpers for client queries in VIVA domain router."""

from __future__ import annotations

import re
from typing import Optional

from app.services.viva_shared_service import _normalize_key


def is_client_list_intent(message: str) -> bool:
    normalized = _normalize_key(message or "")
    if not normalized:
        return False
    has_client = ("cliente" in normalized) or ("clientes" in normalized)
    has_list_signal = any(
        token in normalized
        for token in (
            "listar",
            "liste",
            "lista",
            "quais",
            "todos",
            "registrados",
            "cadastrado",
            "cadastrados",
            "base",
            "mostre",
            "lite",
            "list",
            "cadastro",
        )
    )
    return has_client and has_list_signal


def is_client_detail_intent(message: str) -> bool:
    normalized = _normalize_key(message or "")
    if not normalized:
        return False

    has_client_ref = any(
        token in normalized
        for token in ("cliente", "cadastro", "dados do cliente", "ficha do cliente", "entre no cadastro", "abrir cadastro")
    )
    has_open_or_detail = any(
        token in normalized
        for token in (
            "abrir",
            "abre",
            "abrir",
            "entre no cadastro",
            "entrar no cadastro",
            "entre no",
            "dados",
            "detalhe",
            "detalhes",
            "ficha",
            "mostrar",
            "mostra",
            "ver",
        )
    )
    return has_client_ref and has_open_or_detail


def is_client_profile_contracts_intent(message: str) -> bool:
    normalized = _normalize_key(message or "")
    if not normalized:
        return False

    has_contract = any(token in normalized for token in ("contrato", "contratos"))
    has_profile = any(
        token in normalized
        for token in (
            "cadastro",
            "ficha",
            "dados",
            "resumo",
            "o que ele tem",
            "tem de contrato",
        )
    )
    return has_contract and has_profile


def extract_client_name_for_detail_query(message: str) -> Optional[str]:
    raw = str(message or "").strip()
    if not raw:
        return None

    patterns = [
        r"(?:entre|entrar|abrir|abre|abrir)\s+(?:no|na|o|a)?\s*(?:cadastro|ficha)?\s*(?:do|da|de)?\s*cliente\s+(.+)$",
        r"(?:cadastro|ficha|dados)\s+(?:do|da|de)\s+cliente\s+(.+)$",
        r"(?:cadastro|ficha)\s+(?:do|da|de)\s+(.+)$",
        r"cliente\s+(.+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, raw, flags=re.IGNORECASE)
        if match:
            name = re.sub(r"[\]\[\)\(\.,;:!?]+$", "", str(match.group(1)).strip())
            name = re.sub(r"\s+", " ", name).strip()
            if name:
                return name
    return None


def is_visual_proof_request(message: str) -> bool:
    normalized = _normalize_key(message or "")
    if not normalized:
        return False

    visual_tokens = ("print", "screenshot", "imagem", "foto", "anexo", "ocr", "recorte", "referencia visual")
    data_tokens = ("telefone", "cpf", "email", "cadastro", "cliente", "dados", "com prova", "prova")
    ask_tokens = ("veja", "olha", "mostra", "mostre", "confirma", "confirme", "me fale")

    has_visual = any(token in normalized for token in visual_tokens)
    has_data = any(token in normalized for token in data_tokens)
    has_ask = any(token in normalized for token in ask_tokens)
    return has_visual and has_data and has_ask
