"""
Servico de Webhook para Evolution API.
Recebe mensagens do WhatsApp e integra com IA VIVA.
"""
from datetime import datetime
import logging
from typing import Any, Dict, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.whatsapp_conversa import (
    StatusConversa,
    TipoOrigem,
    WhatsappConversa,
    WhatsappMensagem,
)
from app.services.viva_ia_service import viva_service
from app.services.whatsapp_service import WhatsAppService


class EvolutionWebhookService:
    """Processa webhooks recebidos do Evolution Manager."""

    async def processar_webhook(
        self,
        data: Dict[str, Any],
        db: AsyncSession,
    ) -> bool:
        """Processa evento recebido do Evolution API."""
        event_type = data.get("event")

        if event_type == "messages.upsert":
            return await self._processar_mensagem(data, db)
        if event_type == "connection.update":
            return await self._processar_status_conexao(data, db)

        return True

    async def _processar_mensagem(
        self,
        data: Dict[str, Any],
        db: AsyncSession,
    ) -> bool:
        """Processa nova mensagem recebida."""
        try:
            message_data = data.get("data", {}).get("message", {})
            instance_data = data.get("instance", {})

            numero = message_data.get("key", {}).get("remoteJid", "").split("@")[0]
            texto = self._extrair_texto_mensagem(message_data)
            instance_name = instance_data.get("instanceName", "Teste")

            if not numero or not texto:
                return True

            conversa = await self._get_ou_criar_conversa(
                numero=numero,
                instance_name=instance_name,
                db=db,
            )

            msg_usuario = WhatsappMensagem(
                conversa_id=conversa.id,
                tipo_origem=TipoOrigem.USUARIO,
                conteudo=texto,
                message_id=message_data.get("key", {}).get("id"),
            )
            db.add(msg_usuario)

            conversa.ultima_mensagem_em = datetime.utcnow()
            await db.commit()

            resposta_ia = await viva_service.processar_mensagem(
                numero=numero,
                mensagem=texto,
                conversa=conversa,
                db=db,
            )

            wa_service = WhatsAppService()
            envio_result = await wa_service.send_text(numero=numero, mensagem=resposta_ia)
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
            await db.commit()

            return True
        except Exception as e:
            logging.exception("Erro ao processar mensagem webhook: %s", str(e))
            return False

    def _extrair_texto_mensagem(self, message_data: Dict[str, Any]) -> Optional[str]:
        """Extrai texto da mensagem do payload."""
        try:
            if "conversation" in message_data:
                return message_data["conversation"]

            if "extendedTextMessage" in message_data:
                return message_data["extendedTextMessage"].get("text", "")

            if "imageMessage" in message_data:
                return message_data["imageMessage"].get("caption", "[imagem]")

            return None
        except Exception:
            return None

    async def _get_ou_criar_conversa(
        self,
        numero: str,
        instance_name: str,
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
                instance_name=instance_name,
                status=StatusConversa.ATIVA,
                contexto_ia={},
            )
            db.add(conversa)
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
