# omnimart-review-agent

> An agentic LLM application that composes four sibling portfolio projects — [omnimart-ratings-reviews](https://github.com/shubhambakre/omnimart-ratings-reviews), [go-llm-gateway](https://github.com/shubhambakre/go-llm-gateway), [vertex-ai-rag-pipeline](https://github.com/shubhambakre/vertex-ai-rag-pipeline), and [llm-eval-harness](https://github.com/shubhambakre/llm-eval-harness) — into one stack that demonstrates agent loops, tool use, model routing across Claude Opus / Sonnet / Haiku, and evaluation as a runtime concern.

**Status:** Day 1 — OmniMart tool wrapper only. See [SPEC.md](SPEC.md) for the full build plan and [BLOG_OUTLINE.md](BLOG_OUTLINE.md) for the writeup outline.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

# In another terminal: start OmniMart locally
cd ../omnimart-ratings-reviews && make run

# Then back here:
omnimart-review-agent summary P-001
omnimart-review-agent reviews P-001 --limit 5
omnimart-review-agent pending --limit 5
```

## Layout

```
omnimart-review-agent/
├── src/omnimart_review_agent/
│   ├── __main__.py          # CLI entry
│   ├── config.py            # pydantic-settings
│   └── tools/
│       └── omnimart.py      # OmniMart HTTP client (Day 1)
├── tests/
│   └── test_omnimart.py     # integration smoke test
├── SPEC.md
├── BLOG_OUTLINE.md
└── pyproject.toml
```

## Tests

```bash
pytest                       # runs everything; integration tests skip if OmniMart isn't up
pytest -m integration        # only integration tests
```
