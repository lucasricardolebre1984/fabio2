# Configuração de testes
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.db.session import get_db
from app.main import app


# Fixture para cliente HTTP async
@pytest.fixture
async def client():
    """Cliente HTTP para testes"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


# Fixture para banco de dados de teste
@pytest.fixture
async def db_session():
    """Sessão de banco de dados para testes"""
    # Usar banco de teste separado se disponível
    test_db_url = settings.DATABASE_URL.replace("fabio2", "fabio2_test") if "fabio2" in settings.DATABASE_URL else settings.DATABASE_URL

    engine = create_async_engine(test_db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session


# Fixture para autenticação
@pytest.fixture
async def auth_token(client):
    """Token de autenticação para testes"""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "fabio@fcsolucoes.com", "password": "1234"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


# Fixture para headers de autenticação
@pytest.fixture
def auth_headers(auth_token):
    """Headers com token de autenticação"""
    if auth_token:
        return {"Authorization": f"Bearer {auth_token}"}
    return {}
