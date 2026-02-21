from app.services.evolution_webhook_service import EvolutionWebhookService


def test_pick_preferred_ignores_invalid_resolved_number_and_uses_lead_phone():
    service = EvolutionWebhookService()
    context = {
        "resolved_whatsapp_number": "55",
        "lead": {"telefone": "5516997030530"},
    }
    assert service._pick_preferred_number_from_context(context) == "5516997030530"


def test_extract_numero_from_lid_prefers_participant_real_phone():
    service = EvolutionWebhookService()
    message_wrapper = {
        "key": {
            "remoteJid": "40372910711016@lid",
            "participant": "5516997030530@s.whatsapp.net",
        },
        "message": {"conversation": "Oi"},
    }
    payload_data = {}
    assert service._extrair_numero(message_wrapper, payload_data) == "5516997030530"


def test_extract_number_from_lid_metadata_remote_jid_alt():
    service = EvolutionWebhookService()
    message_wrapper = {
        "key": {
            "remoteJid": "260129056403704@lid",
            "remoteJidAlt": "5516981234567@s.whatsapp.net",
        },
        "message": {"conversation": "Oi"},
    }
    payload_data = {}
    assert service._extract_number_from_lid_metadata(message_wrapper, payload_data) == "5516981234567"


def test_extract_message_wrapper_supports_messages_list_payload():
    service = EvolutionWebhookService()
    payload_data = {
        "messages": [
            {
                "key": {
                    "id": "ABCD1234",
                    "remoteJid": "5516999999999@s.whatsapp.net",
                },
                "message": {"conversation": "oi"},
                "pushName": "Lucas",
            }
        ]
    }
    wrapper = service._extrair_message_wrapper(payload_data)
    assert isinstance(wrapper, dict)
    assert wrapper.get("key", {}).get("remoteJid") == "5516999999999@s.whatsapp.net"


def test_extract_message_wrapper_prefers_inbound_when_messages_batch_has_from_me():
    service = EvolutionWebhookService()
    payload_data = {
        "messages": [
            {
                "key": {
                    "id": "OUTBOUND001",
                    "remoteJid": "5516999999999@s.whatsapp.net",
                    "fromMe": True,
                },
                "message": {"conversation": "mensagem enviada pelo proprio bot"},
            },
            {
                "key": {
                    "id": "INBOUND001",
                    "remoteJid": "5516888888888@s.whatsapp.net",
                    "fromMe": False,
                },
                "message": {"conversation": "mensagem real do cliente"},
            },
        ]
    }
    wrapper = service._extrair_message_wrapper(payload_data)
    assert isinstance(wrapper, dict)
    assert wrapper.get("key", {}).get("id") == "INBOUND001"


def test_is_from_me_message_helper():
    service = EvolutionWebhookService()
    assert service._is_from_me_message({"key": {"fromMe": True}}) is True
    assert service._is_from_me_message({"key": {"fromMe": False}}) is False
