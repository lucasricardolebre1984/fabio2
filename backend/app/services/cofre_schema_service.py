"""COFRE schema governance service.

Creates institutional metadata tables and keeps COFRE memory dirs in sync
with database tables.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
from typing import Dict, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.cofre_manifest_service import cofre_manifest_service
from app.services.cofre_memory_service import cofre_memory_service
from app.services.viva_brain_paths_service import viva_brain_paths_service


class CofreSchemaService:
    async def ensure_tables(self, db: AsyncSession) -> None:
        await db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS cofre_persona_registry (
                    id SERIAL PRIMARY KEY,
                    file_name VARCHAR(255) NOT NULL,
                    file_path TEXT NOT NULL,
                    sha256 VARCHAR(64) NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (file_path)
                )
                """
            )
        )
        await db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS cofre_skill_registry (
                    id SERIAL PRIMARY KEY,
                    skill_name VARCHAR(255) NOT NULL,
                    file_name VARCHAR(255) NOT NULL,
                    file_path TEXT NOT NULL,
                    sha256 VARCHAR(64) NOT NULL,
                    active BOOLEAN NOT NULL DEFAULT TRUE,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (file_path)
                )
                """
            )
        )
        await db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS cofre_memory_registry (
                    id SERIAL PRIMARY KEY,
                    table_name VARCHAR(255) NOT NULL,
                    cofre_dir TEXT NOT NULL,
                    active BOOLEAN NOT NULL DEFAULT TRUE,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (table_name)
                )
                """
            )
        )
        await db.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS cofre_manifest_registry (
                    id SERIAL PRIMARY KEY,
                    manifest_path TEXT NOT NULL,
                    version VARCHAR(64),
                    sha256 VARCHAR(64) NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (manifest_path)
                )
                """
            )
        )

    @staticmethod
    def _sha256(path: Path) -> str:
        data = path.read_bytes()
        return hashlib.sha256(data).hexdigest()

    async def sync_persona_and_skills(self, db: AsyncSession) -> Dict[str, int]:
        persona_dir = viva_brain_paths_service.persona_skills_dir
        upserted_persona = 0
        upserted_skills = 0
        persona_files = [
            viva_brain_paths_service.viva_agent_file,
            viva_brain_paths_service.viviane_agent_file,
        ]

        for persona_file in persona_files:
            if not persona_file.exists():
                continue
            await db.execute(
                text(
                    """
                    INSERT INTO cofre_persona_registry (file_name, file_path, sha256, updated_at)
                    VALUES (:file_name, :file_path, :sha256, NOW())
                    ON CONFLICT (file_path) DO UPDATE
                    SET file_name = EXCLUDED.file_name,
                        sha256 = EXCLUDED.sha256,
                        updated_at = NOW()
                    """
                ),
                {
                    "file_name": persona_file.name,
                    "file_path": str(persona_file),
                    "sha256": self._sha256(persona_file),
                },
            )
            upserted_persona += 1

        for skill_file in sorted(persona_dir.glob("**/*.md")):
            if skill_file.name.lower() == "agent.md":
                continue
            await db.execute(
                text(
                    """
                    INSERT INTO cofre_skill_registry (skill_name, file_name, file_path, sha256, active, updated_at)
                    VALUES (:skill_name, :file_name, :file_path, :sha256, TRUE, NOW())
                    ON CONFLICT (file_path) DO UPDATE
                    SET skill_name = EXCLUDED.skill_name,
                        file_name = EXCLUDED.file_name,
                        sha256 = EXCLUDED.sha256,
                        active = TRUE,
                        updated_at = NOW()
                    """
                ),
                {
                    "skill_name": skill_file.stem,
                    "file_name": skill_file.name,
                    "file_path": str(skill_file),
                    "sha256": self._sha256(skill_file),
                },
            )
            upserted_skills += 1

        return {"persona": upserted_persona, "skills": upserted_skills}

    async def sync_memory_registry(self, db: AsyncSession) -> Dict[str, int]:
        result = await db.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
                """
            )
        )
        table_names = [str(row.table_name) for row in result.fetchall()]
        upserted = 0
        for table_name in table_names:
            cofre_dir = cofre_memory_service.ensure_table_dir(table_name)
            await db.execute(
                text(
                    """
                    INSERT INTO cofre_memory_registry (table_name, cofre_dir, active, updated_at)
                    VALUES (:table_name, :cofre_dir, TRUE, NOW())
                    ON CONFLICT (table_name) DO UPDATE
                    SET cofre_dir = EXCLUDED.cofre_dir,
                        active = TRUE,
                        updated_at = NOW()
                    """
                ),
                {
                    "table_name": table_name,
                    "cofre_dir": str(viva_brain_paths_service.memories_dir / cofre_dir),
                },
            )
            upserted += 1
        return {"tables": upserted}

    async def sync_manifest_registry(self, db: AsyncSession) -> Dict[str, int]:
        manifest = cofre_manifest_service.load_manifest()
        manifest_path = viva_brain_paths_service.root_dir / "system" / "endpoints_manifest.json"
        if not manifest_path.exists():
            return {"manifest": 0}
        await db.execute(
            text(
                """
                INSERT INTO cofre_manifest_registry (manifest_path, version, sha256, updated_at)
                VALUES (:manifest_path, :version, :sha256, NOW())
                ON CONFLICT (manifest_path) DO UPDATE
                SET version = EXCLUDED.version,
                    sha256 = EXCLUDED.sha256,
                    updated_at = NOW()
                """
            ),
            {
                "manifest_path": str(manifest_path),
                "version": str(manifest.get("version") or ""),
                "sha256": self._sha256(manifest_path),
            },
        )
        return {"manifest": 1}

    async def bootstrap(self, db: AsyncSession) -> Dict[str, Dict[str, int]]:
        await self.ensure_tables(db)
        persona_skills = await self.sync_persona_and_skills(db)
        memory = await self.sync_memory_registry(db)
        manifest = await self.sync_manifest_registry(db)
        return {"persona_skills": persona_skills, "memory": memory, "manifest": manifest}


cofre_schema_service = CofreSchemaService()
