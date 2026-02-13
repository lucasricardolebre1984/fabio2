"""Shared helpers for VIVA routes/services.

Centraliza normalizacao e mapeadores usados por modulos que nao devem
depender diretamente de `app.api.v1.viva_core`.
"""

from __future__ import annotations

import json
import re
import unicodedata
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.viva_schemas import CampanhaItem, HandoffItem
from app.services.viva_campaign_repository_service import viva_campaign_repository_service


def _normalize_key(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto or "")
    without_accents = "".join(ch for ch in base if not unicodedata.combining(ch))
    normalized = without_accents.lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return " ".join(normalized.split())


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


def _sanitize_prompt(texto: str, max_len: int) -> str:
    texto_limpo = " ".join((texto or "").replace("\r", " ").split())
    if len(texto_limpo) <= max_len:
        return texto_limpo
    return texto_limpo[:max_len].rstrip() + "..."


def _extract_subject(texto: str) -> str:
    texto_limpo = " ".join((texto or "").replace("\r", " ").split())
    lower = texto_limpo.lower()
    markers = [
        "segue o texto a ser vinculado",
        "segue o texto",
        "texto a ser vinculado",
        "texto:",
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
    return await viva_campaign_repository_service.save_campaign(
        db=db,
        user_id=user_id,
        modo=modo,
        titulo=_sanitize_prompt(titulo or f"Campanha {modo}", 255),
        briefing=briefing,
        mensagem_original=mensagem_original,
        image_url=image_url,
        overlay=overlay or {},
        meta=meta or {},
    )


async def _get_recent_campaign_cast_ids(
    db: AsyncSession,
    user_id: Optional[UUID],
    modo: str,
    limit: int = 10,
) -> List[str]:
    return await viva_campaign_repository_service.get_recent_cast_ids(
        db=db,
        user_id=user_id,
        modo=modo,
        limit=limit,
    )


async def _get_recent_campaign_scene_ids(
    db: AsyncSession,
    user_id: Optional[UUID],
    modo: str,
    limit: int = 10,
) -> List[str]:
    return await viva_campaign_repository_service.get_recent_scene_ids(
        db=db,
        user_id=user_id,
        modo=modo,
        limit=limit,
    )


async def _clear_campaign_history(
    db: AsyncSession,
    user_id: UUID,
    modo: Optional[str] = None,
) -> int:
    return await viva_campaign_repository_service.clear_campaign_history(
        db=db,
        user_id=user_id,
        modo=modo,
    )
