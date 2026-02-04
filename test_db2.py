import asyncpg
import asyncio

async def test():
    try:
        # Tentando com parâmetros separados
        conn = await asyncpg.connect(
            host='172.18.0.3',
            port=5432,
            user='fabio2_prod',
            password='Fabio2@Secure2026!',
            database='fabio2_prod'
        )
        result = await conn.fetch("SELECT 1")
        print(f"Success: {result}")
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
