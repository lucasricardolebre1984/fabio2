"""Intent helpers for campaign queries in VIVA domain router."""

from __future__ import annotations

from typing import Optional

from app.services.viva_chat_domain_service import _is_direct_generation_intent, _is_image_request
from app.services.viva_shared_service import _normalize_key


def is_campaign_list_intent(message: str) -> bool:
    normalized = _normalize_key(message or "")
    if not normalized:
        return False
    has_campaign = "campanha" in normalized or "campanhas" in normalized
    has_list_signal = any(
        token in normalized
        for token in ("listar", "liste", "lista", "quais", "historico", "criadas", "criados", "mostre", "list")
    )
    has_generate_signal = bool(_is_image_request(message) or _is_direct_generation_intent(message))
    return has_campaign and has_list_signal and not has_generate_signal


def is_campaign_count_intent(message: str) -> bool:
    normalized = _normalize_key(message or "")
    if not normalized:
        return False
    has_campaign = "campanha" in normalized or "campanhas" in normalized
    has_count = any(
        token in normalized
        for token in ("quantas", "quanto", "total", "numero", "qtd", "quantidade", "feitas", "criadas")
    )
    has_generate_signal = bool(_is_image_request(message) or _is_direct_generation_intent(message))
    return has_campaign and has_count and not has_generate_signal


def extract_campaign_mode_filter(message: str) -> Optional[str]:
    normalized = _normalize_key(message or "")
    if "rezeta" in normalized:
        return "REZETA"
    if " fc " in f" {normalized} " or "fc solucoes" in normalized:
        return "FC"
    return None
