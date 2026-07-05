# NOBODY

> **The filesystem-native semantic layer that makes any agent punch above its weight.**
> No server. No database. No frontier. Just meaning, measured.

NOBODY turns a directory of markdown files into a **verified semantic brain** for AI
agents, and compiles it into task-relevant context on demand — for *any* agent that can
run one shell command.

```
nobody compile "your task" --brain ./brain
```

## First measured result

```
model: qwen2.5:7b-instruct (local, temperature 0)   naked: 0/12   with NOBODY: 12/12
```

A 7B model running on a laptop answered **every** question about knowledge it was never
trained on — because the layer delivered it. Naked, it honestly answered "unknown" 12
times. Raw run: [`bench/results/20260705-qwen2.5-7b-instruct-local.jsonl`](bench/results/20260705-qwen2.5-7b-instruct-local.jsonl).

**What this measures, honestly:** the private-knowledge suite — facts that live in
*your* brain, not in any model's weights. On this class of task no model size
compensates for a missing context layer; the result validates end-to-end delivery
(ranking → budget-packing → the model actually using it), not reasoning gains.
Reasoning-gain benchmarks (ACE-style) are the next roadmap stage. The harness smoke
(`mock-oracle`, a deterministic perfect-reader — not an LLM) scores the same suite
0.0 → 1.0. **Honesty law:** only numbers backed by raw JSONL in
[`bench/results/`](bench/results/) are cited — negative deltas included.

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

## Orchestration (v0.2) — mined from humanity's oldest multi-agent systems

Churches, crowns and schools of philosophy ran multi-agent coordination for millennia
under adversarial load. v0.2 transplants their surviving mechanisms — as plain concept
types, linted like everything else. No workflow engine: orchestration IS knowledge.

| Primitive | Lineage | What it enforces |
|---|---|---|
| `type: role` + `charter:`/`owes:`/`heir:` | the King's Two Bodies · vassalage · succession law | roles outlive sessions; delegation has explicit scope, owed proof, and a named heir (`E-HEIR` if unresolved) |
| `type: council` + `members:`/`rule:` | curia, witan | who must agree, under `majority`/`unanimous`/`any-veto` |
| `type: rite` + `nobody rite --witness` | liturgy | fixed step sequences, sealed into a tamper-evident hash chain |
| `refute:` on laws | the Devil's Advocate (1587) | a law stands only if the official attack on it FAILS — `nobody lint --walls` runs both poles |
| `apocrypha/` + `nobody canonize` | canon formation | agents write freely to quarantine; nothing enters canon without passing the gates |

Full design rationale: [ORCHESTRATION.md](ORCHESTRATION.md).

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
- [x] Governed write-back — `apocrypha/` quarantine + `nobody canonize` (v0.2)
- [x] Orchestration primitives — roles, councils, rites, advocatus (v0.2)
- [ ] Orchestration bench: sealed-rite pipelines vs freeform agent loops
- [ ] Multi-brain composition (`--brain a --brain b`)
- [ ] GitHub Pages docs site

## The name

Οὖτις — "Nobody" — the name Odysseus gave the Cyclops. The giant had size; Nobody had
semantics. When the benchmark lands, every frontier the layer outperforms will say it
themselves: **"Nobody beat me."**

MIT. No server, no telemetry, no lock-in — there is nobody to lock you in.
