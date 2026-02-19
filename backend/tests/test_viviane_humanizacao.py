from app.services.viva_ia_service import VivaIAService


def test_disengage_intent_detected():
    service = VivaIAService()
    assert service._is_disengage_intent("vc e muito insistente nao quero mais vou procurar outra empresa")


def test_who_am_i_reply_contains_known_data():
    service = VivaIAService()
    lead = {
        "nome": "Teste Webhook Lid",
        "telefone": "55223927414591688",
        "servico": "Limpa Nome Standart",
    }
    text = service._build_known_identity_reply(lead=lead, fallback_phone="5516999999999")
    assert "Teste Webhook Lid" in text
    assert "55223927414591688" in text
    assert "Limpa Nome Standart" in text


def test_price_question_detected():
    service = VivaIAService()
    assert service._is_price_question("qual e o valor do limpa nome?")
    assert service._is_price_question("quanto custa o servico?")


def test_fallback_reduces_insistence_when_missing_field_repeats():
    service = VivaIAService()
    resposta = service._garantir_resposta_texto(
        resposta="",
        faltantes=["cidade"],
        lead={"servico": "Limpa Nome"},
        missing_field_streak=3,
    )
    assert "Sem pressa" in resposta
    assert "Quando quiser" in resposta


def test_extract_name_from_natural_intro_with_question():
    service = VivaIAService()
    assert service._extrair_nome("Sou o Ricardo e você ?") == "Ricardo"


def test_extract_name_from_short_turn_with_question():
    service = VivaIAService()
    assert service._extrair_nome("Ricardo qual o seu ?") == "Ricardo"


def test_social_identity_question_detected():
    service = VivaIAService()
    assert service._is_social_identity_question("sou o Ricardo e você?")
    assert service._is_social_identity_question("Ricardo qual o seu nome?")


def test_user_frustration_detected():
    service = VivaIAService()
    assert service._is_user_frustrated("viva nao enrola, voce ta insistente")


def test_decompression_reply_offers_human_handoff():
    service = VivaIAService()
    reply = service._build_decompression_reply(
        lead={"servico": "Limpa Nome"},
        faltantes=["cidade"],
    )
    assert "Sem problema" in reply
    assert "atendimento humano" in reply
