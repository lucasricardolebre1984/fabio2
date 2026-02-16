from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.cofre_memory_service import cofre_memory_service
from app.services.cofre_manifest_service import cofre_manifest_service
from app.services.cofre_schema_service import cofre_schema_service
from app.services.viva_brain_paths_service import viva_brain_paths_service
from app.services.viva_memory_service import viva_memory_service
from sqlalchemy import text

router = APIRouter()


@router.get("/memories/status")
async def cofre_memory_status(
    session_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    try:
        viva_status = await viva_memory_service.memory_status(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
        )
        tables = cofre_memory_service.list_tables()
        return {
            "cofre_root": str(viva_brain_paths_service.root_dir),
            "tables": tables,
            "viva_memory": viva_status,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar COFRE: {str(exc)}")


@router.get("/memories/tables")
async def cofre_memory_tables(
    current_user: User = Depends(get_current_user),
) -> Dict[str, List[str]]:
    _ = current_user
    return {"tables": cofre_memory_service.list_tables()}


@router.get("/memories/{table_name}/tail")
async def cofre_memory_table_tail(
    table_name: str,
    limit: int = Query(default=80, ge=1, le=300),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user
    try:
        items = cofre_memory_service.tail_table(table_name=table_name, limit=limit)
        return {"table": table_name, "total": len(items), "items": items}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar tabela COFRE: {str(exc)}")


@router.post("/memories/sync-db-tables")
async def cofre_memory_sync_db_tables(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    _ = current_user
    try:
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

        created_dirs: List[str] = []
        for table_name in table_names:
            created_dirs.append(cofre_memory_service.ensure_table_dir(table_name))

        return {
            "total_tables": len(table_names),
            "tables": table_names,
            "cofre_dirs": sorted(set(created_dirs)),
            "cofre_root": str(viva_brain_paths_service.root_dir),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao sincronizar tabelas no COFRE: {str(exc)}")


@router.get("/system/manifest")
async def cofre_system_manifest(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user
    data = cofre_manifest_service.load_manifest()
    return {
        "cofre_root": str(viva_brain_paths_service.root_dir),
        "manifest": data,
    }


@router.get("/system/schema-status")
async def cofre_system_schema_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    _ = current_user
    await cofre_schema_service.ensure_tables(db)
    queries = {
        "cofre_persona_registry": "SELECT COUNT(*) AS total FROM cofre_persona_registry",
        "cofre_skill_registry": "SELECT COUNT(*) AS total FROM cofre_skill_registry",
        "cofre_memory_registry": "SELECT COUNT(*) AS total FROM cofre_memory_registry",
        "cofre_manifest_registry": "SELECT COUNT(*) AS total FROM cofre_manifest_registry",
    }
    counts: Dict[str, int] = {}
    for key, sql in queries.items():
        result = await db.execute(text(sql))
        counts[key] = int(result.scalar() or 0)
    return {
        "cofre_root": str(viva_brain_paths_service.root_dir),
        "counts": counts,
    }
