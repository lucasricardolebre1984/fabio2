"""
Capabilities catalog exposed by VIVA.
"""
from typing import Any, Dict, List

from app.services.cofre_manifest_service import cofre_manifest_service


class VivaCapabilitiesService:
    def get_capabilities(self) -> List[Dict[str, Any]]:
        items = cofre_manifest_service.capabilities()
        return items


viva_capabilities_service = VivaCapabilitiesService()
