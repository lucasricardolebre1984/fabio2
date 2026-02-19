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

