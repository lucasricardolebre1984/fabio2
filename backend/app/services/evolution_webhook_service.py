"""
Servico de Webhook para Evolution API.
Recebe mensagens do WhatsApp e integra com IA VIVA.
"""
import base64
from datetime import datetime
import logging
import re
from typing import Any, Dict, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cliente import Cliente
from app.models.whatsapp_conversa import (
    StatusConversa,
    TipoOrigem,
    WhatsappConversa,
    WhatsappMensagem,
)
from app.services.viva_ia_service import viva_service
from app.services.viva_model_service import viva_model_service
from app.services.whatsapp_service import WhatsAppService


class EvolutionWebhookService:
    """Processa webhooks recebidos do Evolution Manager."""

    @staticmethod
    def _normalizar_evento(event_type: Any) -> str:
        """Normaliza evento para formato canônico (ex.: messages.upsert)."""
        if not isinstance(event_type, str):
            return ""

        evento = event_type.strip()
        if not evento:
            return ""

        # Evolution costuma enviar eventos em UPPER_SNAKE_CASE (MESSAGES_UPSERT)
        if "_" in evento and "." not in evento:
            return evento.lower().replace("_", ".")

        return evento.lower()

    async def processar_webhook(
        self,
        data: Dict[str, Any],
        db: AsyncSession,
    ) -> bool:
        """Processa evento recebido do Evolution API."""
        event_type = data.get("event")
        evento_normalizado = self._normalizar_evento(event_type)

        if evento_normalizado == "messages.upsert":
            return await self._processar_mensagem(data, db)
        if evento_normalizado == "connection.update":
            return await self._processar_status_conexao(data, db)

        logging.info("Webhook ignorado: evento=%s", event_type)
        return True

    async def _processar_mensagem(
        self,
        data: Dict[str, Any],
        db: AsyncSession,
    ) -> bool:
        """Processa nova mensagem recebida."""
        try:
            payload_data = data.get("data", {})
            instance_name = self._extrair_instance_name(
                instance_data=data.get("instance"),
                payload_data=payload_data,
            )
            message_wrapper = self._extrair_message_wrapper(payload_data)
            if not message_wrapper:
                return True

            remote_jid = self._extrair_remote_jid(message_wrapper, payload_data)
            numero = self._extrair_numero(message_wrapper, payload_data)
            if not numero:
                return True

            message_id = (
                message_wrapper.get("key", {}).get("id")
                if isinstance(message_wrapper.get("key"), dict)
                else None
            )
            push_name = self._extrair_push_name(message_wrapper, payload_data)
            message_content = self._extrair_conteudo_mensagem(message_wrapper)

            tipo_midia: Optional[str] = None
            falha_transcricao_audio = False
            texto = self._extrair_texto_mensagem(message_content)

            if not texto and self._eh_audio_mensagem(message_content):
                tipo_midia = "audio"
                texto = await self._transcrever_audio_mensagem(
                    instance_name=instance_name,
                    message_wrapper=message_wrapper,
                    message_content=message_content,
                )
                if not texto:
                    texto = "[audio nao transcrito]"
                    falha_transcricao_audio = True

            if not texto:
                return True

            conversa = await self._get_ou_criar_conversa(
                numero=numero,
                instance_name=instance_name,
                nome_contato=push_name,
                db=db,
            )
            contexto_atual = conversa.contexto_ia if isinstance(conversa.contexto_ia, dict) else {}
            contexto_atual = await self._refresh_lid_resolution_context(
                db=db,
                conversa=conversa,
                push_name=push_name,
                texto_usuario=texto,
                remote_jid=remote_jid,
                contexto_atual=contexto_atual,
            )
            if contexto_atual.get("non_deliverable_number"):
                if isinstance(remote_jid, str) and remote_jid.lower().endswith("@lid"):
                    contexto = dict(contexto_atual)
                    contexto.pop("non_deliverable_number", None)
                    contexto.pop("non_deliverable_reason", None)
                    contexto.pop("non_deliverable_at", None)
                    conversa.contexto_ia = contexto
                    await db.commit()
                else:
                    logging.info(
                        "Numero marcado como nao entregavel, ignorando resposta automatica. numero=%s instance=%s",
                        numero,
                        instance_name,
                    )
                    return True

            msg_usuario = WhatsappMensagem(
                conversa_id=conversa.id,
                tipo_origem=TipoOrigem.USUARIO,
                conteudo=texto,
                message_id=message_id,
                tipo_midia=tipo_midia,
            )
            db.add(msg_usuario)

            conversa.ultima_mensagem_em = datetime.utcnow()
            await db.commit()

            if falha_transcricao_audio:
                resposta_ia = (
                    "Recebi seu audio, mas nao consegui transcrever agora. "
                    "Pode me enviar em texto ou em um audio mais curto para eu te ajudar?"
                )
            else:
                resposta_ia = await viva_service.processar_mensagem(
                    numero=numero,
                    mensagem=texto,
                    conversa=conversa,
                    db=db,
                )

            if not isinstance(resposta_ia, str) or not resposta_ia.strip():
                logging.warning(
                    "Resposta vazia da VIVA detectada, aplicando fallback. numero=%s instance=%s",
                    numero,
                    instance_name,
                )
                resposta_ia = (
                    "Perfeito, recebi sua mensagem. "
                    "Para eu te ajudar melhor, me confirma seu objetivo principal em uma frase."
                )

            wa_service = WhatsAppService()
            destino_envio = remote_jid or numero
            preferred_number = self._pick_preferred_number_from_context(contexto_atual)
            envio_result = await wa_service.send_text(
                numero=destino_envio,
                mensagem=resposta_ia,
                context_push_name=push_name,
                context_preferred_number=preferred_number,
            )
            enviado = bool(envio_result.get("sucesso"))
            erro_envio = None if enviado else envio_result.get("erro")

            msg_ia = WhatsappMensagem(
                conversa_id=conversa.id,
                tipo_origem=TipoOrigem.IA,
                conteudo=resposta_ia,
                enviada=enviado,
                erro=erro_envio,
            )
            db.add(msg_ia)

            destino_utilizado = str(envio_result.get("destino") or destino_envio or "")
            if (
                erro_envio
                and "\"exists\":false" in str(erro_envio).replace(" ", "").lower()
                and "@lid" not in destino_utilizado.lower()
            ):
                contexto = dict(conversa.contexto_ia or {})
                contexto["non_deliverable_number"] = True
                contexto["non_deliverable_reason"] = "exists_false"
                contexto["non_deliverable_at"] = datetime.utcnow().isoformat()
                conversa.contexto_ia = contexto

            await db.commit()

            return True
        except Exception as e:
            logging.exception("Erro ao processar mensagem webhook: %s", str(e))
            return False

    def _extrair_instance_name(
        self,
        instance_data: Any,
        payload_data: Dict[str, Any],
    ) -> str:
        if isinstance(instance_data, dict):
            for key in ("instanceName", "name", "instance"):
                value = instance_data.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        elif isinstance(instance_data, str) and instance_data.strip():
            return instance_data.strip()

        payload_instance = payload_data.get("instanceName")
        if isinstance(payload_instance, str) and payload_instance.strip():
            return payload_instance.strip()

        return "Teste"

    def _extrair_message_wrapper(self, payload_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not isinstance(payload_data, dict):
            return None

        if isinstance(payload_data.get("key"), dict):
            if isinstance(payload_data.get("message"), dict):
                return payload_data

            if any(
                key in payload_data
                for key in ("conversation", "extendedTextMessage", "imageMessage", "audioMessage")
            ):
                return {"key": payload_data.get("key"), "message": payload_data}

        message_data = payload_data.get("message")
        if isinstance(message_data, dict):
            if isinstance(message_data.get("key"), dict):
                return message_data

            if isinstance(payload_data.get("key"), dict):
                return {"key": payload_data.get("key"), "message": message_data}

        return None

    def _extrair_numero(self, message_wrapper: Dict[str, Any], payload_data: Dict[str, Any]) -> str:
        remote_jid = self._extrair_remote_jid(message_wrapper, payload_data)
        if not remote_jid:
            return ""
        return remote_jid.split("@")[0]

    def _extrair_remote_jid(self, message_wrapper: Dict[str, Any], payload_data: Dict[str, Any]) -> str:
        key_data = message_wrapper.get("key") if isinstance(message_wrapper.get("key"), dict) else {}
        remote_jid = key_data.get("remoteJid")

        if not remote_jid and isinstance(payload_data.get("key"), dict):
            remote_jid = payload_data.get("key", {}).get("remoteJid")

        if not isinstance(remote_jid, str) or "@" not in remote_jid:
            return ""

        return remote_jid

    def _extrair_push_name(self, message_wrapper: Dict[str, Any], payload_data: Dict[str, Any]) -> Optional[str]:
        for candidate in (
            message_wrapper.get("pushName"),
            payload_data.get("pushName") if isinstance(payload_data, dict) else None,
        ):
            if isinstance(candidate, str):
                name = candidate.strip()
                if name:
                    return name
        return None

    def _normalize_digits(self, value: Any) -> str:
        if not isinstance(value, str):
            return ""
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) <= 11 and not digits.startswith("55"):
            digits = "55" + digits
        return digits

    def _extract_phone_from_text(self, text: str) -> Optional[str]:
        if not isinstance(text, str):
            return None
        normalized = text.lower()
        if not any(token in normalized for token in ("whats", "whatsapp", "telefone", "celular", "fone", "numero")):
            return None
        candidates = re.findall(r"(?:\+?\d[\d\-\s\(\)]{9,}\d)", text)
        for candidate in candidates:
            normalized_digits = self._normalize_digits(candidate)
            if 12 <= len(normalized_digits) <= 13:
                return normalized_digits
        return None

    def _pick_preferred_number_from_context(self, context: Dict[str, Any]) -> Optional[str]:
        if not isinstance(context, dict):
            return None
        direct = self._normalize_digits(str(context.get("resolved_whatsapp_number") or ""))
        if direct:
            return direct
        lead = context.get("lead")
        if isinstance(lead, dict):
            lead_phone = self._normalize_digits(str(lead.get("telefone") or ""))
            if lead_phone:
                return lead_phone
        return None

    async def _resolve_phone_from_client_registry(
        self,
        db: AsyncSession,
        push_name: Optional[str],
    ) -> Optional[str]:
        if not isinstance(push_name, str):
            return None
        name = push_name.strip()
        if len(name) < 5:
            return None
        stmt = select(Cliente).where(Cliente.nome.ilike(name))
        result = await db.execute(stmt)
        matches = [item for item in result.scalars().all() if getattr(item, "telefone", None)]
        if len(matches) != 1:
            return None
        return self._normalize_digits(str(matches[0].telefone or ""))

    async def _refresh_lid_resolution_context(
        self,
        db: AsyncSession,
        conversa: WhatsappConversa,
        push_name: Optional[str],
        texto_usuario: str,
        remote_jid: str,
        contexto_atual: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not isinstance(remote_jid, str) or not remote_jid.lower().endswith("@lid"):
            return contexto_atual

        contexto = dict(contexto_atual or {})
        changed = False

        extracted_from_text = self._extract_phone_from_text(texto_usuario)
        if extracted_from_text and contexto.get("resolved_whatsapp_number") != extracted_from_text:
            contexto["resolved_whatsapp_number"] = extracted_from_text
            contexto["resolved_whatsapp_source"] = "user_text"
            changed = True

        if not contexto.get("resolved_whatsapp_number"):
            from_lead = self._pick_preferred_number_from_context(contexto)
            if from_lead:
                contexto["resolved_whatsapp_number"] = from_lead
                contexto["resolved_whatsapp_source"] = "lead_context"
                changed = True

        if not contexto.get("resolved_whatsapp_number"):
            from_registry = await self._resolve_phone_from_client_registry(db=db, push_name=push_name)
            if from_registry:
                contexto["resolved_whatsapp_number"] = from_registry
                contexto["resolved_whatsapp_source"] = "client_registry"
                changed = True

        if changed:
            conversa.contexto_ia = contexto
            await db.commit()
            await db.refresh(conversa)

        return contexto

    def _extrair_conteudo_mensagem(self, message_wrapper: Dict[str, Any]) -> Dict[str, Any]:
        raw_message = message_wrapper.get("message")
        if not isinstance(raw_message, dict):
            raw_message = message_wrapper

        return self._desembrulhar_mensagem(raw_message)

    def _desembrulhar_mensagem(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        current = message_data
        nested_keys = (
            "ephemeralMessage",
            "viewOnceMessage",
            "viewOnceMessageV2",
            "viewOnceMessageV2Extension",
            "documentWithCaptionMessage",
        )

        for _ in range(6):
            next_message: Optional[Dict[str, Any]] = None
            for nested_key in nested_keys:
                nested_obj = current.get(nested_key)
                if isinstance(nested_obj, dict) and isinstance(nested_obj.get("message"), dict):
                    next_message = nested_obj.get("message")
                    break

            if isinstance(next_message, dict):
                current = next_message
                continue

            break

        return current

    def _extrair_texto_mensagem(self, message_data: Dict[str, Any]) -> Optional[str]:
        """Extrai texto da mensagem do payload."""
        try:
            if "conversation" in message_data:
                return str(message_data["conversation"] or "").strip() or None

            if "extendedTextMessage" in message_data:
                text = message_data["extendedTextMessage"].get("text", "")
                return str(text).strip() or None

            if "imageMessage" in message_data:
                caption = message_data["imageMessage"].get("caption", "")
                return str(caption).strip() or "[imagem]"

            if "videoMessage" in message_data:
                caption = message_data["videoMessage"].get("caption", "")
                return str(caption).strip() or "[video]"

            if "buttonsResponseMessage" in message_data:
                text = message_data["buttonsResponseMessage"].get("selectedDisplayText", "")
                return str(text).strip() or None

            if "listResponseMessage" in message_data:
                title = message_data["listResponseMessage"].get("title", "")
                description = message_data["listResponseMessage"].get("description", "")
                merged = f"{title} {description}".strip()
                return merged or None

            return None
        except Exception:
            return None

    def _eh_audio_mensagem(self, message_data: Dict[str, Any]) -> bool:
        return isinstance(message_data.get("audioMessage"), dict)

    def _extrair_base64_audio_local(self, audio_data: Dict[str, Any]) -> Optional[str]:
        for key in ("base64", "data", "media", "file", "content"):
            value = audio_data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    def _decode_base64_bytes(self, base64_input: str) -> Optional[bytes]:
        if not base64_input:
            return None

        payload = base64_input.strip()
        if payload.lower().startswith("data:") and "," in payload:
            payload = payload.split(",", 1)[1]

        payload = payload.replace("\n", "").replace("\r", "").replace(" ", "")
        if not payload:
            return None

        remainder = len(payload) % 4
        if remainder:
            payload += "=" * (4 - remainder)

        try:
            return base64.b64decode(payload, validate=False)
        except Exception:
            return None

    def _build_audio_filename(self, message_wrapper: Dict[str, Any], mime_type: str) -> str:
        message_id = (
            message_wrapper.get("key", {}).get("id")
            if isinstance(message_wrapper.get("key"), dict)
            else None
        ) or "audio"
        safe_mime = mime_type.split(";")[0].strip().lower()
        ext_map = {
            "audio/ogg": "ogg",
            "audio/opus": "opus",
            "audio/mpeg": "mp3",
            "audio/mp4": "m4a",
            "audio/wav": "wav",
            "audio/x-wav": "wav",
            "audio/webm": "webm",
        }
        extension = ext_map.get(safe_mime, "ogg")
        return f"{message_id}.{extension}"

    async def _transcrever_audio_mensagem(
        self,
        instance_name: str,
        message_wrapper: Dict[str, Any],
        message_content: Dict[str, Any],
    ) -> Optional[str]:
        audio_data = message_content.get("audioMessage")
        if not isinstance(audio_data, dict):
            return None

        media_base64 = self._extrair_base64_audio_local(audio_data)
        if not media_base64:
            wa_service = WhatsAppService()
            media_result = await wa_service.get_media_base64(
                message_payload=message_wrapper,
                instance_name=instance_name,
            )
            if media_result.get("sucesso"):
                media_base64 = str(media_result.get("base64") or "").strip()
            else:
                logging.warning(
                    "Falha ao baixar audio para transcricao via Evolution: %s",
                    media_result.get("erro"),
                )

        if not media_base64:
            return None

        audio_bytes = self._decode_base64_bytes(media_base64)
        if not audio_bytes:
            return None

        mime_type = str(audio_data.get("mimetype") or "audio/ogg")
        filename = self._build_audio_filename(message_wrapper, mime_type)
        transcricao = await viva_model_service.audio_transcribe_bytes(
            audio_bytes=audio_bytes,
            filename=filename,
            content_type=mime_type,
        )
        texto = (transcricao or "").strip()
        texto_lower = texto.lower()
        if not texto or texto_lower.startswith("erro") or texto_lower.startswith("error"):
            logging.warning("Falha na transcricao do audio: %s", texto or "vazio")
            return None
        return texto

    async def _get_ou_criar_conversa(
        self,
        numero: str,
        instance_name: str,
        nome_contato: Optional[str],
        db: AsyncSession,
    ) -> WhatsappConversa:
        """Busca conversa existente ou cria nova."""
        stmt = select(WhatsappConversa).where(
            and_(
                WhatsappConversa.numero_telefone == numero,
                WhatsappConversa.instance_name == instance_name,
                WhatsappConversa.status == StatusConversa.ATIVA,
            )
        )
        result = await db.execute(stmt)
        conversa = result.scalar_one_or_none()

        if not conversa:
            conversa = WhatsappConversa(
                numero_telefone=numero,
                nome_contato=nome_contato,
                instance_name=instance_name,
                status=StatusConversa.ATIVA,
                contexto_ia={},
            )
            db.add(conversa)
            await db.commit()
            await db.refresh(conversa)
        elif nome_contato and conversa.nome_contato != nome_contato:
            conversa.nome_contato = nome_contato
            await db.commit()
            await db.refresh(conversa)

        return conversa

    async def _processar_status_conexao(
        self,
        data: Dict[str, Any],
        db: AsyncSession,
    ) -> bool:
        """Processa atualizacoes de status de conexao."""
        _ = data
        _ = db
        return True


webhook_service = EvolutionWebhookService()
