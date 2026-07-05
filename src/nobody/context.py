"""Compile a brain into task-relevant context under a token budget.

Rank (BM25, name/description boosted) -> expand links of top hits -> greedy pack.
Deterministic: same brain + same query = same bundle, byte for byte.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .brain import Brain
from .rank import bm25

TOP_HITS_FOR_EXPANSION = 5
LINK_INHERIT = 0.5


def est_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4)


def _doc_text(c) -> str:
    name_words = c.name.replace("-", " ")
    parts = [name_words] * 3 + [c.description] * 3 + [" ".join(c.tags)] * 2 + [c.body]
    return "\n".join(parts)


@dataclass
class Compiled:
    query: str
    budget: int
    used: int = 0
    names: list = field(default_factory=list)
    text: str = ""


def compile_context(brain: Brain, query: str, budget: int = 2000) -> Compiled:
    packable = {n: c for n, c in brain.concepts.items() if c.type != "index"}
    scores = bm25(query, {n: _doc_text(c) for n, c in packable.items()})
    top = sorted(scores, key=lambda n: (-scores[n], n))[:TOP_HITS_FOR_EXPANSION]
    for parent in top:
        for link in packable[parent].links:
            if link in packable:
                scores[link] = max(scores.get(link, 0.0), scores[parent] * LINK_INHERIT)
    order = sorted(scores, key=lambda n: (-scores[n], n))

    out = Compiled(query=query, budget=budget)
    blocks = []
    for name in order:
        c = packable[name]
        block = f"# {name} ({c.type})\n{c.body.strip()}\n"
        cost = est_tokens(block)
        if out.used + cost > budget:
            continue
        blocks.append(block)
        out.names.append(name)
        out.used += cost
    attr_query = query.replace('"', "'")
    out.text = (
        f'<nobody-context query="{attr_query}" budget="{budget}" '
        f'used="{out.used}" concepts="{len(out.names)}">\n'
        + "\n".join(blocks)
        + "</nobody-context>"
    )
    return out
