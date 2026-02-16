from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.cofre_memory_service import cofre_memory_service
from app.services.viva_brain_paths_service import viva_brain_paths_service
from app.services.viva_memory_service import viva_memory_service

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
