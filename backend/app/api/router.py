"""Main API router."""
from fastapi import APIRouter

from app.api.v1 import auth, contratos, clientes, agenda, whatsapp

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(contratos.router, prefix="/contratos", tags=["Contratos"])
api_router.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
api_router.include_router(agenda.router, prefix="/agenda", tags=["Agenda"])
api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp"])
