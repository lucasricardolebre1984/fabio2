import os

import asyncpg
import pytest


@pytest.mark.asyncio
async def test_database_connection_from_parts():
    """Optional connectivity smoke test using TEST_DB_* env vars."""
    host = os.getenv("TEST_DB_HOST")
    port = int(os.getenv("TEST_DB_PORT", "5432"))
    user = os.getenv("TEST_DB_USER")
    password = os.getenv("TEST_DB_PASSWORD")
    database = os.getenv("TEST_DB_NAME")

    if not all([host, user, password, database]):
        pytest.skip(
            "Set TEST_DB_HOST, TEST_DB_USER, TEST_DB_PASSWORD and TEST_DB_NAME "
            "to run this connectivity test."
        )

    conn = await asyncpg.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )
    try:
        result = await conn.fetchval("SELECT 1")
        assert result == 1
    finally:
        await conn.close()
