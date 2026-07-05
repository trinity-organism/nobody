# NOBODY — Specification v0.2

> The semantic layer that makes any agent punch above its weight.
> No server. No database. No frontier. Just meaning, measured.

## 1. Thesis

An agent whose knowledge is **semantically structured** — named concepts, typed files,
explicit links, verified claims — outperforms the same agent fed raw context, at equal
model size. Context quality, not model size, is the cheapest capability lever
(cf. ACE, ICLR 2026: +17.1% on AppWorld from context engineering alone).

NOBODY is the falsifiable implementation of that thesis: a filesystem-native semantic
brain + a compiler that turns it into task-relevant context + a benchmark that measures
the delta. **If the delta is zero, the thesis is wrong and the number gets published anyway.**

## 2. The four primitives

| Primitive | Rule | Enforced by |
|---|---|---|
| **Concept** | One file = one concept. Markdown + strict frontmatter. | `nobody lint` |
| **Name** | The filename IS the claim (`kebab-case`, name = what the file contains). | `nobody lint` (form), humans (meaning) |
| **Link** | `[[other-concept]]` builds the graph. Unresolved links are *known unknowns*, not errors. | `nobody frontier` |
| **Wall** | A `law` MUST declare `verify:` — an executable command proving it holds. Declared knowledge that can't be executed is lore, not law. | `nobody lint --walls` |

## 3. Concept file anatomy

```markdown
---
type: concept | law | playbook | memory | index | role | rite | council
description: One-line summary. Used for ranking and indexes.
tags: [ops, deploy]          # optional
verify: <shell command>      # REQUIRED for type: law, optional otherwise
refute: <shell command>      # optional advocatus diaboli — MUST exit non-zero
charter: <text>              # role only, REQUIRED: what it may do
owes: <text>                 # role only, REQUIRED: the proof it must deliver
heir: <role-name>            # role only, optional: succession on failure
members: [role-a, role-b]    # council only, REQUIRED
rule: majority | unanimous | any-veto   # council only, REQUIRED
---

Markdown body. Link with [[other-concept]].
A rite declares its steps as body lines starting with `$ `.
```

Rules:
- **Declared ontology (v0.3)**: any `type: index` concept may declare `types: [doctrine, ...]`
  in its frontmatter — those types become legal brain-wide. The map declares the legal kinds.
- **Name** = filename stem. MUST match `^[a-z0-9]+(-[a-z0-9]+)*$`. Unique brain-wide.
- **Frontmatter** is a strict YAML *subset*: `key: value`, inline lists `[a, b]`,
  dash lists. No nesting, no multiline scalars. Unknown syntax is an error, never a guess.
- `type` and non-empty `description` are required.
- `verify` runs with `cwd` = brain root. Exit 0 = the wall holds.

## 4. Lint rules

| Code | Level | Meaning |
|---|---|---|
| E-NAME | error | filename is not kebab-case |
| E-FM-PARSE | error | frontmatter missing / unclosed / unrecognized line |
| E-FM-REQ | error | missing `type` or empty `description` |
| E-TYPE | error | unknown `type` |
| E-LAW-WALL | error | `type: law` without `verify:` |
| E-DUP | error | duplicate concept name in brain |
| E-WALL-FAIL | error (`--walls` only) | a `verify` command exited non-zero |
| E-ADVOCATUS | error (`--walls` only) | a `refute` command succeeded — the law falls |
| E-ROLE-REQ | error | role missing `charter:` or `owes:` |
| E-HEIR | error | `heir:` does not resolve to a role (succession crisis) |
| E-COUNCIL-REQ / E-COUNCIL-MEMBER / E-COUNCIL-RULE | error | council malformed |
| E-RITE-EMPTY | error | rite with no `$ ` step lines |
| W-SUCCESSION | warning | role with no heir (interregnum risk) |
| W-LINK | warning | unresolved `[[link]]` (the frontier — legitimate) |

Exit code: 1 if any error, 0 otherwise. Warnings never fail the build.

## 5. Context compilation

`nobody compile "<query>" --brain DIR --budget 2000`

1. Rank concepts by BM25 (k1=1.5, b=0.75) over `name + description + tags + body`
   (name/description tokens weighted 3×, tags 2×).
2. Link expansion: neighbors of the top-5 hits inherit half their parent's score.
3. Greedy-pack highest scores into the budget (tokens ≈ chars/4). `type: index` files
   are navigation, never packed.
4. Emit a deterministic bundle to stdout:

```
<nobody-context query="..." budget="2000" used="1874" concepts="4">
# error-budget (concept)
...

# deploy-freeze (law)
...
</nobody-context>
```

Integration with ANY agent = one shell line. Example (Claude Code, Cursor, any CLI):

```
nobody compile "$TASK" --brain ./brain >> context.md
```

## 6. Benchmark protocol

- Tasks: `bench/tasks.jsonl` — `{"id", "prompt", "expect": {"mode": "contains|regex|exact", "value"}}`.
- Two arms, same model, temperature 0:
  - **naked**: system + prompt.
  - **nobody**: system + compiled context + prompt.
- Models: `mock-oracle` (deterministic perfect-reader; isolates retrieval quality of the
  layer, validates the harness — NOT an LLM result) or any OpenAI-compatible endpoint
  (`--endpoint`, `--model`, `--key-env`).
- Output: JSONL rows + summary `{naked, nobody, delta}`.
- **Honesty law**: no number appears in the README unless the raw JSONL that produced it
  is committed under `bench/results/`. Negative deltas get published too.

## 7. CLI

```
nobody init <dir>                     scaffold a brain
nobody lint <brain> [--walls] [--json]
nobody compile "<query>" --brain DIR [--budget N] [--include-apocrypha]
nobody frontier <brain> [--json]      known unknowns (dangling links)
nobody stats <brain> [--json]
nobody rite <name> --brain DIR [--witness FILE]    execute a rite, sealed
nobody canonize <name> --brain DIR    promote apocrypha/ concept to canon
nobody bench --tasks F --brain DIR --model mock-oracle|NAME
             [--endpoint URL] [--key-env VAR] [--budget N] [--out F]
```

## 7b. Orchestration semantics (v0.2)

- **Apocrypha**: concepts under `apocrypha/` are quarantined — linted like everything
  else, excluded from `compile` unless `--include-apocrypha`. `canonize` promotes a
  concept only after concept-level lint + its walls pass.
- **Rites**: body lines starting with `$ ` run sequentially with `cwd` = brain root;
  execution stops at the first failure. With `--witness`, each step is sealed into a
  hash-chained JSONL (`prev` + sha256); `verify_witness` recomputes the chain and
  detects tampering.
- **Two-poled proof**: with `--walls`, `verify:` must exit 0 AND `refute:` (if present)
  must exit non-zero. A law whose refutation succeeds falls (E-ADVOCATUS).
- Design rationale and the institutional lineage of each primitive: [ORCHESTRATION.md](ORCHESTRATION.md).

## 8. Non-goals (v0.1)

- No embeddings, no vector DB, no server, no API key required by the core. BM25 + files.
- No write-back automation (agents append concepts themselves; lint keeps them honest).
- No Windows CI (POSIX first).

## 9. Acceptance criteria

1. A stranger clones the repo and reproduces the bench in under 10 minutes with 2 commands.
2. `nobody lint examples/brain --walls` exits 0.
3. `pytest` green.
4. The measured delta sits at the top of the README, whatever its sign.

## 10. Name

Οὖτις — "Nobody" — the name Odysseus gave the Cyclops. The giant had size;
Nobody had semantics. Every benchmark line the frontier loses, it will say:
**"Nobody beat me."**
