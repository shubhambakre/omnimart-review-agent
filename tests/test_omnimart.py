"""Integration smoke test against a locally running OmniMart server.

Skipped if OmniMart isn't up. Run with:
    pytest -m integration
or simply:
    pytest                 # auto-skips when the server isn't reachable
"""

from __future__ import annotations

import pytest

from omnimart_review_agent.config import load_settings
from omnimart_review_agent.tools.omnimart import OmniMartClient, OmniMartError


@pytest.fixture(scope="module")
def client() -> OmniMartClient:
    settings = load_settings()
    c = OmniMartClient(
        site_base_url=settings.omnimart_site_base_url,
        internal_base_url=settings.omnimart_internal_base_url,
        internal_api_key=settings.omnimart_internal_api_key,
    )
    if not c.healthz():
        c.close()
        pytest.skip("OmniMart site server not reachable — start it with `make run`")
    yield c
    c.close()


@pytest.mark.integration
def test_healthz_both_servers(client: OmniMartClient) -> None:
    assert client.healthz() is True
    assert client.healthz(internal=True) is True


@pytest.mark.integration
def test_summary_unknown_product_returns_error(client: OmniMartClient) -> None:
    # OmniMart returns a zeroed/404 envelope for unknown product. We just want a clean
    # signal (either a 404 OmniMartError or a zero-totalReviews summary). Both are valid;
    # the contract is "doesn't raise an unexpected exception".
    try:
        summary = client.get_rating_summary("does-not-exist")
        assert summary.total_reviews == 0
    except OmniMartError as e:
        assert e.status_code in (404, 400)


@pytest.mark.integration
def test_list_pending_internal_api_authenticates(client: OmniMartClient) -> None:
    """Confirms the X-Api-Key header is wired through — should not get an auth error."""
    pending = client.list_pending_reviews(limit=5)
    assert isinstance(pending, list)


@pytest.mark.integration
def test_list_pending_with_wrong_api_key_raises(client: OmniMartClient) -> None:
    """Negative path — guarantees the auth check is real, not stubbed off."""
    settings = load_settings()
    with OmniMartClient(
        site_base_url=settings.omnimart_site_base_url,
        internal_base_url=settings.omnimart_internal_base_url,
        internal_api_key="not-a-valid-key",
    ) as bad:
        with pytest.raises(OmniMartError) as exc:
            bad.list_pending_reviews(limit=1)
        assert exc.value.status_code in (401, 403)
