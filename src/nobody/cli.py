"""nobody — CLI. Everything reads/writes plain files; stdout is the integration API."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from . import bench as bench_mod
from . import brain as brain_mod
from .context import compile_context
from .lint import has_errors, lint
from .rite import run_rite, verify_witness

STARTER_INDEX = """---
type: index
description: Map of this brain. Every concept worth loading is linked here.
---

# Brain index

- [[hello-nobody]] — what this brain is
- [[laws-have-walls]] — the honesty law
"""

STARTER_CONCEPT = """---
type: concept
description: This brain stores knowledge as one concept per file, linted and verifiable.
tags: [meta]
---

One file = one concept. The filename is the claim. Link concepts with
[[laws-have-walls]] style wikilinks. Run `nobody lint .` to keep it honest.
"""

STARTER_LAW = """---
type: law
description: Every law in this brain declares an executable wall that proves it holds.
verify: test -f index.md
---

Declared knowledge that cannot be executed is lore, not law. This law's own wall
checks that the brain keeps its map: `index.md` must exist.
"""


def _load(brain_dir):
    return brain_mod.load(Path(brain_dir))


def cmd_init(args) -> int:
    root = Path(args.dir)
    root.mkdir(parents=True, exist_ok=True)
    files = {
        "index.md": STARTER_INDEX,
        "hello-nobody.md": STARTER_CONCEPT,
        "laws-have-walls.md": STARTER_LAW,
    }
    written = []
    for name, content in files.items():
        p = root / name
        if p.exists():
            continue
        p.write_text(content, encoding="utf-8")
        written.append(name)
    print(f"brain initialized at {root} ({len(written)} files written)")
    return 0


def cmd_lint(args) -> int:
    b = _load(args.brain)
    issues = lint(b, walls=args.walls)
    if args.json:
        print(
            json.dumps(
                {
                    "ok": not has_errors(issues),
                    "concepts": len(b.concepts),
                    "issues": [vars(i) for i in issues],
                },
                indent=2,
            )
        )
    else:
        for i in issues:
            print(i)
        errs = sum(1 for i in issues if i.level == "error")
        print(f"{len(b.concepts)} concepts · {errs} errors · {len(issues) - errs} warnings")
    return 1 if has_errors(issues) else 0


def cmd_compile(args) -> int:
    out = compile_context(
        _load(args.brain),
        args.query,
        budget=args.budget,
        include_apocrypha=args.include_apocrypha,
    )
    print(out.text)
    return 0


def cmd_rite(args) -> int:
    b = _load(args.brain)
    c = b.get(args.name)
    if c is None or c.type != "rite":
        print(f"no rite named {args.name!r} in {args.brain}", file=sys.stderr)
        return 2
    code, results = run_rite(b, c, witness=args.witness)
    for r in results:
        mark = "ok" if r["exit"] == 0 else f"FAIL({r['exit']})"
        print(f"  step {r['step']}: {r['cmd']}  ->  {mark}")
    if args.witness:
        ok, n = verify_witness(Path(args.witness))
        print(f"witness: {args.witness} — chain {'intact' if ok else 'BROKEN'} ({n} records)")
    print(f"rite {c.name}: {'complete' if code == 0 else 'interrupted'}")
    return code


def cmd_canonize(args) -> int:
    b = _load(args.brain)
    c = b.get(args.name)
    if c is None:
        print(f"no concept named {args.name!r}", file=sys.stderr)
        return 2
    if not c.apocryphal:
        print(f"{args.name} is already canon", file=sys.stderr)
        return 2
    rel = str(c.path.relative_to(b.root))
    issues = [
        i
        for i in lint(b, walls=True)
        if i.level == "error" and (i.path == rel or args.name in i.path)
    ]
    if issues:
        for i in issues:
            print(i)
        print(f"canonization REFUSED: {len(issues)} errors")
        return 1
    dest = b.root / f"{c.name}.md"
    c.path.rename(dest)
    print(f"canonized: {rel} -> {dest.name}")
    return 0


def cmd_frontier(args) -> int:
    fr = brain_mod.frontier(_load(args.brain))
    if args.json:
        print(json.dumps(fr, indent=2))
    else:
        for link, citers in fr.items():
            print(f"[[{link}]] <- {', '.join(citers)}")
        print(f"{len(fr)} known unknowns")
    return 0


def cmd_stats(args) -> int:
    st = brain_mod.stats(_load(args.brain))
    print(json.dumps(st, indent=2))
    return 0


def cmd_bench(args) -> int:
    b = _load(args.brain)
    tasks = bench_mod.load_tasks(args.tasks)
    if args.model == "mock-oracle":
        model = bench_mod.MockOracle()
    else:
        if not args.endpoint:
            print("--endpoint is required for non-mock models", file=sys.stderr)
            return 2
        model = bench_mod.OpenAIChat(args.endpoint, args.model, args.key_env)
    summary, rows = bench_mod.run(tasks, b, model, budget=args.budget)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
            f.write(json.dumps({"summary": summary}) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="nobody",
        description="NOBODY — the filesystem-native semantic layer for agents.",
    )
    p.add_argument("--version", action="version", version=f"nobody {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="scaffold a brain")
    s.add_argument("dir")
    s.set_defaults(fn=cmd_init)

    s = sub.add_parser("lint", help="validate a brain (add --walls to execute laws)")
    s.add_argument("brain")
    s.add_argument("--walls", action="store_true", help="execute every verify: command")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_lint)

    s = sub.add_parser("compile", help="compile task-relevant context to stdout")
    s.add_argument("query")
    s.add_argument("--brain", required=True)
    s.add_argument("--budget", type=int, default=2000, help="token budget (default 2000)")
    s.add_argument(
        "--include-apocrypha", action="store_true", help="also pack quarantined concepts"
    )
    s.set_defaults(fn=cmd_compile)

    s = sub.add_parser("rite", help="execute a rite (deterministic step sequence)")
    s.add_argument("name")
    s.add_argument("--brain", required=True)
    s.add_argument("--witness", default="", help="seal steps into this hash-chained JSONL")
    s.set_defaults(fn=cmd_rite)

    s = sub.add_parser(
        "canonize", help="promote an apocrypha/ concept to canon (lint + walls first)"
    )
    s.add_argument("name")
    s.add_argument("--brain", required=True)
    s.set_defaults(fn=cmd_canonize)

    s = sub.add_parser("frontier", help="known unknowns: dangling [[links]]")
    s.add_argument("brain")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_frontier)

    s = sub.add_parser("stats", help="brain statistics")
    s.add_argument("brain")
    s.set_defaults(fn=cmd_stats)

    s = sub.add_parser("bench", help="run the naked-vs-nobody benchmark")
    s.add_argument("--tasks", required=True)
    s.add_argument("--brain", required=True)
    s.add_argument("--model", default="mock-oracle")
    s.add_argument("--endpoint", default="", help="OpenAI-compatible base URL")
    s.add_argument("--key-env", default="", help="env var holding the API key")
    s.add_argument("--budget", type=int, default=2000)
    s.add_argument("--out", default="", help="write raw JSONL rows here")
    s.set_defaults(fn=cmd_bench)

    args = p.parse_args(argv)
    return args.fn(args)
