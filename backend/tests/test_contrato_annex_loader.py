"""Tests for fixed contract annex loader."""

from app.services.contrato_annex_loader import list_fixed_annexes_for_template


def _annex_ids(items):
    return {str(item.get("id") or "").strip() for item in items}


def test_general_annex_applies_to_regular_template():
    annexes = list_fixed_annexes_for_template("bacen")
    ids = _annex_ids(annexes)

    assert "termo_ciencia_geral" in ids
    assert "termo_ciencia_rating" not in ids


def test_rating_annex_applies_to_rating_template():
    annexes = list_fixed_annexes_for_template("aumento_score")
    ids = _annex_ids(annexes)

    assert "termo_ciencia_geral" in ids
    assert "termo_ciencia_rating" in ids
