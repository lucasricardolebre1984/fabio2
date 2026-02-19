import pytest

from app.services.evolution_webhook_service import EvolutionWebhookService


class _DummyDb:
    async def commit(self):
        return None


class _DummyConversa:
    def __init__(self, contexto):
        self.contexto_ia = contexto
        self.nome_contato = "Lucas"
        self.numero_telefone = "223927414591688"


@pytest.mark.asyncio
async def test_flush_pending_outbound_delivers_and_clears_queue(monkeypatch):
    service = EvolutionWebhookService()
    conversa = _DummyConversa(
        {
            "lead": {"telefone": "5516981903443"},
            "pending_outbound": [
                {
                    "id": "1",
                    "conteudo": "teste pendente",
                    "remote_jid": "223927414591688@lid",
                    "push_name": "Lucas",
                    "attempts": 0,
                }
            ],
        }
    )

    async def _fake_send_text(self, numero, mensagem, context_push_name=None, context_preferred_number=None):
        return {"sucesso": True, "destino": "5516981903443"}

    monkeypatch.setattr("app.services.whatsapp_service.WhatsAppService.send_text", _fake_send_text)

    sent = await service._flush_pending_outbound_for_conversation(
        db=_DummyDb(),
        conversa=conversa,
        push_name="Lucas",
        remote_jid="223927414591688@lid",
    )

    assert sent == 1
    assert conversa.contexto_ia.get("pending_outbound") == []

