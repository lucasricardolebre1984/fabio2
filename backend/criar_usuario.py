"""Script simples para criar usuário admin."""
import asyncio
import sys

sys.path.insert(0, '.')

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def create_user():
    async with AsyncSessionLocal() as db:
        # Verificar se usuário já existe
        result = await db.execute(
            select(User).where(User.email == "fabio@fcsolucoes.com")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("⚠️  Usuário já existe!")
            print("   📧 fabio@fcsolucoes.com")
            return
        
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
        print("   📧 Email: fabio@fcsolucoes.com")
        print("   🔑 Senha: 1234")

if __name__ == "__main__":
    asyncio.run(create_user())
