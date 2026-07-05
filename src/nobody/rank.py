"""BM25 ranking (k1=1.5, b=0.75). Pure stdlib — rare terms in dense docs win."""
from __future__ import annotations

import math
import re
from collections import Counter

WORD_RE = re.compile(r"[a-z0-9_]{2,}")
K1, B = 1.5, 0.75


def tokenize(text: str) -> list:
    return WORD_RE.findall((text or "").lower())


def bm25(query: str, docs: dict) -> dict:
    """docs: name -> text. Returns name -> score, positive scores only."""
    terms = set(tokenize(query))
    counters = {n: Counter(tokenize(t)) for n, t in docs.items()}
    counters = {n: c for n, c in counters.items() if c}
    if not terms or not counters:
        return {}
    n_docs = len(counters)
    df: Counter = Counter()
    for c in counters.values():
        df.update(set(c))
    avgdl = sum(sum(c.values()) for c in counters.values()) / n_docs
    scores = {}
    for name, c in counters.items():
        dl = sum(c.values())
        s = 0.0
        for t in terms:
            f = c.get(t, 0)
            if not f:
                continue
            idf = math.log(1 + (n_docs - df[t] + 0.5) / (df[t] + 0.5))
            s += idf * (f * (K1 + 1)) / (f + K1 * (1 - B + B * dl / avgdl))
        if s > 0:
            scores[name] = s
    return scores
