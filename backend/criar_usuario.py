"""Script para criar usuário admin."""
import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash

async def create_user():
    async with AsyncSessionLocal() as db:
        # Verificar se usuário já existe
        from sqlalchemy import select
        from app.models.user import User as UserModel
        result = await db.execute(
            select(UserModel).where(UserModel.email == "fabio@fcsolucoes.com")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("Usuário já existe!")
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
        print("Usuário criado com sucesso!")
        print("Email: fabio@fcsolucoes.com")
        print("Senha: 1234")

if __name__ == "__main__":
    asyncio.run(create_user())
