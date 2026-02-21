from app.services.viva_chat_runtime_helpers_service import (
    _extract_handoff_lead_minutes,
    _is_handoff_whatsapp_intent,
    _is_viviane_handoff_query_intent,
    _sanitize_fake_asset_delivery_reply,
)


def test_sanitize_fake_campaign_delivery_reply_blocks_fake_success_text():
    reply = (
        "Campanha criada para FC com base na referencia.\n"
        "Formatos gerados: feed e story.\n"
        "Local salvo: Campanhas > FC > Ano pos-carnaval."
    )
    sanitized = _sanitize_fake_asset_delivery_reply(reply, "FC")
    assert "Ainda nao confirmei criacao real da campanha no SaaS" in sanitized


def test_sanitize_fake_campaign_delivery_reply_keeps_regular_text():
    reply = "Perfeito. Me envie o CTA final e eu gero a campanha."
    sanitized = _sanitize_fake_asset_delivery_reply(reply, "FC")
    assert sanitized == reply


def test_handoff_intent_detects_direct_reminder_command():
    text = "lembrete no meu whatsapp pela viviane meia hora antes ok"
    assert _is_handoff_whatsapp_intent(text) is True
    assert _is_viviane_handoff_query_intent(text) is False


def test_handoff_query_intent_detects_list_request():
    text = "Viviane, quais lembretes pendentes no WhatsApp hoje?"
    assert _is_viviane_handoff_query_intent(text) is True


def test_extract_handoff_lead_minutes_supports_natural_phrases():
    assert _extract_handoff_lead_minutes("meia hora antes") == 30
    assert _extract_handoff_lead_minutes("30 minutos antes") == 30
    assert _extract_handoff_lead_minutes("2 horas antes") == 120
