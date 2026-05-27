"""OmniMart Ratings & Reviews HTTP client.

Wraps the two OmniMart API surfaces (site-facing :8080, internal :8081) as typed Python
methods. Used by the agent's tool layer (Day 3+) and directly by the CLI (Day 1).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field


# ---------- Response models (mirror omnimart-ratings-reviews/internal/domain) ----------


class Review(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    product_id: str = Field(alias="productId")
    customer_id: str = Field(alias="customerId")
    order_id: str | None = Field(default=None, alias="orderId")
    rating: int
    title: str
    body: str
    verified_purchase: bool = Field(alias="verifiedPurchase")
    status: str
    helpful_count: int = Field(alias="helpfulCount")
    unhelpful_count: int = Field(alias="unhelpfulCount")
    moderation_notes: str | None = Field(default=None, alias="moderationNotes")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class ReviewsPage(BaseModel):
    reviews: list[Review]
    next_cursor: str | None = Field(default=None, alias="nextCursor")

    model_config = ConfigDict(populate_by_name=True)


class RatingSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    product_id: str = Field(alias="productId")
    average_rating: float = Field(alias="averageRating")
    total_reviews: int = Field(alias="totalReviews")
    distribution: dict[int, int]
    updated_at: datetime = Field(alias="updatedAt")


# ---------- Errors ----------


class OmniMartError(Exception):
    """Raised when the OmniMart API returns a non-2xx response."""

    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(f"OmniMart {status_code} {code}: {message}")


# ---------- Client ----------


class OmniMartClient:
    """Thin typed wrapper over OmniMart's two HTTP surfaces.

    Sync (httpx). Async variant can be added by mirroring methods if/when the agent loop
    benefits from concurrent tool calls.
    """

    def __init__(
        self,
        site_base_url: str = "http://localhost:8080",
        internal_base_url: str = "http://localhost:8081",
        internal_api_key: str = "dev-internal-key",
        timeout: float = 10.0,
    ):
        self._site = httpx.Client(base_url=site_base_url, timeout=timeout)
        self._internal = httpx.Client(
            base_url=internal_base_url,
            timeout=timeout,
            headers={"X-Api-Key": internal_api_key},
        )

    def close(self) -> None:
        self._site.close()
        self._internal.close()

    def __enter__(self) -> OmniMartClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ----- Site-facing (:8080) -----

    def list_reviews(
        self,
        product_id: str,
        cursor: str | None = None,
        limit: int = 20,
    ) -> ReviewsPage:
        """Fetch a page of APPROVED reviews for a product. Site-facing API."""
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        data = self._get(self._site, f"/v1/products/{product_id}/reviews", params=params)
        return ReviewsPage.model_validate(data)

    def get_rating_summary(self, product_id: str) -> RatingSummary:
        """Fetch the aggregate rating summary for a product. Site-facing API."""
        data = self._get(self._site, f"/v1/products/{product_id}/ratings/summary")
        return RatingSummary.model_validate(data)

    # ----- Internal (:8081, X-Api-Key) -----

    def list_pending_reviews(self, offset: int = 0, limit: int = 20) -> list[Review]:
        """Fetch the moderation queue. Internal API; requires API key."""
        data = self._get(
            self._internal,
            "/internal/v1/reviews/pending",
            params={"offset": offset, "limit": limit},
        )
        if isinstance(data, list):
            return [Review.model_validate(r) for r in data]
        if isinstance(data, dict) and "reviews" in data:
            return [Review.model_validate(r) for r in data["reviews"]]
        return []

    def healthz(self, internal: bool = False) -> bool:
        client = self._internal if internal else self._site
        try:
            r = client.get("/healthz")
            return r.status_code == 200
        except httpx.HTTPError:
            return False

    # ----- internals -----

    @staticmethod
    def _get(client: httpx.Client, path: str, params: dict[str, Any] | None = None) -> Any:
        r = client.get(path, params=params)
        body = r.json() if r.content else {}
        if r.status_code >= 400:
            err = body.get("error", {}) if isinstance(body, dict) else {}
            raise OmniMartError(
                status_code=r.status_code,
                code=err.get("code", "UNKNOWN"),
                message=err.get("message", r.text or "no body"),
            )
        if isinstance(body, dict) and "data" in body:
            return body["data"]
        return body
