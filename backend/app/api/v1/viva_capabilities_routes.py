from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.api.v1.viva_schemas import VivaCapabilitiesResponse
from app.models.user import User
from app.services.viva_capabilities_service import viva_capabilities_service

router = APIRouter()


@router.get("/capabilities", response_model=VivaCapabilitiesResponse)
async def get_capabilities(
    current_user: User = Depends(get_current_user),
):
    return VivaCapabilitiesResponse(items=viva_capabilities_service.get_capabilities())
