"""Lint: form is checkable, so form is checked. Laws must have executable walls."""
from __future__ import annotations

import subprocess

from .brain import Brain, Issue, frontier
from .concept import KNOWN_TYPES, NAME_RE


def lint(brain: Brain, walls: bool = False, timeout: int = 30) -> list:
    issues = list(brain.load_issues)
    for name in sorted(brain.concepts):
        c = brain.concepts[name]
        rel = str(c.path.relative_to(brain.root))
        if not NAME_RE.match(c.name):
            issues.append(Issue("E-NAME", rel, f"name {c.name!r} is not kebab-case"))
        if not c.type:
            issues.append(Issue("E-FM-REQ", rel, "missing required field: type"))
        elif c.type not in KNOWN_TYPES:
            issues.append(
                Issue("E-TYPE", rel, f"unknown type {c.type!r} (known: {', '.join(KNOWN_TYPES)})")
            )
        if not c.description.strip():
            issues.append(Issue("E-FM-REQ", rel, "missing required field: description"))
        if c.type == "law" and not c.verify.strip():
            issues.append(
                Issue(
                    "E-LAW-WALL",
                    rel,
                    "a law MUST declare verify: — declared knowledge that "
                    "cannot be executed is lore, not law",
                )
            )
    for link, citers in frontier(brain).items():
        issues.append(
            Issue(
                "W-LINK",
                ",".join(citers),
                f"unresolved [[{link}]] (frontier — known unknown)",
                level="warning",
            )
        )
    if walls:
        issues.extend(_run_walls(brain, timeout))
    return issues


def _run_walls(brain: Brain, timeout: int) -> list:
    issues = []
    for name in sorted(brain.concepts):
        c = brain.concepts[name]
        if not c.verify.strip():
            continue
        rel = str(c.path.relative_to(brain.root))
        try:
            r = subprocess.run(
                c.verify,
                shell=True,
                cwd=str(brain.root),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            issues.append(Issue("E-WALL-FAIL", rel, f"verify timed out after {timeout}s"))
            continue
        if r.returncode != 0:
            tail = (r.stderr or r.stdout or "").strip().splitlines()
            issues.append(
                Issue("E-WALL-FAIL", rel, f"verify exited {r.returncode}: {tail[-1] if tail else ''}")
            )
    return issues


def has_errors(issues) -> bool:
    return any(i.level == "error" for i in issues)
