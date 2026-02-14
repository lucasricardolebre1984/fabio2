"""
OpenAI service for VIVA chat and audio transcription.
"""
import hashlib
import math
import re
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
        self.model_embedding = settings.OPENAI_EMBEDDING_MODEL
        self.embedding_fallback_local = bool(settings.OPENAI_EMBEDDING_FALLBACK_LOCAL)
        self.embedding_fallback_dim = 1536
        self.timeout = float(settings.OPENAI_TIMEOUT_SECONDS)
        self._last_embedding_provider = "none"

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

    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 800,
    ):
        """Stream chat completion tokens em tempo real.
        
        Yields:
            str: Chunks de texto conforme OpenAI retorna
        """
        if not self.api_key:
            yield "Erro: OPENAI_API_KEY nao configurada"
            return

        normalized = self._normalize_messages(messages)
        if not normalized:
            yield "Erro: mensagem invalida para chat OpenAI"
            return

        payload: Dict[str, Any] = {
            "model": self.model_chat,
            "messages": normalized,
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=self._headers(),
                    json=payload,
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        yield f"Erro OpenAI stream ({response.status_code}): {error_text.decode()[:400]}"
                        return

                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        
                        if line.startswith("data: "):
                            data_str = line[6:]  # Remove "data: " prefix
                            
                            if data_str == "[DONE]":
                                break
                            
                            try:
                                import json
                                chunk_data = json.loads(data_str)
                                choices = chunk_data.get("choices", [])
                                
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content")
                                    
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            yield f"Erro no streaming: {str(e)}"

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

    async def embed_text(self, text: str) -> Optional[List[float]]:
        clean = str(text or "").strip()
        if not clean:
            return None

        if not self.api_key:
            if self.embedding_fallback_local:
                self._last_embedding_provider = "local_fallback"
                return self._fallback_embed_text(clean)
            self._last_embedding_provider = "disabled"
            return None

        payload: Dict[str, Any] = {
            "model": self.model_embedding,
            "input": clean,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers=self._headers(),
                    json=payload,
                )
        except Exception:
            if self.embedding_fallback_local:
                self._last_embedding_provider = "local_fallback"
                return self._fallback_embed_text(clean)
            self._last_embedding_provider = "error"
            return None

        if response.status_code != 200:
            if self.embedding_fallback_local:
                self._last_embedding_provider = "local_fallback"
                return self._fallback_embed_text(clean)
            self._last_embedding_provider = f"error_{response.status_code}"
            return None

        try:
            data = response.json()
        except Exception:
            if self.embedding_fallback_local:
                self._last_embedding_provider = "local_fallback"
                return self._fallback_embed_text(clean)
            self._last_embedding_provider = "error_json"
            return None
        items = data.get("data")
        if not isinstance(items, list) or not items:
            if self.embedding_fallback_local:
                self._last_embedding_provider = "local_fallback"
                return self._fallback_embed_text(clean)
            self._last_embedding_provider = "error_payload"
            return None

        first = items[0] if isinstance(items[0], dict) else {}
        embedding = first.get("embedding")
        if not isinstance(embedding, list):
            if self.embedding_fallback_local:
                self._last_embedding_provider = "local_fallback"
                return self._fallback_embed_text(clean)
            self._last_embedding_provider = "error_embedding_shape"
            return None

        vector: List[float] = []
        for item in embedding:
            try:
                vector.append(float(item))
            except Exception:
                if self.embedding_fallback_local:
                    self._last_embedding_provider = "local_fallback"
                    return self._fallback_embed_text(clean)
                self._last_embedding_provider = "error_embedding_value"
                return None
        self._last_embedding_provider = "openai"
        return vector

    def _fallback_embed_text(self, text: str) -> Optional[List[float]]:
        """Deterministic local hash embedding to keep RAG functional without API quota."""
        clean = str(text or "").strip().lower()
        if not clean:
            return None

        dim = self.embedding_fallback_dim
        vector = [0.0] * dim

        tokens = re.findall(r"[a-z0-9]+", clean)
        if not tokens:
            tokens = [clean]

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % dim
            sign = -1.0 if (digest[4] & 1) else 1.0
            weight = 1.0 + (float(digest[5]) / 255.0) * 0.5
            vector[idx] += sign * weight

        # Add a small whole-text anchor to reduce collisions for short phrases.
        full_digest = hashlib.sha256(clean.encode("utf-8")).digest()
        for offset in range(0, 16, 4):
            idx = int.from_bytes(full_digest[offset:offset + 4], "big") % dim
            sign = -1.0 if (full_digest[(offset + 4) % len(full_digest)] & 1) else 1.0
            vector[idx] += sign * 0.35

        norm = math.sqrt(sum(value * value for value in vector))
        if norm <= 1e-12:
            return None

        return [value / norm for value in vector]

    def get_status(self) -> Dict[str, Any]:
        return {
            "api_configurada": bool(self.api_key),
            "modelos": {
                "chat": self.model_chat,
                "audio": self.model_audio,
                "image": self.model_image,
                "vision": self.model_vision,
                "embedding": self.model_embedding,
            },
        }

    def get_embedding_runtime_status(self) -> Dict[str, Any]:
        provider = str(self._last_embedding_provider or "none")
        premium_active = provider == "openai"
        return {
            "configured": bool(self.api_key),
            "model": self.model_embedding,
            "fallback_enabled": self.embedding_fallback_local,
            "provider_last": provider,
            "semantic_tier": "premium_openai" if premium_active else "fallback_local",
            "premium_active": premium_active,
        }


openai_service = OpenAIService()
