# omnimart-review-agent — Project Spec

**One-line pitch:** An agentic LLM application that composes four existing portfolio projects (OmniMart API, go-llm-gateway, vertex-ai-rag-pipeline, llm-eval-harness) into one stack that demonstrates 2026-grade applied AI engineering.

**Target audience for this artifact:** A reviewer at Anthropic / OpenAI / Google Cloud / an AI-first startup who opens the GitHub repo cold and decides in ~3 minutes whether to keep reading.

---

## 1. Why this project exists

The current portfolio has six strong but **disconnected** projects. A reviewer sees infra (gateway), retrieval (RAG), evaluation (harness), and a marketplace API (OmniMart) — but has to do the synthesis work themselves to see that the author can build *applied LLM systems end-to-end*.

This project is the synthesis. It is the only project that:

1. Calls every other project as a service / tool.
2. Demonstrates **agent loops, tool use, and eval-in-the-loop** — the three skills that moved from "nice-to-have" to "table stakes" in AI/ML hiring during 2025.
3. Gives the portfolio a single anchor URL: *"this is the project I want you to look at."*

Without this project, the portfolio reads as competent. With it, it reads as senior.

## 2. What it does (product surface)

A CLI + thin HTTP API that, given a product ID or a freeform question:

- **Mode A — Insights report.** Pulls approved reviews from OmniMart, retrieves product/category context from the RAG pipeline, drafts a structured insights report (sentiment themes, top complaints, recommended merchant actions), self-evaluates the report with the eval harness, retries with critique if quality is below threshold, and emits both the final report and the full trace.
- **Mode B — Conversational Q&A.** Multi-turn chat where the user asks questions like "what are customers saying about returns?" and the agent decides which tools to call.

Both modes share the same agent core. Mode A is the **demo-able artifact** (deterministic-ish, screen-recordable). Mode B is the **stretch / interactive** mode.

## 3. Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                       omnimart-review-agent                       │
│                                                                   │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│   │   Planner    │ -> │   Executor   │ -> │    Critic    │       │
│   │  (Claude)    │    │  (tool use)  │    │ (eval-judge) │       │
│   └──────────────┘    └──────┬───────┘    └──────┬───────┘       │
│           ^                  │                    │               │
│           └──────────────────┴────────────────────┘               │
│                       retry-with-critique loop                    │
└──────────────────────────────────────────────────────────────────┘
            │                  │              │              │
            v                  v              v              v
     ┌──────────┐      ┌──────────────┐  ┌──────────┐  ┌──────────┐
     │ OmniMart │      │ go-llm-      │  │ vertex-  │  │ llm-eval-│
     │ internal │      │ gateway      │  │ ai-rag   │  │ harness  │
     │ API      │      │ (LLM calls)  │  │ pipeline │  │ (judges) │
     └──────────┘      └──────────────┘  └──────────┘  └──────────┘
```

**Tools exposed to the agent (Anthropic-SDK tool-use schema):**

| Tool | Backend | Purpose |
|---|---|---|
| `list_reviews(product_id, cursor?, limit?)` | OmniMart site API (`:8080`) | Fetch paginated **approved** reviews — site-facing API filters to approved by design |
| `get_rating_summary(product_id)` | OmniMart site API (`:8080`) | Aggregate stats (avg + distribution) |
| `list_pending_reviews(offset?, limit?)` | OmniMart internal API (`:8081`, `X-Api-Key`) | Optional: moderation queue (merchant-insights stretch — see what's *about* to land) |
| `retrieve_product_context(query, top_k=5)` | vertex-ai-rag-pipeline | Cross-product / category docs |
| `draft_report(reviews, context, prior_critique?)` | go-llm-gateway | LLM call routed through gateway |
| `evaluate_report(report, reviews)` | llm-eval-harness | Faithfulness + Correctness scores |

All LLM calls route through **go-llm-gateway** — even the planner's. This is non-negotiable because it (a) demos the gateway in the same trace and (b) gives one place to swap models for the cost/quality comparison stretch goal.

## 4. The eval-in-the-loop pattern (the differentiator)

Most agent demos in 2026 are agent → tool calls → final output. This project adds:

```
draft_report → evaluate_report
  if scores >= threshold: return
  else:
    critique = explain_failure(scores)
    draft_report(..., prior_critique=critique)   # retry
  cap retries at 3, log all attempts
