"""CLI entry point. Wraps the OmniMart tool surface for ad-hoc inspection.

Run via:
    omnimart-review-agent summary P-001
    omnimart-review-agent reviews P-001 --limit 5
    omnimart-review-agent pending --limit 5
"""

from __future__ import annotations

import argparse
import json
import sys

from omnimart_review_agent.config import load_settings
from omnimart_review_agent.tools.omnimart import OmniMartClient, OmniMartError


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="omnimart-review-agent")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("summary", help="Fetch rating summary for a product")
    s.add_argument("product_id")

    r = sub.add_parser("reviews", help="Fetch approved reviews for a product")
    r.add_argument("product_id")
    r.add_argument("--limit", type=int, default=20)
    r.add_argument("--cursor", default=None)

    pn = sub.add_parser("pending", help="Fetch moderation queue (internal API)")
    pn.add_argument("--limit", type=int, default=20)
    pn.add_argument("--offset", type=int, default=0)

    sub.add_parser("healthz", help="Ping both OmniMart servers")

    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    settings = load_settings()

    with OmniMartClient(
        site_base_url=settings.omnimart_site_base_url,
        internal_base_url=settings.omnimart_internal_base_url,
        internal_api_key=settings.omnimart_internal_api_key,
    ) as client:
        try:
            if args.command == "summary":
                out = client.get_rating_summary(args.product_id).model_dump(mode="json")
            elif args.command == "reviews":
                out = client.list_reviews(
                    args.product_id, cursor=args.cursor, limit=args.limit
                ).model_dump(mode="json")
            elif args.command == "pending":
                out = [
                    r.model_dump(mode="json")
                    for r in client.list_pending_reviews(offset=args.offset, limit=args.limit)
                ]
            elif args.command == "healthz":
                out = {"site": client.healthz(), "internal": client.healthz(internal=True)}
            else:
                raise AssertionError(f"unhandled command: {args.command}")
        except OmniMartError as e:
            print(f"error: {e}", file=sys.stderr)
            return 1

    print(json.dumps(out, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
