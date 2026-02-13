"""
MiniMax Text-to-Speech service for VIVA voice playback.
"""
from __future__ import annotations

import base64
import re
from typing import Any, Dict, Optional, Tuple

import httpx

from app.config import settings


class MinimaxTTSService:
    def __init__(self) -> None:
        self.api_key = settings.MINIMAX_API_KEY
        self.group_id = settings.MINIMAX_GROUP_ID
        self.base_url = settings.MINIMAX_BASE_URL.rstrip("/")
        self.model = settings.MINIMAX_TTS_MODEL
        self.voice_id = settings.MINIMAX_TTS_VOICE_ID
        self.speed = float(settings.MINIMAX_TTS_SPEED)
        self.pitch = float(settings.MINIMAX_TTS_PITCH)
        self.volume = float(settings.MINIMAX_TTS_VOLUME)
        self.format = settings.MINIMAX_TTS_FORMAT or "mp3"
        self.sample_rate = int(settings.MINIMAX_TTS_SAMPLE_RATE)
        self.bitrate = int(settings.MINIMAX_TTS_BITRATE)
        self.channel = int(settings.MINIMAX_TTS_CHANNEL)

    def is_configured(self) -> bool:
        return bool(self.api_key and self.group_id and self.voice_id)

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _decode_audio_payload(self, value: Any) -> bytes:
        if isinstance(value, bytes):
            return value
        raw = str(value or "").strip()
        if not raw:
            return b""
        if raw.startswith("data:audio"):
            parts = raw.split(",", 1)
            if len(parts) == 2:
                raw = parts[1].strip()

        # Hex fallback (observado em alguns exemplos de API).
        if re.fullmatch(r"[0-9a-fA-F]+", raw) and len(raw) % 2 == 0:
            try:
                return bytes.fromhex(raw)
            except Exception:
                pass

        # Base64 padrão.
        try:
            return base64.b64decode(raw, validate=True)
        except Exception:
            try:
                return base64.b64decode(raw + "===")
            except Exception:
                return b""

    async def synthesize(self, text: str) -> Tuple[bytes, str]:
        clean = str(text or "").strip()
        if not clean:
            raise ValueError("Texto vazio para TTS")
        if not self.is_configured():
            raise ValueError("MiniMax TTS nao configurado")

        endpoint = f"{self.base_url}/v1/t2a_v2?GroupId={self.group_id}"
        payload = {
            "model": self.model,
            "text": clean,
            "stream": False,
            "output_format": self.format,
            "voice_setting": {
                "voice_id": self.voice_id,
                "speed": self.speed,
                "vol": self.volume,
                "pitch": self.pitch,
            },
            "audio_setting": {
                "sample_rate": self.sample_rate,
                "bitrate": self.bitrate,
                "format": self.format,
                "channel": self.channel,
            },
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                endpoint,
                headers=self._headers(),
                json=payload,
            )

        if response.status_code != 200:
            raise ValueError(f"MiniMax erro ({response.status_code}): {response.text[:280]}")

        data = response.json() if response.text else {}
        base_resp = data.get("base_resp") if isinstance(data, dict) else {}
        if isinstance(base_resp, dict):
            status_code = int(base_resp.get("status_code") or 0)
            if status_code not in (0, 200):
                raise ValueError(f"MiniMax status {status_code}: {str(base_resp.get('status_msg') or 'erro')[:180]}")

        payload_data = data.get("data") if isinstance(data, dict) else {}
        audio_blob = b""
        if isinstance(payload_data, dict):
            audio_blob = self._decode_audio_payload(payload_data.get("audio"))
            if not audio_blob and isinstance(payload_data.get("audio_base64"), str):
                audio_blob = self._decode_audio_payload(payload_data.get("audio_base64"))

            audio_url = str(payload_data.get("audio_url") or "").strip()
            if not audio_blob and audio_url:
                async with httpx.AsyncClient(timeout=45.0) as client:
                    get_resp = await client.get(audio_url)
                if get_resp.status_code == 200:
                    audio_blob = get_resp.content

        if not audio_blob:
            raise ValueError("MiniMax nao retornou audio valido")

        media_type = "audio/mpeg" if self.format.lower() == "mp3" else "audio/wav"
        return audio_blob, media_type

    def get_status(self) -> Dict[str, Any]:
        return {
            "configured": self.is_configured(),
            "provider": "minimax",
            "model": self.model,
            "voice_id": self.voice_id,
            "format": self.format,
        }


minimax_tts_service = MinimaxTTSService()

