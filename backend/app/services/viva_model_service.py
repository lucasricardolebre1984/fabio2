"""
VIVA model router service.
OpenAI-only provider for institutional VIVA operation.
"""
from typing import Any, Dict, List

from app.config import settings
from app.services.openai_service import openai_service


class VivaModelService:
    """Provider router used by WhatsApp VIVA flows."""

    def __init__(self) -> None:
        self.provider = (settings.VIVA_PROVIDER or "openai").strip().lower()

    def _is_error_response(self, text: Any) -> bool:
        if not isinstance(text, str):
            return True
        normalized = text.strip().lower()
        if not normalized:
            return True
        return normalized.startswith("erro") or normalized.startswith("error")

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        result = await openai_service.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if not self._is_error_response(result):
            return result
        return f"Erro: falha no provedor OpenAI. detalhe={result}"

    async def audio_transcribe_bytes(
        self,
        audio_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> str:
        result = await openai_service.audio_transcribe_bytes(
            audio_bytes=audio_bytes,
            filename=filename,
            content_type=content_type,
        )
        if not self._is_error_response(result):
            return result
        return f"Erro: falha na transcricao de audio com OpenAI. detalhe={result}"

    def get_status(self) -> Dict[str, Any]:
        return {
            "provider_preferido": self.provider,
            "openai": openai_service.get_status(),
        }


viva_model_service = VivaModelService()
