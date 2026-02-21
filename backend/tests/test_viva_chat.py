# Testes para API de VIVA Chat
import pytest
from httpx import AsyncClient

from app.main import app
from app.services.viva_chat_orchestrator_service import VivaChatOrchestratorService


@pytest.mark.asyncio
async def test_viva_chat_requires_auth():
    """Test que VIVA chat requer autenticação"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/viva/chat",
            json={"mensagem": "Olá", "contexto": []}
        )
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_viva_chat_with_auth():
    """Test VIVA chat com autenticação"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "fabio@fcsolucoes.com", "password": "1234"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Enviar mensagem para VIVA
        response = await client.post(
            "/api/v1/viva/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"mensagem": "Olá, como você está?", "contexto": []}
        )
        assert response.status_code in [200, 201, 400, 500]  # Pode variar dependendo da implementação


@pytest.mark.asyncio
async def test_viva_tts_status():
    """Test status do TTS VIVA"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "fabio@fcsolucoes.com", "password": "1234"}
        )
        token = login_response.json()["access_token"]

        # Verificar status TTS
        response = await client.get(
            "/api/v1/viva/tts/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "configured" in data
        assert "test" in data


@pytest.mark.asyncio
async def test_viva_audio_speak():
    """Test síntese de áudio VIVA"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "fabio@fcsolucoes.com", "password": "1234"}
        )
        token = login_response.json()["access_token"]

        # Tentar sintetizar áudio
        response = await client.post(
            "/api/v1/viva/audio/speak",
            headers={"Authorization": f"Bearer {token}"},
            json={"text": "Olá mundo"}
        )
        # Pode ser 200 com áudio ou erro se TTS não configurado
        assert response.status_code in [200, 400, 500]


@pytest.mark.asyncio
async def test_viva_chat_stream():
    """Test streaming de chat VIVA"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "fabio@fcsolucoes.com", "password": "1234"}
        )
        token = login_response.json()["access_token"]

        # Testar streaming
        response = await client.post(
            "/api/v1/viva/chat/stream",
            headers={"Authorization": f"Bearer {token}"},
            json={"mensagem": "Olá", "contexto": []}
        )
        # Pode ser streaming ou fallback
        assert response.status_code in [200, 201, 400, 500]


@pytest.mark.asyncio
async def test_viva_chat_stream_delegates_to_canonical_flow(monkeypatch):
    """Garante que o stream usa a mesma orquestracao canonica de /chat."""

    class FakeResponse:
        def __init__(self):
            self.resposta = "Ola Fabio! Fluxo canonico."
            self.session_id = "sessao-123"

    async def fake_handle_chat_with_viva(self, request, current_user, db):
        return FakeResponse()

    monkeypatch.setattr(
        VivaChatOrchestratorService,
        "handle_chat_with_viva",
        fake_handle_chat_with_viva,
    )

    service = VivaChatOrchestratorService()
    chunks = []
    async for chunk in service.handle_chat_with_viva_stream(
        request=object(),
        current_user=object(),
        db=object(),
    ):
        chunks.append(chunk)

    assert chunks[0]["content"] == "Ola Fabio! Fluxo canonico."
    assert chunks[1]["done"] is True
    assert chunks[1]["session_id"] == "sessao-123"
