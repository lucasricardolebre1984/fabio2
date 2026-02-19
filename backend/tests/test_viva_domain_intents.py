from datetime import datetime
from uuid import UUID

import pytest

from app.services.assistant.intents.campanhas import is_campaign_count_intent, is_campaign_list_intent
from app.services.assistant.intents.clientes import (
    extract_client_name_for_detail_query,
    is_client_detail_intent,
    is_client_profile_contracts_intent,
    is_visual_proof_request,
)
from app.services.assistant.intents.contratos import is_contract_templates_intent
from app.services.viva_agenda_nlu_service import parse_agenda_conclude_command, parse_agenda_natural_create
from app.services.viva_domain_query_router_service import viva_domain_query_router_service


def test_client_detail_intent_and_name_extraction():
    msg = "entre no cadastro do cliente Lucas Ricardo Lebre"
    assert is_client_detail_intent(msg) is True
    assert extract_client_name_for_detail_query(msg) == "Lucas Ricardo Lebre"


def test_contract_templates_intent_tolerates_typos():
    assert is_contract_templates_intent("quero ver os modolos de contratos") is True
    assert is_contract_templates_intent("listar modelos de contrato") is True
    assert is_contract_templates_intent("lista os modulos de contratos que temos") is True


def test_campaign_list_intent_does_not_trigger_generation_path():
    assert is_campaign_list_intent("liste todas as campanhas criadas") is True
    assert is_campaign_list_intent("gere uma campanha de carnaval") is False


def test_campaign_count_intent_simple_direct():
    assert is_campaign_count_intent("campanhas feitas") is True
    assert is_campaign_count_intent("quero saber quantas campanhas temos feitas") is True
    assert is_campaign_count_intent("gere campanha de carnaval") is False


def test_visual_proof_request_guard_intent():
    msg = "olha o print do cliente e me fale com prova se tem telefone"
    assert is_visual_proof_request(msg) is True


def test_combined_client_contract_intent_with_noisy_text():
    msg = "Que pra mim o Lucas Leiva que que ele tem de contrato e cadastro?"
    assert is_client_profile_contracts_intent(msg) is True


def test_agenda_conclude_requires_agenda_context():
    assert parse_agenda_conclude_command("vai se fuder ordem direta nao tenho que confirmar nada") is None
    assert parse_agenda_conclude_command("confirmar compromisso reuniao com andre") is not None


def test_agenda_natural_create_accepts_marca_variant():
    payload = parse_agenda_natural_create("entao marca pra mim falar com o Antonio Briggs daqui uma hora")
    assert payload is not None
    assert payload.get("error") is None
    assert "antonio" in str(payload.get("title", "")).lower()


def test_agenda_natural_create_accepts_coloque_na_agenda_with_google_verification_clause():
    payload = parse_agenda_natural_create(
        "coloque na agenda compromisso ligar para fabio hoje as 18 horas verifique se google agenda ja esta vinculada"
    )
    assert payload is not None
    assert payload.get("error") is None
    title = str(payload.get("title", "")).lower()
    assert "google" not in title
    assert "verifique" not in title
    assert "ligar" in title


def test_agenda_natural_create_accepts_viva_prefix_and_only_hour():
    payload = parse_agenda_natural_create("viva marque na agenda teste com a nega as 17 horas")
    assert payload is not None
    assert payload.get("error") is None
    title = str(payload.get("title", "")).lower()
    assert "teste" in title
    assert "nega" in title
    date_time = payload.get("date_time")
    assert isinstance(date_time, datetime)
    assert date_time.hour == 17
    assert date_time.minute == 0


@pytest.mark.asyncio
async def test_domain_router_returns_client_detail_with_real_fields(monkeypatch):
    class _FakeClienteService:
        def __init__(self, db):
            self.db = db

        async def list(self, search=None, page=1, page_size=20):
            assert "lucas" in str(search or "").lower()
            return {
                "items": [
                    {
                        "nome": "Lucas Ricardo Lebre",
                        "documento": "33429258847",
                        "telefone": "11999998888",
                        "email": "lucas@example.com",
                        "cidade": "Sao Paulo",
                        "estado": "SP",
                        "endereco": "Rua A, 100",
                        "observacoes": "Cliente premium",
                        "total_contratos": 21,
                    }
                ],
                "total": 1,
            }

    monkeypatch.setattr(
        "app.services.viva_domain_query_router_service.ClienteService",
        _FakeClienteService,
    )

    response = await viva_domain_query_router_service.handle_domain_query(
        db=object(),
        user_id="00000000-0000-0000-0000-000000000000",
        message="entre no cadastro do cliente Lucas Ricardo Lebre",
        contexto_efetivo=[],
    )

    assert response is not None
    assert "Abrindo cadastro de Lucas Ricardo Lebre" in response
    assert "Telefone: 11999998888" in response
    assert "Contratos vinculados: 21" in response


