"""WhatsApp service - Integration with Evolution API."""
from datetime import datetime
import unicodedata
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings


class WhatsAppService:
    """Service for WhatsApp integration via Evolution API."""

    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL.rstrip("/")
        self.api_key = settings.EVOLUTION_API_KEY
        self.instance_name = settings.WA_INSTANCE_NAME
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json",
        }

    def _auth_candidates(self) -> List[str]:
        """Auth candidates for dev/prod compatibility."""
        keys = [self.api_key, "default_key", "dev_evolution_key", "default_key_change_in_production"]
        unique: List[str] = []
        for key in keys:
            if key and key not in unique:
                unique.append(key)
        return unique

    async def _request(
        self,
        client: httpx.AsyncClient,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        timeout: float = 10.0,
    ) -> httpx.Response:
        """Request helper with API key fallback when Evolution returns 401."""
        last_response: Optional[httpx.Response] = None
        for key in self._auth_candidates():
            headers = {"apikey": key, "Content-Type": "application/json"}
            response = await client.request(
                method=method,
                url=f"{self.base_url}{path}",
                headers=headers,
                json=json,
                timeout=timeout,
            )
            last_response = response
            if response.status_code != 401:
                self.headers = headers
                return response
        assert last_response is not None
        return last_response

    def _normalize_instances_payload(self, data: Any) -> List[Dict[str, Any]]:
        """Normalize fetchInstances payload across Evolution versions."""
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            return [data]
        return []

    def _map_instance_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Map instance row from old/new Evolution contracts."""
        nested = item.get("instance") if isinstance(item.get("instance"), dict) else {}

        name = item.get("name") or nested.get("instanceName")
        status = (
            item.get("connectionStatus")
            or item.get("status")
            or nested.get("status")
            or nested.get("state")
        )
        number = item.get("number")
        profile_name = item.get("profileName") or nested.get("profileName")
        owner_jid = item.get("ownerJid") or nested.get("owner")

        return {
            "name": name,
            "status": status,
            "number": number,
            "profile_name": profile_name,
            "owner_jid": owner_jid,
        }

    async def _fetch_instances(self, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """Fetch available instances from Evolution."""
        try:
            response = await self._request(client, "GET", "/instance/fetchInstances", timeout=10.0)
            if response.status_code != 200:
                return []
            raw = self._normalize_instances_payload(response.json())
            mapped = [self._map_instance_item(item) for item in raw]
            return [item for item in mapped if item.get("name")]
        except Exception:
            return []

    def _resolve_instance_name(self, instances: List[Dict[str, Any]]) -> str:
        """Resolve effective instance name from config and available instances."""
        configured = self.instance_name
        if not instances:
            return configured

        names = [item.get("name") for item in instances if item.get("name")]
        open_names = [
            item["name"]
            for item in instances
            if item.get("name") and str(item.get("status", "")).lower() in {"open", "connected", "online"}
        ]

        if configured in names:
            return configured
        if len(open_names) == 1:
            return open_names[0]
        if len(names) == 1:
            return names[0]
        return configured

    def _extract_state(self, payload: Any) -> Optional[str]:
        """Extract connection state from old/new Evolution connection payloads."""
        if not isinstance(payload, dict):
            return None
        instance_data = payload.get("instance")
        if isinstance(instance_data, dict):
            state = instance_data.get("state") or instance_data.get("status")
            if state:
                return str(state)
        state = payload.get("state") or payload.get("status")
        return str(state) if state else None

    def _extract_qr_code(self, payload: Any) -> Optional[str]:
        """Extract qr/base64/pairing code from connect payload."""
        if not isinstance(payload, dict):
            return None

        direct_keys = ["base64", "qrcode", "code", "qrCode", "pairingCode", "pairing_code"]
        for key in direct_keys:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        nested = payload.get("qrcode")
        if isinstance(nested, dict):
            for key in ["base64", "code", "qr", "pairingCode", "pairing_code"]:
                value = nested.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()

        return None

    def _find_instance(self, instances: List[Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
        for item in instances:
            if item.get("name") == name:
                return item
        return None

    async def get_status(self) -> Dict[str, Any]:
        """Get WhatsApp connection status."""
        async with httpx.AsyncClient() as client:
            try:
                instances = await self._fetch_instances(client)
                instance = self._resolve_instance_name(instances)
                response = await self._request(
                    client,
                    "GET",
                    f"/instance/connectionState/{instance}",
                    timeout=10.0,
                )

                if response.status_code == 200:
                    state = self._extract_state(response.json())
                    details = self._find_instance(instances, instance) or {}
                    owner = details.get("owner_jid")
                    numero_owner = owner.split("@")[0] if isinstance(owner, str) and "@" in owner else owner
                    numero = details.get("number") or numero_owner
                    nome_perfil = details.get("profile_name")
                    return {
                        "conectado": str(state).lower() == "open",
                        "estado": state,
                        "numero": numero,
                        "nome_perfil": nome_perfil,
                        "instance_name": instance,
                    }

                if response.status_code == 404:
                    return {
                        "conectado": False,
                        "erro": "Instancia nao encontrada",
                        "instance_name": instance,
                        "instance_name_configurada": self.instance_name,
                        "instances_disponiveis": [item["name"] for item in instances if item.get("name")],
                    }

                return {
                    "conectado": False,
                    "erro": f"Status {response.status_code}",
                    "instance_name": instance,
                }
            except Exception as e:
                return {
                    "conectado": False,
                    "erro": str(e),
                    "instance_name": self.instance_name,
                }

    async def connect(self) -> Dict[str, Any]:
        """Start WhatsApp connection (returns QR code when available)."""
        async with httpx.AsyncClient() as client:
            try:
                instances = await self._fetch_instances(client)
                if not instances:
                    return {
                        "sucesso": False,
                        "erro": "Nenhuma instancia cadastrada no Evolution Manager",
                        "instance_name": self.instance_name,
                    }

                instance = self._resolve_instance_name(instances)
                names = [item["name"] for item in instances if item.get("name")]
                if instance not in names and len(names) == 1:
                    instance = names[0]
                elif instance not in names:
                    return {
                        "sucesso": False,
                        "erro": "Instancia configurada nao encontrada",
                        "instance_name": self.instance_name,
                        "instances_disponiveis": names,
                    }

                state_resp = await self._request(
                    client,
                    "GET",
                    f"/instance/connectionState/{instance}",
                    timeout=10.0,
                )
                if state_resp.status_code == 200:
                    current_state = self._extract_state(state_resp.json())
                    if str(current_state).lower() == "open":
                        return {
                            "sucesso": True,
                            "conectado": True,
                            "mensagem": "WhatsApp ja conectado",
                            "instance_name": instance,
                        }

                connect_response = await self._request(
                    client,
                    "GET",
                    f"/instance/connect/{instance}",
                    timeout=30.0,
                )
                if connect_response.status_code in [200, 201]:
                    payload: Dict[str, Any] = {}
                    try:
                        payload = connect_response.json()
                    except Exception:
                        payload = {}

                    qr_code = self._extract_qr_code(payload)
                    if qr_code:
                        return {
                            "sucesso": True,
                            "conectado": False,
                            "qr_code": qr_code,
                            "mensagem": "Escaneie o QR Code com seu WhatsApp",
                            "instance_name": instance,
                        }

                    new_state = self._extract_state(payload)
                    if str(new_state).lower() == "open":
                        return {
                            "sucesso": True,
                            "conectado": True,
                            "mensagem": "WhatsApp conectado",
                            "instance_name": instance,
                        }

                    return {
                        "sucesso": True,
                        "conectado": False,
                        "mensagem": "Conexao iniciada. Aguarde o QR Code no Evolution Manager",
                        "instance_name": instance,
                    }

                return {
                    "sucesso": False,
                    "erro": f"Status {connect_response.status_code}: {connect_response.text}",
                    "instance_name": instance,
                }
            except Exception as e:
                return {
                    "sucesso": False,
                    "erro": str(e),
                    "instance_name": self.instance_name,
                }

    async def disconnect(self) -> Dict[str, Any]:
        """Disconnect WhatsApp."""
        async with httpx.AsyncClient() as client:
            try:
                instances = await self._fetch_instances(client)
                instance = self._resolve_instance_name(instances)
                response = await self._request(
                    client,
                    "DELETE",
                    f"/instance/logout/{instance}",
                    timeout=10.0,
                )

                if response.status_code in [200, 201]:
                    return {
                        "sucesso": True,
                        "mensagem": "Desconectado com sucesso",
                        "instance_name": instance,
                    }

                return {
                    "sucesso": False,
                    "erro": f"Status {response.status_code}: {response.text}",
                    "instance_name": instance,
                }
            except Exception as e:
                return {
                    "sucesso": False,
                    "erro": str(e),
                    "instance_name": self.instance_name,
                }

    async def send_text(
        self,
        numero: str,
        mensagem: str,
        context_push_name: Optional[str] = None,
        context_preferred_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send text message."""
        mensagem = mensagem.strip() if isinstance(mensagem, str) else ""
        if not mensagem:
            return {
                "sucesso": False,
                "erro": "Mensagem vazia para envio",
                "instance_name": self.instance_name,
            }

        destino_original = str(numero or "").strip()
        numero = self._format_number(destino_original)

        async with httpx.AsyncClient() as client:
            try:
                instances = await self._fetch_instances(client)
                instance = self._resolve_instance_name(instances)
                numero_resolvido = await self._resolve_lid_number(
                    client=client,
                    instance=instance,
                    numero=numero,
                    context_push_name=context_push_name,
                    context_preferred_number=context_preferred_number,
                )
                if numero_resolvido:
                    numero = numero_resolvido
                elif isinstance(numero, str) and numero.lower().endswith("@lid"):
                    return {
                        "sucesso": False,
                        "erro": "Destino @lid sem numero resolvido. Aguardando bind do WhatsApp real.",
                        "erro_codigo": "lid_unresolved",
                        "instance_name": instance,
                        "destino": numero,
                        "destino_original": destino_original,
                    }

                payload = {
                    "number": numero,
                    "text": mensagem,
                }
                response = await self._request(
                    client,
                    "POST",
                    f"/message/sendText/{instance}",
                    json=payload,
                    timeout=30.0,
                )

                if response.status_code in [400, 422]:
                    error_text = (response.text or "").lower()
                    should_try_legacy = (
                        "text is required" in error_text
                        or "textmessage" in error_text
                        or "text message" in error_text
                    )
                    if should_try_legacy:
                        legacy_payload = {
                            "number": numero,
                            "textMessage": {"text": mensagem},
                        }
                        legacy_response = await self._request(
                            client,
                            "POST",
                            f"/message/sendText/{instance}",
                            json=legacy_payload,
                            timeout=30.0,
                        )
                        if legacy_response.status_code in [200, 201]:
                            response = legacy_response

                if response.status_code in [200, 201]:
                    return {
                        "sucesso": True,
                        "mensagem": "Mensagem enviada com sucesso",
                        "instance_name": instance,
                        "destino": numero,
                        "destino_original": destino_original,
                    }

                return {
                    "sucesso": False,
                    "erro": f"Status {response.status_code}: {response.text}",
                    "erro_codigo": "send_text_http_error",
                    "instance_name": instance,
                    "destino": numero,
                    "destino_original": destino_original,
                }
            except Exception as e:
                return {
                    "sucesso": False,
                    "erro": str(e),
                    "erro_codigo": "send_text_exception",
                    "instance_name": self.instance_name,
                    "destino": numero,
                    "destino_original": destino_original,
                }

    async def send_document(
        self,
        numero: str,
        documento_url: str,
        legenda: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send document/file."""
        numero = self._format_number(numero)

        async with httpx.AsyncClient() as client:
            try:
                instances = await self._fetch_instances(client)
                instance = self._resolve_instance_name(instances)
                payload = {
                    "number": numero,
                    "mediatype": "document",
                    "fileName": documento_url.split("/")[-1],
                    "caption": legenda or "",
                    "media": documento_url,
                }
                response = await self._request(
                    client,
                    "POST",
                    f"/message/sendMedia/{instance}",
                    json=payload,
                    timeout=60.0,
                )

                if response.status_code in [400, 422]:
                    legacy_payload = {
                        "number": numero,
                        "mediaMessage": {
                            "mediatype": "document",
                            "fileName": documento_url.split("/")[-1],
                            "caption": legenda or "",
                            "media": documento_url,
                        },
                    }
                    legacy_response = await self._request(
                        client,
                        "POST",
                        f"/message/sendMedia/{instance}",
                        json=legacy_payload,
                        timeout=60.0,
                    )
                    if legacy_response.status_code in [200, 201]:
                        response = legacy_response

                if response.status_code in [200, 201]:
                    return {
                        "sucesso": True,
                        "mensagem": "Documento enviado com sucesso",
                        "instance_name": instance,
                    }

                return {
                    "sucesso": False,
                    "erro": f"Status {response.status_code}: {response.text}",
                    "instance_name": instance,
                }
            except Exception as e:
                return {
                    "sucesso": False,
                    "erro": str(e),
                    "instance_name": self.instance_name,
                }

    def _extract_media_base64(self, payload: Any) -> Optional[str]:
        """Extract media base64 from different Evolution payload contracts."""
        if isinstance(payload, str) and payload.strip():
            return payload.strip()

        if not isinstance(payload, dict):
            return None

        direct_keys = ("base64", "data", "media", "file", "content", "buffer")
        for key in direct_keys:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        nested_keys = ("message", "response", "result", "data")
        for key in nested_keys:
            value = payload.get(key)
            if isinstance(value, dict):
                nested = self._extract_media_base64(value)
                if nested:
                    return nested

        return None

    async def get_media_base64(
        self,
        message_payload: Dict[str, Any],
        instance_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch media base64 from Evolution chat endpoint for a message payload."""
        async with httpx.AsyncClient() as client:
            try:
                instances = await self._fetch_instances(client)
                instance = (
                    instance_name
                    if instance_name
                    else self._resolve_instance_name(instances)
                )
                if not instance:
                    return {
                        "sucesso": False,
                        "erro": "Instancia nao resolvida para buscar midia",
                        "instance_name": self.instance_name,
                    }

                key = (
                    message_payload.get("key")
                    if isinstance(message_payload.get("key"), dict)
                    else {}
                )
                inner_message = (
                    message_payload.get("message")
                    if isinstance(message_payload.get("message"), dict)
                    else None
                )

                request_candidates: List[Dict[str, Any]] = [
                    {"message": message_payload},
                ]

                if key and inner_message:
                    request_candidates.append(
                        {"message": {"key": key, "message": inner_message}}
                    )

                if key and not inner_message:
                    request_candidates.append(
                        {"message": {"key": key, "message": message_payload}}
                    )

                last_error: Optional[str] = None
                for candidate in request_candidates:
                    response = await self._request(
                        client,
                        "POST",
                        f"/chat/getBase64FromMediaMessage/{instance}",
                        json=candidate,
                        timeout=30.0,
                    )
                    if response.status_code not in [200, 201]:
                        last_error = f"Status {response.status_code}: {response.text}"
                        continue

                    payload: Any = {}
                    try:
                        payload = response.json()
                    except Exception:
                        payload = response.text

                    media_base64 = self._extract_media_base64(payload)
                    if media_base64:
                        return {
                            "sucesso": True,
                            "base64": media_base64,
                            "instance_name": instance,
                        }

                return {
                    "sucesso": False,
                    "erro": last_error or "Nao foi possivel extrair base64 da midia",
                    "instance_name": instance,
                }
            except Exception as e:
                return {
                    "sucesso": False,
                    "erro": str(e),
                    "instance_name": instance_name or self.instance_name,
                }

    async def _fetch_contacts(
        self,
        client: httpx.AsyncClient,
        instance: str,
    ) -> List[Dict[str, Any]]:
        """Fetch contacts from Evolution chat module."""
        try:
            response = await self._request(
                client,
                "POST",
                f"/chat/findContacts/{instance}",
                json={},
                timeout=20.0,
            )
            if response.status_code != 200:
                return []
            payload = response.json()
            if isinstance(payload, list):
                return [item for item in payload if isinstance(item, dict)]
            return []
        except Exception:
            return []

    def _normalizar_nome(self, nome: Optional[str]) -> str:
        if not isinstance(nome, str):
            return ""
        value = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
        return " ".join(value.lower().split())

    def _extrair_numero_de_jid(self, jid: str) -> Optional[str]:
        if not isinstance(jid, str) or "@" not in jid:
            return None
        numero = "".join(filter(str.isdigit, jid.split("@")[0]))
        return numero if numero else None

    def _is_plausible_phone_number(self, numero: str) -> bool:
        if not isinstance(numero, str):
            return False
        if numero.lower().endswith("@lid"):
            return False
        digits = "".join(filter(str.isdigit, numero))
        return 10 <= len(digits) <= 15

    async def _check_whatsapp_number(
        self,
        client: httpx.AsyncClient,
        instance: str,
        numero: str,
    ) -> Optional[str]:
        """Validate candidate number with Evolution and return deliverable digits."""
        formatted = self._format_number(numero)
        if not self._is_plausible_phone_number(formatted):
            return None
        try:
            response = await self._request(
                client,
                "POST",
                f"/chat/whatsappNumbers/{instance}",
                json={"numbers": [formatted]},
                timeout=10.0,
            )
            if response.status_code != 200:
                return None

            payload = response.json()
            if not isinstance(payload, list) or not payload:
                return None
            row = payload[0] if isinstance(payload[0], dict) else {}
            if not row.get("exists"):
                return None

            numero_row = "".join(filter(str.isdigit, str(row.get("number") or "")))
            if self._is_plausible_phone_number(numero_row):
                return numero_row

            jid_row = str(row.get("jid") or "")
            from_jid = self._extrair_numero_de_jid(jid_row)
            if from_jid and self._is_plausible_phone_number(from_jid):
                return from_jid
            return None
        except Exception:
            return None

    async def _fetch_chats(
        self,
        client: httpx.AsyncClient,
        instance: str,
    ) -> List[Dict[str, Any]]:
        """Fetch chats from Evolution chat module."""
        try:
            response = await self._request(
                client,
                "POST",
                f"/chat/findChats/{instance}",
                json={},
                timeout=20.0,
            )
            if response.status_code != 200:
                return []
            payload = response.json()
            if isinstance(payload, list):
                return [item for item in payload if isinstance(item, dict)]
            return []
        except Exception:
            return []

    def _parse_iso_datetime(self, value: Any) -> Optional[datetime]:
        if not isinstance(value, str) or not value.strip():
            return None
        text = value.strip().replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(text)
        except Exception:
            return None

    def _name_similarity_score(self, base_name: str, candidate_name: str) -> int:
        base = self._normalizar_nome(base_name)
        candidate = self._normalizar_nome(candidate_name)
        if not base or not candidate:
            return 0
        if base == candidate:
            return 100
        if base in candidate or candidate in base:
            return 80
        base_tokens = {token for token in base.split(" ") if len(token) >= 3}
        candidate_tokens = {token for token in candidate.split(" ") if len(token) >= 3}
        if not base_tokens or not candidate_tokens:
            return 0
        overlap = len(base_tokens.intersection(candidate_tokens))
        if overlap == 0:
            return 0
        return overlap * 20

    async def _resolve_lid_number(
        self,
        client: httpx.AsyncClient,
        instance: str,
        numero: str,
        context_push_name: Optional[str],
        context_preferred_number: Optional[str],
    ) -> Optional[str]:
        """Try to map @lid identifier to a deliverable phone number."""
        if not isinstance(numero, str) or not numero.lower().endswith("@lid"):
            return None

        candidate_numbers: List[str] = []
        preferred = self._format_number(context_preferred_number or "")
        if self._is_plausible_phone_number(preferred):
            candidate_numbers.append(preferred)

        contacts = await self._fetch_contacts(client, instance)
        current_contact = next(
            (
                item
                for item in contacts
                if str(item.get("remoteJid", "")).lower() == numero.lower()
            ),
            None,
        )
        for alt_key in ("remoteJidAlt", "remoteJidAlternative", "jidAlt"):
            if current_contact and isinstance(current_contact.get(alt_key), str):
                numero_alt = self._extrair_numero_de_jid(current_contact.get(alt_key))
                if numero_alt and self._is_plausible_phone_number(numero_alt):
                    candidate_numbers.append(numero_alt)

        # Nao usar heuristica de nome/foto para converter @lid.
        # Esse "chute" pode redirecionar mensagem para outro cliente com nome parecido.
        # Para @lid, aceitamos apenas origem explicita/confiavel:
        # - numero preferencial validado no contexto
        # - metadado alternativo vindo do proprio evento/contato

        unique_candidates: List[str] = []
        for candidate in candidate_numbers:
            normalized = "".join(filter(str.isdigit, str(candidate or "")))
            if not normalized or normalized in unique_candidates:
                continue
            unique_candidates.append(normalized)

        for candidate in unique_candidates:
            checked = await self._check_whatsapp_number(client, instance, candidate)
            if checked:
                return checked

        # Nao retornar fallback nao validado.
        # Em cenarios @lid, enviar para numero "chutado" aumenta falso negativo (exists:false)
        # e piora a taxa de entrega. Se nao validar, mantemos fluxo sem resolucao.
        return None

    def _format_number(self, numero: str) -> str:
        """Format phone number for WhatsApp API."""
        if not isinstance(numero, str):
            return ""
        numero = numero.strip()
        if numero.lower().endswith("@lid"):
            return numero
        if "@" in numero:
            numero = numero.split("@")[0]
        numero = "".join(filter(str.isdigit, numero))
        # Prefixa 55 apenas quando vier numero local (DDD + numero, sem pais).
        # Se ja vier internacional, preserva como chegou no webhook.
        if len(numero) <= 11 and not numero.startswith("55"):
            numero = "55" + numero
        return numero



