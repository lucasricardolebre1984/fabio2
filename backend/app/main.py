"""Main FastAPI application."""
import contextlib
from contextlib import asynccontextmanager
import asyncio
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.router import api_router
from app.core.logging import setup_logging
from app.db.session import AsyncSessionLocal
from app.services.viva_handoff_service import viva_handoff_service
from app.services.viva_brain_paths_service import viva_brain_paths_service
from app.services.viva_memory_service import viva_memory_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging()
    
    # Create storage directory if not exists
    os.makedirs(settings.STORAGE_LOCAL_PATH, exist_ok=True)
    viva_brain_paths_service.ensure_runtime_dirs()

    is_vercel = os.getenv("VERCEL") == "1"

    # Pre-flight memory backends (pgvector + redis) without crashing startup.
    try:
        async with AsyncSessionLocal() as db:
            await viva_memory_service.ensure_storage(db)
    except Exception:
        pass

    stop_event = asyncio.Event()
    worker_task = None

    if not is_vercel:
        async def handoff_worker() -> None:
            while not stop_event.is_set():
                try:
                    async with AsyncSessionLocal() as db:
                        await viva_handoff_service.process_due_tasks(db=db, limit=20)
                except Exception:
                    # Keep server up even if handoff has a transient failure.
                    pass
                try:
                    await asyncio.wait_for(stop_event.wait(), timeout=30)
                except asyncio.TimeoutError:
                    continue

        worker_task = asyncio.create_task(handoff_worker())
    
    yield
    
    # Shutdown
    stop_event.set()
    if worker_task is not None:
        worker_task.cancel()
        with contextlib.suppress(Exception):
            await worker_task


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
