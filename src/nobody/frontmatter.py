"""Strict frontmatter parser — a deliberate YAML subset, zero dependencies.

Grammar (v0.1):
    file   := "---" NL line* "---" NL body
    line   := key ":" value? | "- " item | blank | "#" comment
    value  := scalar | "[" scalar ("," scalar)* "]"

Scalars are strings; surrounding single/double quotes are stripped.
A bare `key:` opens a dash list. No nesting, no multiline scalars.
Unknown syntax is an error, never a guess.
"""
from __future__ import annotations

import re

KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$")


class FrontmatterError(ValueError):
    def __init__(self, msg: str, line: int):
        super().__init__(f"line {line}: {msg}")
        self.line = line


def _scalar(raw: str) -> str:
    v = raw.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        v = v[1:-1]
    return v


def parse(text: str):
    """Return (meta, body). Raise FrontmatterError on anything ambiguous."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError("missing opening '---'", 1)
    meta: dict = {}
    open_list = None  # key of the dash list currently accepting items
    end = None
    for i, raw in enumerate(lines[1:], start=2):
        stripped = raw.strip()
        if stripped == "---":
            end = i
            break
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            if open_list is None:
                raise FrontmatterError("dash item without an open list key", i)
            meta[open_list].append(_scalar(stripped[2:]))
            continue
        m = KEY_RE.match(stripped)
        if not m:
            raise FrontmatterError(f"unrecognized line: {stripped!r}", i)
        key, raw_val = m.group(1), m.group(2).strip()
        if key in meta:
            raise FrontmatterError(f"duplicate key: {key}", i)
        if raw_val == "":
            meta[key] = []
            open_list = key
        elif raw_val.startswith("[") and raw_val.endswith("]"):
            inner = raw_val[1:-1].strip()
            meta[key] = [_scalar(p) for p in inner.split(",")] if inner else []
            open_list = None
        else:
            meta[key] = _scalar(raw_val)
            open_list = None
    if end is None:
        raise FrontmatterError("unclosed frontmatter (no closing '---')", len(lines))
    return meta, "\n".join(lines[end:])