```

**Why this matters:** It directly addresses the #1 production failure mode of LLM apps (silent hallucination) by making evaluation a first-class runtime concern, not a CI step. This is the bullet point that survives a 30-second resume scan.

## 5. Tech choices (with the *why*)

| Decision | Choice | Why |
|---|---|---|
| Language | **Python 3.11+** | RAG + eval clients are already Python; rewriting in Go would be reimplementation theater. |
| Agent framework | **No framework — hand-rolled ~300-line loop** | LangChain agents are opaque and brittle; a reviewer who's debugged one will respect this. Senior signal. |
| LLM SDK | **`anthropic` SDK with tool use** | Target companies include Anthropic. Show you know the SDK directly, including prompt caching. |
| Routing | All Anthropic calls go via go-llm-gateway base URL | Demos the gateway in the same trace. |
| Storage of traces | Local JSONL per run, optional SQLite for the viewer | Zero-deps demo; SQLite is the upgrade path. |
| Models | Default **Claude Sonnet 4.6** for planner, **Haiku 4.5** for cheap tool-selection passes, **Opus 4.7** for the critic | The model-routing story is itself a portfolio asset. |
| Prompt caching | **Yes — cache the system prompt + tool definitions** | Reduces cost on multi-turn / retry runs; explicitly called out in the README. |

## 6. Build plan (1–2 weeks, evenings)

- **Day 1:** Project skeleton, `.env`, tool wrapper for OmniMart (start it locally with `make run`). Smoke test: list_reviews returns JSON.
- **Day 2:** Tool wrappers for RAG + eval harness. Smoke test: end-to-end one-shot (no agent yet) — fetch reviews, draft summary via gateway, evaluate.
- **Day 3:** Agent loop with Anthropic SDK tool use. Planner picks tools. Single-pass, no critic yet.
- **Day 4:** Critic + retry-with-critique loop. Trace logging.
- **Day 5:** CLI polish, structured report schema (Pydantic), example run captured to `examples/`.
- **Day 6:** README (with architecture diagram), GIF/screen-recording of a run, eval-in-the-loop explainer section.
- **Day 7:** Blog post draft: *"Composing four side projects into one LLM stack."*

**Stretch (week 2):**
- HTTP API mode (Mode B conversational).
- Trace viewer (simple Streamlit or htmx page reading JSONL).
- **Model-comparison study:** Same 20 test products, Sonnet 4.6 vs Haiku 4.5 vs Opus 4.7, plot quality vs $ vs latency. This is its own blog post and gets shared.

## 7. Definition of done

The project ships when **all** of these are true:

- [ ] `make demo` runs end-to-end against locally-running OmniMart + RAG + eval, with no manual setup beyond `.env`.
- [ ] README has architecture diagram, the eval-loop explainer, and an embedded recording.
- [ ] At least one example run is checked in to `examples/` (report + trace JSON).
- [ ] Tool calls are logged with token counts, latency, and which gateway backend served the request.
- [ ] Prompt caching is wired and visible in the trace (cache_read_input_tokens > 0 on second turn).
- [ ] Blog post drafted (publish gates separately).

## 8. Non-goals (deliberate)

- **Not building a UI beyond CLI + maybe one Streamlit page.** This is an engineering portfolio, not a product.
- **Not training or fine-tuning anything.** The story is composition, not modeling.
- **Not adding a vector DB.** RAG pipeline already has BigQuery vector index.
- **Not generalizing the agent to other domains.** Resist the urge — staying narrow is what makes it demoable.

## 9. Portfolio framing (for shubhambakre.com and the README header)

> *omnimart-review-agent is a production-shaped agentic LLM application built on top of four other open-source projects in this portfolio: a Go marketplace API, an OpenAI-compatible LLM gateway, a Vertex AI / BigQuery RAG pipeline, and an LLM-as-judge eval harness. It demonstrates agent loops with tool use, model routing across Claude Opus / Sonnet / Haiku, and evaluation as a runtime concern — not a CI afterthought.*

That paragraph goes at the top of the README, in the homepage hero, and in the LinkedIn featured section.

## 10. Open questions to resolve before Day 1

1. Run OmniMart in **memory** or **sqlite** mode for the demo? → Recommend `sqlite` so the demo state is reproducible across runs.
2. Should the RAG pipeline be seeded with real product docs or synthetic ones? → Synthetic, generated once, checked into `examples/seed_docs/`. Avoids GCP-credentials-required demos.
3. Is go-llm-gateway running with a real Anthropic API key or with a mock backend for offline demos? → Real key for the live demo; document a `MOCK_MODE=1` for offline reviewers.
