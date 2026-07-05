# Changelog

## 0.3.0 — 2026-07-05

Born from dogfooding NOBODY against its creator's own production knowledge base
(39 errors found, including a design error in the tool itself — see DOGFOOD.md):

- **Declared ontologies**: a `type: index` concept may declare `types: [...]` — custom
  types become legal brain-wide. Hardcoded ontologies lose to living brains.

## 0.2.0 — 2026-07-05

First real benchmark result: qwen2.5:7b-instruct (local), naked 0/12 → with NOBODY
12/12 on the private-knowledge suite (raw JSONL in `bench/results/`).

Orchestration primitives mined from institutional design (see ORCHESTRATION.md):

- `type: role` — charter / owes / heir (succession linted, `E-HEIR` on crisis)
- `type: council` — members + majority / unanimous / any-veto
- `type: rite` + `nobody rite --witness` — sealed, hash-chained execution
- `refute:` — two-poled proof: verify must pass AND the devil's advocate must fail
- `apocrypha/` quarantine + `nobody canonize` — governed write-back
- Retry/backoff in the OpenAI-compatible bench client (429/5xx)

## 0.1.0 — 2026-07-04

Core: strict frontmatter parser (zero deps), brain loader, linter (laws must
declare executable walls), BM25 context compiler under token budget with link
expansion, naked-vs-nobody bench harness with deterministic `mock-oracle` smoke.
38 tests. `pip install nobody` name reserved on PyPI.
