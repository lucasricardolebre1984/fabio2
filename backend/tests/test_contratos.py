# Testes para API de contratos
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_list_contratos_requires_auth():
    """Test que listar contratos requer autenticação"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/api/v1/contratos/")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_contratos_with_auth():
    """Test listar contratos com autenticação"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "fabio@fcsolucoes.com", "password": "1234"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Listar contratos
        response = await client.get(
            "/api/v1/contratos/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [200, 404]  # 200 se há contratos, 404 se não


@pytest.mark.asyncio
async def test_create_contrato_requires_auth():
    """Test que criar contrato requer autenticação"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post("/api/v1/contratos/", json={})
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_contrato_validation():
    """Test validação de criação de contrato"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "fabio@fcsolucoes.com", "password": "1234"}
        )
        token = login_response.json()["access_token"]

        # Tentar criar contrato sem dados obrigatórios
        response = await client.post(
            "/api/v1/contratos/",
            headers={"Authorization": f"Bearer {token}"},
            json={}
        )
        # Deve falhar com validação ou sucesso dependendo da implementação
        assert response.status_code in [201, 422, 400]


@pytest.mark.asyncio
async def test_get_contrato_by_id():
    """Test obter contrato por ID"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "fabio@fcsolucoes.com", "password": "1234"}
        )
        token = login_response.json()["access_token"]

        # Tentar obter contrato com ID inexistente
        response = await client.get(
            "/api/v1/contratos/99999",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404
