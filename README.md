# NOBODY

> **The filesystem-native semantic layer that makes any agent punch above its weight.**
> No server. No database. No frontier. Just meaning, measured.

NOBODY turns a directory of markdown files into a **verified semantic brain** for AI
agents, and compiles it into task-relevant context on demand — for *any* agent that can
run one shell command.

```
nobody compile "your task" --brain ./brain
```

**Benchmark status (honesty law):** no LLM numbers are published yet. The harness smoke
(deterministic `mock-oracle` perfect-reader, which isolates retrieval quality and is
**not** an LLM claim) scores `naked 0.0 → nobody 1.0` on the 12-task example suite.
Real numbers will appear here only when raw JSONL runs land in [`bench/results/`](bench/results/)
— negative deltas included. Run it yourself in two commands (below).

## The thesis

An agent whose knowledge is **semantically structured** — named concepts, typed files,
explicit links, executable claims — outperforms the same agent fed raw context, at equal
model size. Context quality is the cheapest capability lever: ACE (ICLR 2026) reports
**+17.1% on AppWorld** from context engineering alone, no weight updates
([arXiv:2510.04618](https://arxiv.org/abs/2510.04618)).

NOBODY is that thesis made falsifiable: a semantic format, a compiler, and a benchmark
that measures the delta. If the delta is zero, the thesis is wrong — and the number
gets published anyway.

## The four primitives

| Primitive | Rule | Enforced by |
|---|---|---|
| **Concept** | One file = one concept. Markdown + strict frontmatter. | `nobody lint` |
| **Name** | The filename IS the claim (kebab-case, no lies). | `nobody lint` |
| **Link** | `[[other-concept]]` builds the graph. Unresolved = *known unknown*, not error. | `nobody frontier` |
| **Wall** | A `law` MUST declare `verify:` — an executable command proving it holds. | `nobody lint --walls` |

The fourth primitive is the one nobody else has: **declared knowledge that cannot be
executed is lore, not law.** Your agent's brain stops being able to lie to it.

## Quickstart

```bash
git clone https://github.com/nobody-agent/nobody && cd nobody
pip install -e .

nobody init mybrain                 # scaffold a brain
nobody lint mybrain --walls         # validate it, execute its laws
nobody compile "deploy question" --brain examples/brain   # get context
nobody frontier examples/brain      # what the brain knows it doesn't know
```

Wire it into **any** agent (Claude Code, Cursor, a bash loop — anything with a shell):

```bash
nobody compile "$TASK" --brain ./brain >> prompt.md
```

## The benchmark

Same model, same tasks, two arms: **naked** (prompt only) vs **nobody** (prompt +
compiled context). Temperature 0. Graded automatically.

```bash
# harness smoke (deterministic, no API key):
nobody bench --tasks bench/tasks.jsonl --brain examples/brain --model mock-oracle

# real run against any OpenAI-compatible endpoint:
export MY_KEY=sk-...
nobody bench --tasks bench/tasks.jsonl --brain examples/brain \
  --model gpt-4o-mini --endpoint https://api.openai.com/v1 --key-env MY_KEY \
  --out bench/results/$(date +%Y%m%d)-gpt-4o-mini.jsonl
```

**Honesty law:** only numbers backed by raw JSONL committed under `bench/results/` may
be cited. The mock-oracle validates the harness and measures retrieval quality; it is
never presented as an LLM result.

## Why not Mem0 / Letta / Zep / Cognee?

They are good at what they do — and they all made the same trade: your agent's memory
lives in **their** server, database, or API.

| | NOBODY | Mem0 / Letta / Zep / Cognee |
|---|---|---|
| Storage | plain markdown files | server / vector DB / graph DB |
| Versioning | `git` (you already have it) | platform-specific |
| Human-readable | yes, every byte | partially |
| Verified knowledge | `verify:` walls, executed by lint | no equivalent |
| Runtime deps | **zero** (Python stdlib) | SDK + service |
| API key required | no | usually |

If you need multi-tenant SaaS memory at enterprise scale, use them. If you want a brain
you can read, diff, version, verify and carry anywhere — `git clone` is your migration.

## Spec

The full format, lint rules, compilation and bench protocol: [SPEC.md](SPEC.md).

## Roadmap

- [ ] Real-model bench results in `bench/results/` (multiple models, small vs large)
- [ ] `nobody add` — structured write-back for agents, linted at write time
- [ ] Multi-brain composition (`--brain a --brain b`)
- [ ] GitHub Pages docs site

## The name

Οὖτις — "Nobody" — the name Odysseus gave the Cyclops. The giant had size; Nobody had
semantics. When the benchmark lands, every frontier the layer outperforms will say it
themselves: **"Nobody beat me."**

MIT. No server, no telemetry, no lock-in — there is nobody to lock you in.
