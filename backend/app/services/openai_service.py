"""
OpenAI service for VIVA chat and audio transcription.
"""
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings


class OpenAIService:
    """OpenAI adapter with resilient parsing and endpoint fallback."""

    def __init__(self) -> None:
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL.rstrip("/")
        self.model_chat = settings.OPENAI_API_MODEL
        self.model_audio = settings.OPENAI_AUDIO_MODEL
        self.model_image = settings.OPENAI_IMAGE_MODEL
        self.model_vision = settings.OPENAI_VISION_MODEL
        self.timeout = float(settings.OPENAI_TIMEOUT_SECONDS)

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _coerce_message_content(self, value: Any) -> str:
        if isinstance(value, str):
            return value.strip()

        if isinstance(value, list):
            parts: List[str] = []
            for item in value:
                text = self._coerce_message_content(item)
                if text:
                    parts.append(text)
            return "\n".join(parts).strip()

        if isinstance(value, dict):
            for key in ("text", "content", "value"):
                text = self._coerce_message_content(value.get(key))
                if text:
                    return text
            return ""

        return ""

    def _normalize_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        normalized: List[Dict[str, str]] = []
        for msg in messages or []:
            role = str(msg.get("role") or "user").strip().lower()
            if role not in {"system", "user", "assistant"}:
                role = "user"
            content = self._coerce_message_content(msg.get("content"))
            if content:
                normalized.append({"role": role, "content": content})
        return normalized

    def _extract_chat_completion_content(self, payload: Dict[str, Any]) -> str:
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            return ""

        first = choices[0] if isinstance(choices[0], dict) else {}
        message = first.get("message") if isinstance(first.get("message"), dict) else {}
        content = self._coerce_message_content(message.get("content"))
        if content:
            return content
        return self._coerce_message_content(first.get("text"))

    def _extract_responses_content(self, payload: Dict[str, Any]) -> str:
        output_text = payload.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return output_text.strip()

        output = payload.get("output")
        if isinstance(output, list):
            for item in output:
                if not isinstance(item, dict):
                    continue
                content_list = item.get("content")
                if not isinstance(content_list, list):
                    continue
                for part in content_list:
                    if not isinstance(part, dict):
                        continue
                    if part.get("type") in {"output_text", "text"}:
                        text = self._coerce_message_content(part.get("text"))
                        if text:
                            return text
        return ""

    async def _chat_completions(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        with_optional_params: bool,
    ) -> tuple[Optional[str], Optional[str], int]:
        payload: Dict[str, Any] = {
            "model": self.model_chat,
            "messages": messages,
        }
        if with_optional_params:
            payload["temperature"] = temperature
            payload["max_completion_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )

        if response.status_code == 200:
            content = self._extract_chat_completion_content(response.json())
            if content:
                return content, None, 200
            return None, "Resposta vazia no endpoint /chat/completions", 200

        return None, response.text[:400], response.status_code

    async def _responses_api(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
    ) -> tuple[Optional[str], Optional[str], int]:
        input_items: List[Dict[str, Any]] = []
        for msg in messages:
            input_items.append(
                {
                    "role": msg["role"],
                    "content": [{"type": "input_text", "text": msg["content"]}],
                }
            )

        payload: Dict[str, Any] = {
            "model": self.model_chat,
            "input": input_items,
            "max_output_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/responses",
                headers=self._headers(),
                json=payload,
            )

        if response.status_code == 200:
            content = self._extract_responses_content(response.json())
            if content:
                return content, None, 200
            return None, "Resposta vazia no endpoint /responses", 200

        return None, response.text[:400], response.status_code

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 800,
    ) -> str:
        if not self.api_key:
            return "Erro: OPENAI_API_KEY nao configurada"

        normalized = self._normalize_messages(messages)
        if not normalized:
            return "Erro: mensagem invalida para chat OpenAI"

        content, error, status = await self._chat_completions(
            messages=normalized,
            temperature=temperature,
            max_tokens=max_tokens,
            with_optional_params=True,
        )
        if content:
            return content

        # Retry sem parametros opcionais (alguns modelos recusam temperature/tokens).
        if status in {400, 422}:
            content, error, _ = await self._chat_completions(
                messages=normalized,
                temperature=temperature,
                max_tokens=max_tokens,
                with_optional_params=False,
            )
            if content:
                return content

        # Fallback para endpoint responses.
        content, responses_error, _ = await self._responses_api(
            messages=normalized,
            max_tokens=max_tokens,
        )
        if content:
            return content

        detail = responses_error or error or "falha desconhecida"
        return f"Erro OpenAI chat: {detail}"

    async def audio_transcribe_bytes(
        self,
        audio_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> str:
        if not self.api_key:
            return "Erro: OPENAI_API_KEY nao configurada"
        if not audio_bytes:
            return "Erro: audio vazio"

        files = {"file": (filename, audio_bytes, content_type)}
        data: Dict[str, Any] = {"model": self.model_audio}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                data=data,
                files=files,
            )

        if response.status_code == 200:
            payload = response.json()
            texto = str(payload.get("text") or "").strip()
            if texto:
                return texto
            return "Erro OpenAI audio: resposta vazia"

        return f"Erro OpenAI audio ({response.status_code}): {response.text[:300]}"

    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.api_key:
            return {"success": False, "error": "OPENAI_API_KEY nao configurada"}

        payload: Dict[str, Any] = {
            "model": self.model_image,
            "prompt": prompt,
            "size": size,
        }
        if quality:
            payload["quality"] = quality

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/images/generations",
                headers=self._headers(),
                json=payload,
            )

        if response.status_code == 200:
            data = response.json()
            return {"success": True, "data": data}

        return {"success": False, "error": response.text[:600]}

    async def vision_base64(
        self,
        image_base64: str,
        prompt: str,
        mime_type: str = "image/jpeg",
        max_tokens: int = 700,
    ) -> str:
        if not self.api_key:
            return "Erro: OPENAI_API_KEY nao configurada"

        image_url = f"data:{mime_type};base64,{image_base64}"
        payload: Dict[str, Any] = {
            "model": self.model_vision,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            "max_completion_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )

        if response.status_code == 200:
            content = self._extract_chat_completion_content(response.json())
            if content:
                return content
            return "Erro OpenAI vision: resposta vazia"

        return f"Erro OpenAI vision ({response.status_code}): {response.text[:300]}"

    def get_status(self) -> Dict[str, Any]:
        return {
            "api_configurada": bool(self.api_key),
            "modelos": {
                "chat": self.model_chat,
                "audio": self.model_audio,
                "image": self.model_image,
                "vision": self.model_vision,
            },
        }


openai_service = OpenAIService()
