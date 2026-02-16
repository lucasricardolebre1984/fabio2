# Testes para API de autenticação
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.db.session import get_db


@pytest.mark.asyncio
async def test_login_success():
    """Test login com credenciais válidas"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "fabio@fcsolucoes.com", "password": "1234"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login com credenciais inválidas"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "invalid@example.com", "password": "wrong"}
        )
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
async def test_protected_route_requires_auth():
    """Test que rotas protegidas requerem autenticação"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/api/v1/contratos/")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_valid_token():
    """Test acesso a rota protegida com token válido"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Login primeiro
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "fabio@fcsolucoes.com", "password": "1234"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Acessar rota protegida
        response = await client.get(
            "/api/v1/contratos/",
            headers={"Authorization": f"Bearer {token}"}
        )
        # Pode ser 200 ou outro código dependendo dos dados, mas não 401
        assert response.status_code != 401
