"""Criar usuário via SQL direto - workaround para bcrypt."""
import asyncio
import sys

sys.path.insert(0, '.')

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Hash de '1234' gerado previamente
HASH_SENHA = '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'

DATABASE_URL = "postgresql+asyncpg://fabio2_user:fabio2_pass@localhost:5432/fabio2"

async def criar_usuario():
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.begin() as conn:
        # Verificar se usuário já existe
        result = await conn.execute(
            text("SELECT id FROM users WHERE email = 'fabio@fcsolucoes.com'")
        )
        existing = result.fetchone()
        
        if existing:
            print("⚠️  Usuário já existe!")
            print("   📧 fabio@fcsolucoes.com")
            return
        
        # Inserir usuário
        await conn.execute(text(f"""
            INSERT INTO users (id, email, hashed_password, nome, role, ativo, created_at)
            VALUES (
                gen_random_uuid(),
                'fabio@fcsolucoes.com',
                '{HASH_SENHA}',
                'Fabio',
                'ADMIN',
                true,
                NOW()
            )
        """))
        
    print("✅ Usuário criado com sucesso!")
    print("   📧 Email: fabio@fcsolucoes.com")
    print("   🔑 Senha: 1234")

if __name__ == "__main__":
    asyncio.run(criar_usuario())
