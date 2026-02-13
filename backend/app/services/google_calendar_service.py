"""
Google Calendar bridge for internal Agenda <-> external calendar sync.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import json
from typing import Any, Dict, Optional
from urllib.parse import urlencode, quote
from uuid import UUID

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings


class GoogleCalendarService:
    _auth_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    _token_url = "https://oauth2.googleapis.com/token"
    _api_base = "https://www.googleapis.com/calendar/v3"

    async def ensure_tables(self, db: AsyncSession) -> None:
        await db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS google_calendar_connections (
                    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                    access_token TEXT NOT NULL,
                    refresh_token TEXT,
                    token_type VARCHAR(40),
                    expires_at TIMESTAMPTZ,
                    scope TEXT,
                    calendar_id VARCHAR(255) NOT NULL DEFAULT 'primary',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ
                )
                """
            )
        )
        await db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS google_calendar_event_links (
                    agenda_event_id UUID PRIMARY KEY REFERENCES agenda(id) ON DELETE CASCADE,
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    google_event_id VARCHAR(255) NOT NULL,
                    calendar_id VARCHAR(255) NOT NULL DEFAULT 'primary',
                    synced_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ
                )
                """
            )
        )
        await db.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_google_calendar_links_user
                ON google_calendar_event_links(user_id, synced_at DESC)
                """
            )
        )

    def _is_configured(self) -> bool:
        return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET and settings.GOOGLE_REDIRECT_URI)

    def _sign_state(self, payload_b64: str) -> str:
        digest = hmac.new(
            (settings.SECRET_KEY or "dev-secret-key").encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return digest

    def _encode_state(self, user_id: UUID) -> str:
        payload = {
            "user_id": str(user_id),
            "ts": int(datetime.now(timezone.utc).timestamp()),
        }
        payload_raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        payload_b64 = base64.urlsafe_b64encode(payload_raw).decode("utf-8").rstrip("=")
        sig = self._sign_state(payload_b64)
        return f"{payload_b64}.{sig}"

    def _decode_state(self, state: str) -> Dict[str, Any]:
        if "." not in (state or ""):
            raise ValueError("state invalido")
        payload_b64, sig = state.split(".", 1)
        expected = self._sign_state(payload_b64)
        if not hmac.compare_digest(sig, expected):
            raise ValueError("state assinatura invalida")
        padding = "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode((payload_b64 + padding).encode("utf-8")).decode("utf-8"))
        ts = int(payload.get("ts") or 0)
        now_ts = int(datetime.now(timezone.utc).timestamp())
        if now_ts - ts > 1800:
            raise ValueError("state expirado")
        user_id = str(payload.get("user_id") or "").strip()
        if not user_id:
            raise ValueError("state sem user_id")
        return payload

    async def build_connect_url(self, user_id: UUID) -> str:
        if not self._is_configured():
            raise ValueError("Google Calendar nao configurado")
        state = self._encode_state(user_id)
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": settings.GOOGLE_CALENDAR_SCOPE,
            "access_type": "offline",
            "prompt": "consent",
            "include_granted_scopes": "true",
            "state": state,
        }
        return f"{self._auth_base_url}?{urlencode(params)}"

    async def _exchange_code(self, code: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self._token_url,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        if response.status_code != 200:
            raise ValueError(f"Falha token Google ({response.status_code}): {response.text[:250]}")
        return response.json()

    async def _refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self._token_url,
                data={
                    "refresh_token": refresh_token,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "grant_type": "refresh_token",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        if response.status_code != 200:
            raise ValueError(f"Falha refresh Google ({response.status_code}): {response.text[:250]}")
        return response.json()

    async def exchange_code_and_store(self, db: AsyncSession, *, code: str, state: str) -> UUID:
        await self.ensure_tables(db)
        payload = self._decode_state(state)
        user_id = UUID(str(payload["user_id"]))
        token = await self._exchange_code(code)
        expires_in = int(token.get("expires_in") or 3600)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=max(60, expires_in - 30))

        await db.execute(
            text(
                """
                INSERT INTO google_calendar_connections (
                    user_id, access_token, refresh_token, token_type, expires_at,
                    scope, calendar_id, created_at, updated_at
                )
                VALUES (
                    :user_id, :access_token, :refresh_token, :token_type, :expires_at,
                    :scope, :calendar_id, NOW(), NOW()
                )
                ON CONFLICT (user_id) DO UPDATE
                SET access_token = EXCLUDED.access_token,
                    refresh_token = COALESCE(EXCLUDED.refresh_token, google_calendar_connections.refresh_token),
                    token_type = EXCLUDED.token_type,
                    expires_at = EXCLUDED.expires_at,
                    scope = EXCLUDED.scope,
                    calendar_id = COALESCE(google_calendar_connections.calendar_id, EXCLUDED.calendar_id),
                    updated_at = NOW()
                """
            ),
            {
                "user_id": str(user_id),
                "access_token": str(token.get("access_token") or ""),
                "refresh_token": token.get("refresh_token"),
                "token_type": token.get("token_type"),
                "expires_at": expires_at,
                "scope": token.get("scope"),
                "calendar_id": settings.GOOGLE_CALENDAR_DEFAULT_ID,
            },
        )
        await db.commit()
        return user_id

    async def _get_connection(self, db: AsyncSession, user_id: UUID) -> Optional[Dict[str, Any]]:
        await self.ensure_tables(db)
        row = await db.execute(
            text(
                """
                SELECT user_id, access_token, refresh_token, token_type, expires_at, scope, calendar_id
                FROM google_calendar_connections
                WHERE user_id = CAST(:user_id AS UUID)
                """
            ),
            {"user_id": str(user_id)},
        )
        item = row.mappings().first()
        return dict(item) if item else None

    async def _get_access_token(self, db: AsyncSession, user_id: UUID) -> Optional[str]:
        conn = await self._get_connection(db, user_id)
        if not conn:
            return None
        access_token = str(conn.get("access_token") or "").strip()
        refresh_token = str(conn.get("refresh_token") or "").strip()
        expires_at = conn.get("expires_at")
        now = datetime.now(timezone.utc)
        if isinstance(expires_at, datetime) and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if access_token and (not isinstance(expires_at, datetime) or expires_at > now + timedelta(seconds=45)):
            return access_token
        if not refresh_token:
            return access_token or None

        refreshed = await self._refresh_token(refresh_token)
        new_access = str(refreshed.get("access_token") or "").strip()
        if not new_access:
            return access_token or None
        expires_in = int(refreshed.get("expires_in") or 3600)
        new_expiry = now + timedelta(seconds=max(60, expires_in - 30))
        await db.execute(
            text(
                """
                UPDATE google_calendar_connections
                SET access_token = :access_token,
                    token_type = COALESCE(:token_type, token_type),
                    expires_at = :expires_at,
                    updated_at = NOW()
                WHERE user_id = CAST(:user_id AS UUID)
                """
            ),
            {
                "user_id": str(user_id),
                "access_token": new_access,
                "token_type": refreshed.get("token_type"),
                "expires_at": new_expiry,
            },
        )
        await db.commit()
        return new_access

    async def get_status(self, db: AsyncSession, user_id: UUID) -> Dict[str, Any]:
        conn = await self._get_connection(db, user_id)
        if not conn:
            return {
                "configured": self._is_configured(),
                "connected": False,
                "calendar_id": None,
                "scope": None,
                "expires_at": None,
            }
        return {
            "configured": self._is_configured(),
            "connected": True,
            "calendar_id": conn.get("calendar_id") or settings.GOOGLE_CALENDAR_DEFAULT_ID,
            "scope": conn.get("scope"),
            "expires_at": conn.get("expires_at"),
        }

    async def disconnect(self, db: AsyncSession, user_id: UUID) -> None:
        await self.ensure_tables(db)
        await db.execute(
            text("DELETE FROM google_calendar_connections WHERE user_id = CAST(:user_id AS UUID)"),
            {"user_id": str(user_id)},
        )
        await db.execute(
            text("DELETE FROM google_calendar_event_links WHERE user_id = CAST(:user_id AS UUID)"),
            {"user_id": str(user_id)},
        )
        await db.commit()

    async def _google_request(
        self,
        *,
        method: str,
        path: str,
        token: str,
        json_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        url = f"{self._api_base}{path}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(method=method, url=url, headers=headers, json=json_payload)
        if response.status_code in (200, 201):
            if response.text.strip():
                return response.json()
            return {}
        if response.status_code == 204:
            return {}
        raise ValueError(f"Google Calendar API erro ({response.status_code}): {response.text[:250]}")

    async def _get_google_event_link(self, db: AsyncSession, agenda_event_id: UUID) -> Optional[Dict[str, Any]]:
        row = await db.execute(
            text(
                """
                SELECT agenda_event_id, user_id, google_event_id, calendar_id
                FROM google_calendar_event_links
                WHERE agenda_event_id = CAST(:agenda_event_id AS UUID)
                """
            ),
            {"agenda_event_id": str(agenda_event_id)},
        )
        item = row.mappings().first()
        return dict(item) if item else None

    async def _upsert_google_event_link(
        self,
        db: AsyncSession,
        *,
        agenda_event_id: UUID,
        user_id: UUID,
        google_event_id: str,
        calendar_id: str,
    ) -> None:
        await db.execute(
            text(
                """
                INSERT INTO google_calendar_event_links (
                    agenda_event_id, user_id, google_event_id, calendar_id, synced_at, created_at, updated_at
                )
                VALUES (
                    :agenda_event_id, :user_id, :google_event_id, :calendar_id, NOW(), NOW(), NOW()
                )
                ON CONFLICT (agenda_event_id) DO UPDATE
                SET google_event_id = EXCLUDED.google_event_id,
                    calendar_id = EXCLUDED.calendar_id,
                    synced_at = NOW(),
                    updated_at = NOW()
                """
            ),
            {
                "agenda_event_id": str(agenda_event_id),
                "user_id": str(user_id),
                "google_event_id": google_event_id,
                "calendar_id": calendar_id,
            },
        )

    def _agenda_to_google_payload(self, evento: Any) -> Dict[str, Any]:
        start_dt = evento.data_inicio
        end_dt = evento.data_fim or (evento.data_inicio + timedelta(minutes=30))
        return {
            "summary": str(evento.titulo or "Compromisso"),
            "description": str(evento.descricao or ""),
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "America/Sao_Paulo"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "America/Sao_Paulo"},
        }

    async def sync_agenda_event(self, db: AsyncSession, *, user_id: UUID, evento: Any) -> Dict[str, Any]:
        if not settings.GOOGLE_CALENDAR_SYNC_ENABLED:
            return {"synced": False, "reason": "sync_disabled"}
        if not self._is_configured():
            return {"synced": False, "reason": "not_configured"}
        token = await self._get_access_token(db, user_id)
        if not token:
            return {"synced": False, "reason": "not_connected"}

        conn = await self._get_connection(db, user_id)
        calendar_id = str((conn or {}).get("calendar_id") or settings.GOOGLE_CALENDAR_DEFAULT_ID)
        calendar_escaped = quote(calendar_id, safe="")
        payload = self._agenda_to_google_payload(evento)
        link = await self._get_google_event_link(db, evento.id)

        if link and link.get("google_event_id"):
            event_id = str(link["google_event_id"])
            data = await self._google_request(
                method="PATCH",
                path=f"/calendars/{calendar_escaped}/events/{quote(event_id, safe='')}",
                token=token,
                json_payload=payload,
            )
            google_event_id = str(data.get("id") or event_id)
        else:
            data = await self._google_request(
                method="POST",
                path=f"/calendars/{calendar_escaped}/events",
                token=token,
                json_payload=payload,
            )
            google_event_id = str(data.get("id") or "")
            if not google_event_id:
                raise ValueError("Google Calendar nao retornou event id")

        await self._upsert_google_event_link(
            db,
            agenda_event_id=evento.id,
            user_id=user_id,
            google_event_id=google_event_id,
            calendar_id=calendar_id,
        )
        await db.commit()
        return {"synced": True, "google_event_id": google_event_id, "calendar_id": calendar_id}

    async def delete_synced_agenda_event(self, db: AsyncSession, *, user_id: UUID, agenda_event_id: UUID) -> Dict[str, Any]:
        if not settings.GOOGLE_CALENDAR_SYNC_ENABLED:
            return {"synced": False, "reason": "sync_disabled"}
        if not self._is_configured():
            return {"synced": False, "reason": "not_configured"}

        link = await self._get_google_event_link(db, agenda_event_id)
        if not link:
            return {"synced": False, "reason": "not_linked"}

        token = await self._get_access_token(db, user_id)
        if not token:
            return {"synced": False, "reason": "not_connected"}

        calendar_id = str(link.get("calendar_id") or settings.GOOGLE_CALENDAR_DEFAULT_ID)
        google_event_id = str(link.get("google_event_id") or "")
        if google_event_id:
            await self._google_request(
                method="DELETE",
                path=f"/calendars/{quote(calendar_id, safe='')}/events/{quote(google_event_id, safe='')}",
                token=token,
            )

        await db.execute(
            text("DELETE FROM google_calendar_event_links WHERE agenda_event_id = CAST(:agenda_event_id AS UUID)"),
            {"agenda_event_id": str(agenda_event_id)},
        )
        await db.commit()
        return {"synced": True, "deleted": True}


google_calendar_service = GoogleCalendarService()

