import pytest


pytestmark = pytest.mark.skip(
    reason=(
        "Legacy GLM image integration script deprecated: "
        "module app.services.glm_image_service is no longer part of backend."
    )
)


def test_glm_legacy_placeholder():
    """Placeholder to keep historical test id without breaking pytest collection."""
    assert True
