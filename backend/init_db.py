"""Script para inicializar banco e criar usuário."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.db.base import Base
from app.db.session import DATABASE_URL, AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash

async def init_database():
    """Criar todas as tabelas."""
    print("Criando tabelas...")
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("✅ Tabelas criadas!")

async def create_admin_user():
    """Criar usuário admin."""
    print("Criando usuário admin...")
    
    async with AsyncSessionLocal() as db:
        user = User(
            email="fabio@fcsolucoes.com",
            hashed_password=get_password_hash("1234"),
            nome="Fabio",
            role="admin",
            ativo=True
        )
        db.add(user)
        await db.commit()
        print("✅ Usuário criado!")
        print("   Email: fabio@fcsolucoes.com")
        print("   Senha: 1234")

async def main():
    await init_database()
    await create_admin_user()
    print("\n🚀 Sistema pronto!")

if __name__ == "__main__":
    asyncio.run(main())
