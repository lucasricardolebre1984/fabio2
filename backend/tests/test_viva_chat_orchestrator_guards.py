from app.services.viva_chat_orchestrator_service import (
    _mentions_agenda_creation_confirmation,
    _should_generate_pending_campaign_followup,
)


def test_mentions_agenda_creation_confirmation_detects_explicit_phrases():
    assert _mentions_agenda_creation_confirmation("agendamento criado com sucesso") is True
    assert _mentions_agenda_creation_confirmation("compromisso criado para hoje") is True
    assert _mentions_agenda_creation_confirmation("campanha criada para fc com formatos gerados") is False


def test_pending_campaign_followup_generation_accepts_cta_field():
    assert (
        _should_generate_pending_campaign_followup(
            message="cta no brasil, o ano comeca agora",
            pending_campaign=True,
            explicit_fields={"cta": "No Brasil, o ano comeca depois do Carnaval."},
        )
        is True
    )
    assert (
        _should_generate_pending_campaign_followup(
            message="sim",
            pending_campaign=True,
            explicit_fields={},
        )
        is True
    )
    assert (
        _should_generate_pending_campaign_followup(
            message="sim",
            pending_campaign=False,
            explicit_fields={},
        )
        is False
    )
