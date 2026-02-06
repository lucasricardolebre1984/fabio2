"""
Z.AI Service - API Oficial
Suporta: Chat, Visão, Áudio, Imagem e Vídeo
"""
from typing import List, Dict, Any, Optional
import httpx

from app.config import settings


class ZAIService:
    """Serviço unificado para Z.AI (API oficial)."""

    def __init__(self) -> None:
        self.api_key = settings.ZAI_API_KEY
        self.base_url = settings.ZAI_BASE_URL.rstrip("/")
        self.model_chat = settings.ZAI_MODEL_CHAT
        self.model_vision = settings.ZAI_MODEL_VISION
        self.model_audio = settings.ZAI_MODEL_AUDIO
        self.model_image = settings.ZAI_MODEL_IMAGE
        self.model_video = settings.ZAI_MODEL_VIDEO

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 800,
        stream: bool = False,
    ) -> str:
        if not self.api_key:
            return "Erro: ZAI_API_KEY não configurada"

        payload = {
            "model": self.model_chat,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )

        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]

        if response.status_code == 401:
            return "Erro: API key inválida ou não autorizada"

        return f"Erro {response.status_code}: {response.text[:200]}"

    async def vision_base64(
        self,
        image_base64: str,
        prompt: str,
        mime_type: str = "image/jpeg",
        max_tokens: int = 800,
    ) -> str:
        if not self.api_key:
            return "Erro: ZAI_API_KEY não configurada"

        image_url = f"data:{mime_type};base64,{image_base64}"

        payload = {
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
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )

        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]

        return f"Erro {response.status_code}: {response.text[:200]}"

    async def audio_transcribe_bytes(
        self,
        audio_bytes: bytes,
        filename: str,
        content_type: str,
        stream: bool = False,
        prompt: Optional[str] = None,
    ) -> str:
        if not self.api_key:
            return "Erro: ZAI_API_KEY não configurada"

        files = {"file": (filename, audio_bytes, content_type)}
        data: Dict[str, Any] = {
            "model": self.model_audio,
            "stream": "true" if stream else "false",
        }
        if prompt:
            data["prompt"] = prompt

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                data=data,
                files=files,
            )

        if response.status_code == 200:
            data = response.json()
            return data.get("text", "")

        return f"Erro {response.status_code}: {response.text[:200]}"

    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.api_key:
            return {"success": False, "error": "ZAI_API_KEY não configurada"}

        payload: Dict[str, Any] = {
            "model": self.model_image,
            "prompt": prompt,
            "size": size,
        }
        if quality:
            payload["quality"] = quality

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/images/generations",
                headers=self._headers(),
                json=payload,
            )

        if response.status_code == 200:
            payload = response.json()
            if isinstance(payload, dict) and payload.get("error"):
                return {"success": False, "error": payload.get("error")}
            return {"success": True, "data": payload}

        return {"success": False, "error": response.text}

    async def generate_video(
        self,
        prompt: str,
        size: str = "1920x1080",
        fps: int = 30,
        duration: int = 5,
        quality: str = "quality",
        with_audio: bool = True,
    ) -> Dict[str, Any]:
        if not self.api_key:
            return {"success": False, "error": "ZAI_API_KEY não configurada"}

        payload = {
            "model": self.model_video,
            "prompt": prompt,
            "size": size,
            "fps": fps,
            "duration": duration,
            "quality": quality,
            "with_audio": with_audio,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/videos/generations",
                headers=self._headers(),
                json=payload,
            )

        if response.status_code == 200:
            return {"success": True, "data": response.json()}

        return {"success": False, "error": response.text}

    async def get_async_result(self, task_id: str) -> Dict[str, Any]:
        if not self.api_key:
            return {"success": False, "error": "ZAI_API_KEY não configurada"}

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{self.base_url}/async-result/{task_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )

        if response.status_code == 200:
            return {"success": True, "data": response.json()}

        return {"success": False, "error": response.text}

    def get_status(self) -> Dict[str, Any]:
        return {
            "api_configurada": bool(self.api_key),
            "modelos": {
                "chat": self.model_chat,
                "vision": self.model_vision,
                "audio": self.model_audio,
                "image": self.model_image,
                "video": self.model_video,
            },
        }


zai_service = ZAIService()