@pytest.mark.asyncio
async def test_domain_router_client_detail_uses_fuzzy_match(monkeypatch):
    class _FakeClienteService:
        def __init__(self, db):
            self.db = db

        async def list(self, search=None, page=1, page_size=20):
            if search:
                return {"items": [], "total": 0}
            return {
                "items": [
                    {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "nome": "Fabio D C da Silva",
                        "documento": "32521118885",
                        "telefone": "11988887777",
                        "email": "fabio@fcsolucoes.com",
                        "cidade": "Sao Paulo",
                        "estado": "SP",
                        "endereco": "Rua B, 200",
                        "observacoes": "",
                        "total_contratos": 5,
                    }
                ],
                "total": 1,
            }

    monkeypatch.setattr(
        "app.services.viva_domain_query_router_service.ClienteService",
        _FakeClienteService,
    )

    response = await viva_domain_query_router_service.handle_domain_query(
        db=object(),
        user_id="00000000-0000-0000-0000-000000000000",
        message="abrir cadastro do cliente Fabio da Unisete",
        contexto_efetivo=[],
    )

    assert response is not None
    assert "Fabio D C da Silva" in response
    assert "Telefone: 11988887777" in response


@pytest.mark.asyncio
async def test_domain_router_blocks_visual_proof_hallucination():
    response = await viva_domain_query_router_service.handle_domain_query(
        db=object(),
        user_id="00000000-0000-0000-0000-000000000000",
        message="olha o print e me fala com prova se o cliente tem telefone",
        contexto_efetivo=[],
    )

    assert response is not None
    assert "Nao uso print/anexo como prova" in response


@pytest.mark.asyncio
async def test_domain_router_returns_combined_client_and_contracts_summary(monkeypatch):
    client_id = UUID("11111111-1111-1111-1111-111111111111")

    class _FakeClienteService:
        def __init__(self, db):
            self.db = db

        async def list(self, search=None, page=1, page_size=20):
            return {
                "items": [
                    {
                        "id": client_id,
                        "nome": "Lucas Ricardo Lebre",
                        "documento": "33429258847",
                        "telefone": "11999998888",
                        "email": "lucas@example.com",
                        "cidade": "Sao Paulo",
                        "estado": "SP",
                        "endereco": "Rua A, 100",
                        "observacoes": "Cliente premium",
                        "total_contratos": 2,
                    }
                ],
                "total": 1,
            }

        async def get_contratos(self, cliente_id):
            assert cliente_id == client_id
            return [
                _Contrato("CNT-2026-0043", "Contrato CADIN", "rascunho", datetime(2026, 2, 16)),
                _Contrato("CNT-2026-0042", "Contrato BACEN", "cancelado", datetime(2026, 2, 15)),
            ]

    class _Status:
        def __init__(self, value):
            self.value = value

    class _Contrato:
        def __init__(self, numero, template_nome, status, created_at):
            self.numero = numero
            self.template_nome = template_nome
            self.status = _Status(status)
            self.created_at = created_at
            self.contratante_nome = "Lucas Ricardo Lebre"

    monkeypatch.setattr(
        "app.services.viva_domain_query_router_service.ClienteService",
        _FakeClienteService,
    )

    response = await viva_domain_query_router_service.handle_domain_query(
        db=object(),
        user_id="00000000-0000-0000-0000-000000000000",
        message="Que pra mim o Lucas Leiva que que ele tem de contrato e cadastro?",
        contexto_efetivo=[],
    )

    assert response is not None
    assert "Resumo do cliente Lucas Ricardo Lebre" in response
    assert "Telefone: 11999998888" in response
    assert "CNT-2026-0043" in response
    assert "CNT-2026-0042" not in response


@pytest.mark.asyncio
async def test_domain_router_returns_contract_count_by_client(monkeypatch):
    client_id = UUID("22222222-2222-2222-2222-222222222222")

    class _FakeClienteService:
        def __init__(self, db):
            self.db = db

        async def list(self, search=None, page=1, page_size=20):
            return {
                "items": [
                    {
                        "id": client_id,
                        "nome": "Fabio D C da Silva",
                    }
                ],
                "total": 1,
            }

        async def get_contratos(self, cliente_id):
            class _Status:
                def __init__(self, value):
                    self.value = value

            class _Contrato:
                def __init__(self, status):
                    self.status = _Status(status)

            return [_Contrato("rascunho"), _Contrato("finalizado"), _Contrato("cancelado")]

    monkeypatch.setattr(
        "app.services.viva_domain_query_router_service.ClienteService",
        _FakeClienteService,
    )

    response = await viva_domain_query_router_service.handle_domain_query(
        db=object(),
        user_id="00000000-0000-0000-0000-000000000000",
        message="Quantos contratos tem no cliente Fabio?",
        contexto_efetivo=[],
    )

    assert response is not None
    assert "Fabio D C da Silva" in response
    assert "2 contratos ativos" in response
    assert "3 contratos emitidos" in response
