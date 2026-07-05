# Institutional Design Patterns for Agent Orchestration

> Churches, crowns and schools of philosophy are humanity's longest-running
> multi-agent systems. They solved alignment, delegation, verification, succession
> and knowledge governance centuries before software existed — and the ones still
> standing survived every stress test history could throw at them. NOBODY v0.2
> mines them as prior art: **keep the mechanism, drop the metaphysics, make it lint.**

Everything below is expressed in the same substrate as the rest of the brain —
markdown concepts, checked by the same linter, proven by the same walls. There is
no separate workflow engine: orchestration IS knowledge.

## The transmutation table

| Institution (problem it solved) | Mechanism | NOBODY primitive |
|---|---|---|
| **Canon vs apocrypha** — which texts enter scripture (epistemic quarantine) | proposals wait outside; admission requires examination | `apocrypha/` dir + `nobody canonize` |
| **Advocatus Diaboli**, 1587 — canonization needs a paid skeptic (adversarial verification) | a case stands only if the official attack on it fails | `refute:` field — the attack MUST exit non-zero |
| **Liturgy** — high-stakes coordination without improvisation | fixed sequence, same order, every time | `type: rite` + `nobody rite` |
| **The King's Two Bodies** (Kantorowicz) — continuity across mortal incumbents | the role never dies; the incumbent does | `type: role` — the file is immortal, sessions are mortal |
| **Royal succession law** — no interregnum, no orphaned realm | the heir is named *before* the crisis | `heir:` — unresolved heir = lint error (`E-HEIR`) |
| **Vassalage** — delegation with mutual, explicit obligations | fief granted ↔ service owed | `charter:` (what it may do) + `owes:` (the proof it must deliver) |
| **Curia / Witan** — decisions too big for one head | named members, explicit decision rule | `type: council` — `members:` + `rule: majority\|unanimous\|any-veto` |
| **Socratic elenchus** — expose contradiction *before* acting | interrogate the claim until it breaks or holds | lint runs before compile; broken brains ship no context |
| **Popperian falsifiability** — knowledge = what survives refutation | every claim carries its own test | `verify:` walls + the naked-vs-nobody bench |
| **Stoic dichotomy of control** — act only on what is yours | scope discipline | a role acts inside its `charter:`, reports the rest |
| **Solve et coagula** — decompose, purify, recompose | map → verify → reduce | the orchestrator pattern below |
| **"As above, so below"** — declaration must match reality | every plan step maps to a trace record | hash-chained rite witness (`verify_witness`) |

## What v0.2 ships vs what stays in your agent

**Ships (deterministic, stdlib, tested):** the types and lint rules above, rite
execution with sealed witness, apocrypha quarantine, canonization gate, the
two-poled proof (`verify` must pass AND `refute` must fail).

**Stays in your agent (LLM territory, by design):** planning, council *voting*,
choosing which rite to run. NOBODY gives the orchestrator ground truth it cannot
fake — it does not pretend to be the orchestrator. A council file defines who must
agree and under what rule; producing the votes is your agents' job.

## The orchestrator pattern (solve et coagula)

Any agent loop — bash, Claude Code, anything — composes the primitives:

```bash
# solve: one compiled context per subtask, disjoint scopes per role
nobody compile "$SUBTASK" --brain ./brain > ctx.md          # the matter
# ... agent works with ctx.md, writes lessons to ./brain/apocrypha/ ...

# coagula: nothing merges without passing the gates
nobody lint ./brain --walls                                  # laws hold, attacks repelled
nobody canonize new-lesson --brain ./brain                   # apocrypha -> canon
nobody rite release-rite --brain ./brain --witness seal.jsonl  # sealed execution
```

The task lifecycle mirrors the old alchemical sequence, because the sequence is
just correct engineering: **decompose** (subtasks, disjoint charters) →
**purify** (walls, advocatus, council) → **recompose** (canonize) →
**seal** (witness chain). No seal without purification: `rite` stops at the first
failing step, and a tampered witness is detected by recomputing the chain.

## Why institutions, honestly

Not because old means true — astrology is old and wrong. Because institutions are
the only multi-agent coordination mechanisms with **millennium-scale uptime under
adversarial load**: schisms, usurpers, heretics, forgeries. Every mechanism in the
table earned its place by failing publicly for centuries until its current form
stopped failing. That is exactly the evidence standard agent frameworks lack, three
years into their existence. We cite our sources; we just compile them.
