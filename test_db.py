import asyncpg
import asyncio

async def test():
    try:
        conn = await asyncpg.connect("postgresql://fabio2_prod:Fabio2@Secure2026!@172.18.0.3:5432/fabio2_prod")
        result = await conn.fetch("SELECT 1")
        print(f"Success: {result}")
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
