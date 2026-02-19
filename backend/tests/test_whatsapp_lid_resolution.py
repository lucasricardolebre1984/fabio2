import pytest

from app.services.whatsapp_service import WhatsAppService


@pytest.mark.asyncio
async def test_resolve_lid_prefers_validated_preferred_number(monkeypatch):
    service = WhatsAppService()

    async def _fake_fetch_contacts(client, instance):
        return []

    async def _fake_fetch_chats(client, instance):
        return []

    async def _fake_check_whatsapp_number(client, instance, number):
        return number if number == "5511999998888" else None

    monkeypatch.setattr(service, "_fetch_contacts", _fake_fetch_contacts)
    monkeypatch.setattr(service, "_fetch_chats", _fake_fetch_chats)
    monkeypatch.setattr(service, "_check_whatsapp_number", _fake_check_whatsapp_number)

    resolved = await service._resolve_lid_number(
        client=None,
        instance="fc-solucoes",
        numero="123456789@lid",
        context_push_name="Lucas",
        context_preferred_number="(11) 99999-8888",
    )

    assert resolved == "5511999998888"


@pytest.mark.asyncio
async def test_resolve_lid_ignores_invalid_preferred_and_uses_chat_similarity(monkeypatch):
    service = WhatsAppService()

    async def _fake_fetch_contacts(client, instance):
        return [
            {
                "remoteJid": "223927414591688@lid",
                "pushName": "Lucas",
            }
        ]

    async def _fake_fetch_chats(client, instance):
        return [
            {
                "remoteJid": "223927414591688@lid",
                "pushName": "Lucas",
                "updatedAt": "2026-02-19T18:33:36.000Z",
            },
            {
                "remoteJid": "5516997030530@s.whatsapp.net",
                "pushName": "Lucas Lebre",
                "updatedAt": "2026-02-19T18:34:10.000Z",
            },
        ]

    async def _fake_check_whatsapp_number(client, instance, number):
        return number if number == "5516997030530" else None

    monkeypatch.setattr(service, "_fetch_contacts", _fake_fetch_contacts)
    monkeypatch.setattr(service, "_fetch_chats", _fake_fetch_chats)
    monkeypatch.setattr(service, "_check_whatsapp_number", _fake_check_whatsapp_number)

    resolved = await service._resolve_lid_number(
        client=None,
        instance="fc-solucoes",
        numero="223927414591688@lid",
        context_push_name="Lucas",
        context_preferred_number="55223927414591688",
    )

    assert resolved == "5516997030530"


@pytest.mark.asyncio
async def test_resolve_lid_does_not_return_unvalidated_fallback(monkeypatch):
    service = WhatsAppService()

    async def _fake_fetch_contacts(client, instance):
        return []

    async def _fake_fetch_chats(client, instance):
        return []

    async def _fake_check_whatsapp_number(client, instance, number):
        return None

    monkeypatch.setattr(service, "_fetch_contacts", _fake_fetch_contacts)
    monkeypatch.setattr(service, "_fetch_chats", _fake_fetch_chats)
    monkeypatch.setattr(service, "_check_whatsapp_number", _fake_check_whatsapp_number)

    resolved = await service._resolve_lid_number(
        client=None,
        instance="fc-solucoes",
        numero="260129056403704@lid",
        context_push_name="Tuane",
        context_preferred_number="5516981234567",
    )

    assert resolved is None
