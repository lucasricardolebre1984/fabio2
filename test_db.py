import os

import asyncpg
import pytest


@pytest.mark.asyncio
async def test_database_connection_from_url():
    """Optional connectivity smoke test driven by TEST_DATABASE_URL env var."""
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("Set TEST_DATABASE_URL to run this connectivity test.")

    conn = await asyncpg.connect(database_url)
    try:
        result = await conn.fetchval("SELECT 1")
        assert result == 1
    finally:
        await conn.close()
