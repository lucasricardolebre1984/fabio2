"""VIVA router aggregator.

Mantem `viva.py` minimo e delega implementacao para `viva_core.py`.
"""

from fastapi import APIRouter

from app.api.v1.viva_core import router as viva_core_router
from app.api.v1.viva_campaign_routes import router as viva_campaign_router
from app.api.v1.viva_capabilities_routes import router as viva_capabilities_router
from app.api.v1.viva_chat_session_routes import router as viva_chat_session_router
from app.api.v1.viva_handoff_routes import router as viva_handoff_router
from app.api.v1.viva_media_routes import router as viva_media_router
from app.api.v1.viva_modules_routes import router as viva_modules_router

router = APIRouter()
router.include_router(viva_core_router)
router.include_router(viva_chat_session_router)
router.include_router(viva_capabilities_router)
router.include_router(viva_modules_router)
router.include_router(viva_handoff_router)
router.include_router(viva_campaign_router)
router.include_router(viva_media_router)
