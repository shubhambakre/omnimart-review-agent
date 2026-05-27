# Blog post — "Composing four side projects into one LLM stack"

**Target venue:** Personal blog (shubhambakre.com/blog) + crosspost to LinkedIn article + r/LocalLLaMA / HN if it lands well.

**Target reader:** A senior engineer or hiring manager at an AI-first company who landed here from a job application or LinkedIn share. They have 4 minutes. They will not scroll twice.

**The single job of this post:** Convince that reader to open the GitHub repo and look at the code. Everything else is decoration.

---

## Working title options (pick later, after the draft)

1. *Composing four side projects into one LLM stack* — descriptive, low-risk
2. *I built a marketplace, then I built an agent on top of it* — narrative, higher CTR
3. *Eval-in-the-loop: why my agent retries itself before answering you* — technical hook, narrower audience
4. *What I learned wiring four LLM side projects into one production-shaped system* — long, but signals craft

**Recommendation:** Lead with #2 on LinkedIn (story-shaped), use #1 as the blog slug for SEO/scanability.

---

## Structure (target: 1,200–1,600 words; 6–8 minute read max)

### Opening — 1 paragraph (~80 words)
- **Hook:** A single concrete result. Example: *"Last weekend I asked an agent 'what are customers complaining about for product SKU-4471?' It read 38 reviews, retrieved category context, drafted a report, scored its own draft 0.62 / 1.0 on faithfulness, rewrote it, scored 0.91, and returned the final answer. Here's how I built it — using four side projects I already had."*
- **No throat-clearing.** No "I've been thinking about agents lately."

### Section 1 — The stack, in one diagram (~150 words + image)
- Architecture diagram (same one from SPEC.md §3).
- One sentence per box explaining what it does.
- Link each box to its GitHub repo. This is where the portfolio gets the click-through.

### Section 2 — Why composition is the interesting problem (~200 words)
- The Anthropic / OpenAI cookbook examples teach you to call one LLM with one prompt. Production is many LLMs, many tools, with state and retries.
- The interesting engineering questions only show up when you compose: *which model where, who owns retries, where does evaluation live, how do you trace it.*
- Frame this as the "missing chapter" between tutorials and production.

### Section 3 — Eval-in-the-loop, with code (~350 words, the meat)
- This is the section a reviewer will actually screenshot.
- Show the retry-with-critique loop in ~30 lines of Python.
- Highlight: the judge is the same code you'd use in CI — runtime and CI eval converge.
- Include a real trace: draft 1 score, critique, draft 2 score. Numbers, not handwaving.
- One paragraph on the limits: judge is itself an LLM, calibration matters, false-pass risk on adversarial inputs.

### Section 4 — Model routing across Claude tiers (~200 words)
- Planner: Sonnet 4.6 (good reasoning, cheap enough to call often).
- Tool-selection / small classifications: Haiku 4.5 (10x cheaper, fast).
- Critic / final judge: Opus 4.7 (worth the cost on the highest-stakes call).
- Show a small table: cost per run + p50 latency for one full Mode A invocation.
- *This is the section that signals "this person has run real numbers on real models."*

### Section 5 — What I'd do next (~150 words)
- Honest list. Not a vision statement. Example items:
  - Multi-product comparative reports
  - Replace the synthetic seed corpus with real product manuals + measure precision delta
  - Try a tool-use-trained smaller open model (Qwen / Llama) as the planner and benchmark against Sonnet
  - Add a sandboxed code-execution tool so the agent can do quantitative analysis on review counts
- Each item should be a hook for a future post. This is how a blog becomes a series.

### Closing — 1 paragraph (~80 words)
- Repo link, *clearly*.
- Invitation to open issues / DM with feedback.
- Anchor your role + what you're looking for in one sentence: *"I'm a senior software engineer at Walmart Labs interested in applied AI / LLM platform roles — if this is the kind of work your team does, I'd love to talk."*
- This is not unprofessional. This is what the post is *for*.

---

## Production checklist

- [ ] Diagram exported as SVG (or high-res PNG) — readable on phone.
- [ ] Code blocks fenced with syntax hint, < 25 lines each. If longer, link to the file on GitHub at a pinned commit SHA.
- [ ] Real numbers in tables (no "fast" / "cheap" — give the milliseconds and the dollars).
- [ ] One animated GIF of a live run (record with `asciinema` or screen-capture; <2MB).
- [ ] OG image set so the LinkedIn preview is the architecture diagram, not a random screenshot.
- [ ] Repo's README leads with a link *back* to this post — bidirectional traffic.
- [ ] All four sibling repos have a "this is used by [omnimart-review-agent]" link in their READMEs. Free portfolio cohesion.

## What to deliberately leave out

- "What is an agent?" — your audience knows.
- "What is RAG?" — your audience knows.
- Apologies, hedging, "I'm new to this" — your audience does *not* care, and it costs credibility cheap.
- Detailed setup instructions — those live in the README.
- A vendor comparison ("Claude vs GPT-4 vs Gemini") unless you're prepared to defend it with numbers. Half-baked comparisons are a credibility tax.

## Distribution plan

1. Publish on personal blog with canonical URL.
2. LinkedIn article (full text, not just a link — LinkedIn punishes external links).
3. Tweet/X thread: 1 architecture image, 4 follow-up tweets each covering one section.
4. Cross-post to HN as a Show HN if and only if the agent has a hosted demo URL. Otherwise it dies on the front page.
5. DM the link to 5 specific people whose feedback you actually want — not as a request to share, just for their read. The shares follow.

## Timing relative to job applications

Publish **before** the next application batch — the post becomes the artifact you reference in cover letters and the recruiter screen. If you publish *after* applying, recruiters never see it.
