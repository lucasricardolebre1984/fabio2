"""Main FastAPI application."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.router import api_router
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging()
    
    # Create storage directory if not exists
    import os
    os.makedirs(settings.STORAGE_LOCAL_PATH, exist_ok=True)
    
    yield
    
    # Shutdown
    pass


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="API para gestão de contratos da FC Soluções Financeiras",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Static files (storage)
    app.mount("/storage", StaticFiles(directory="storage"), name="storage")
    
    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": settings.VERSION}
    
    @app.get("/")
    async def root():
        return {
            "message": "FC Soluções Financeiras API",
            "version": settings.VERSION,
            "docs": "/docs"
        }
    
    return app


app = create_app()
