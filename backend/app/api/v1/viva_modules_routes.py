from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.api.v1.viva_schemas import VivaModulesStatusResponse
from app.models.user import User
from app.services.viva_modules_service import viva_modules_service

router = APIRouter()


@router.get("/modules/status", response_model=VivaModulesStatusResponse)
async def get_modules_status(
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    payload = viva_modules_service.get_modules_status()
    return VivaModulesStatusResponse(**payload)

