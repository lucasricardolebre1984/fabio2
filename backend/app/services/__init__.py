"""Services module."""
from app.services.extenso_service import ExtensoService
# from app.services.pdf_service import PDFService  # WeasyPrint disabled - GTK issue
from app.services.pdf_service_stub import PDFService  # Using stub
from app.services.contrato_service import ContratoService
from app.services.cliente_service import ClienteService
from app.services.agenda_service import AgendaService
from app.services.whatsapp_service import WhatsAppService

__all__ = [
    "ExtensoService",
    "PDFService", 
    "ContratoService",
    "ClienteService",
    "AgendaService",
    "WhatsAppService"
]
