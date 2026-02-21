from app.services.viva_chat_runtime_helpers_service import _sanitize_fake_asset_delivery_reply


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
