"""Benchmark: same model, same tasks — naked vs +NOBODY context.

Honesty by construction:
- `mock-oracle` is a deterministic perfect-reader. It isolates the retrieval quality
  of the semantic layer and validates the harness. It is NOT an LLM result and is
  never presented as one.
- Real numbers come only from OpenAI-compatible endpoints, and only raw JSONL committed
  under bench/results/ may be cited. Negative deltas get published too.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request

from .brain import Brain
from .context import compile_context
from .rank import tokenize

SYSTEM = (
    "You are an operations agent. Answer the question concisely and precisely. "
    "If you do not know, answer exactly: unknown"
)


def load_tasks(path) -> list:
    tasks = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    return tasks


class MockOracle:
    """Returns the context line most similar to the question; 'unknown' without context."""

    name = "mock-oracle"

    def complete(self, system: str, user: str) -> str:
        if "<nobody-context" not in user:
            return "unknown"
        ctx, _, question = user.rpartition("</nobody-context>")
        q = set(tokenize(question or user))
        best, best_score = "unknown", 0.0
        for line in ctx.splitlines():
            toks = tokenize(line)
            if len(toks) < 3 or line.lstrip().startswith(("#", "<")):
                continue
            score = len(q & set(toks)) / (len(set(toks)) ** 0.5)
            if score > best_score:
                best, best_score = line.strip(), score
        return best


class OpenAIChat:
    """Any OpenAI-compatible /chat/completions endpoint. stdlib only, temperature 0."""

    def __init__(self, endpoint: str, model: str, key_env: str = ""):
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.name = model
        self.key = os.environ.get(key_env, "") if key_env else ""

    def complete(self, system: str, user: str) -> str:
        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        headers = {"Content-Type": "application/json"}
        if self.key:
            headers["Authorization"] = f"Bearer {self.key}"
        req = urllib.request.Request(
            self.endpoint + "/chat/completions",
            data=json.dumps(payload).encode(),
            headers=headers,
        )
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.loads(r.read().decode())
        return data["choices"][0]["message"]["content"].strip()


def grade(answer: str, expect: dict) -> bool:
    mode, value = expect["mode"], expect["value"]
    a = (answer or "").strip()
    if mode == "exact":
        return a == value
    if mode == "contains":
        return value.lower() in a.lower()
    if mode == "regex":
        return bool(re.search(value, a, re.IGNORECASE))
    raise ValueError(f"unknown grade mode: {mode}")


def run(tasks: list, brain: Brain, model, budget: int = 2000):
    rows = []
    for t in tasks:
        ctx = compile_context(brain, t["prompt"], budget=budget)
        arms = {
            "naked": t["prompt"],
            "nobody": ctx.text + "\n\n" + t["prompt"],
        }
        for arm, user in arms.items():
            ans = model.complete(SYSTEM, user)
            rows.append(
                {
                    "task": t["id"],
                    "arm": arm,
                    "ok": grade(ans, t["expect"]),
                    "answer": ans[:300],
                    "context_concepts": ctx.names if arm == "nobody" else [],
                }
            )
    n = len(tasks)

    def acc(arm):
        return sum(1 for r in rows if r["arm"] == arm and r["ok"]) / n if n else 0.0

    summary = {
        "model": getattr(model, "name", "?"),
        "tasks": n,
        "naked": round(acc("naked"), 3),
        "nobody": round(acc("nobody"), 3),
    }
    summary["delta"] = round(summary["nobody"] - summary["naked"], 3)
    return summary, rows
