# Dogfood log — NOBODY vs its creator's brain

> The bravest test of a linter is pointing it at the knowledge base it was born from.
> 2026-07-05: we ran `nobody lint` on our own agent's production knowledge framework
> (32 concepts, in daily use by an autonomous agent). Raw findings, unedited.

## What the wall found

```
32 concepts · 39 errors · 0 warnings
walls: 0
```

- **17 concepts had no `description`** — the exact field retrieval ranks on. Our most-used
  knowledge was our least-findable.
- **17 concepts used undeclared types** (`doctrine`, `reference`, `organ`, `ops`, `log`) —
  the real ontology of a living brain is richer than any hardcoded list.
- **`walls: 0`** — not one law in the entire brain declared an executable proof.
  By NOBODY's own standard, everything our agent "knew" was lore, not law.

## What it forced us to build

The type findings were not user error — they were a design error in v0.2: a semantic
layer must let **the map declare the legal kinds**. v0.3 adds declared ontologies:

```markdown
---
type: index
types: [doctrine, reference, organ, ops, log]
---
```

## Result

After declaring the ontology and deriving the missing descriptions from existing titles
(never invented): `32 concepts · 0 errors · 0 warnings`. And the brain became callable:

```
$ nobody compile "how do I delegate a mission to fable worker" --brain ~/.nous/okf --budget 500
<nobody-context ... concepts="3">  # surfaced the exact delegation playbook, 479/500 tokens
```

## Moral

If your agent's knowledge can't survive its own linter, it isn't knowledge yet.
Ours couldn't. Now it can — and the tool got a feature out of the humiliation.
