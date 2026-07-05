"""Lint: form is checkable, so form is checked. Laws must have executable walls."""
from __future__ import annotations

import subprocess

from .brain import Brain, Issue, frontier
from .concept import KNOWN_TYPES, NAME_RE
from .rite import parse_steps

COUNCIL_RULES = ("majority", "unanimous", "any-veto")


def _check_role(brain: Brain, c, rel: str) -> list:
    if c.type != "role":
        return []
    issues = []
    if not c.charter.strip():
        issues.append(Issue("E-ROLE-REQ", rel, "a role MUST declare charter: (what it may do)"))
    if not c.owes.strip():
        issues.append(
            Issue("E-ROLE-REQ", rel, "a role MUST declare owes: (the proof it must deliver)")
        )
    if c.heir:
        heir = brain.concepts.get(c.heir)
        if heir is None or heir.type != "role":
            issues.append(
                Issue("E-HEIR", rel, f"heir {c.heir!r} is not a role — succession crisis")
            )
    else:
        issues.append(
            Issue("W-SUCCESSION", rel, "no heir: declared — interregnum risk", level="warning")
        )
    return issues


def _check_council(brain: Brain, c, rel: str) -> list:
    if c.type != "council":
        return []
    issues = []
    if not c.members:
        issues.append(Issue("E-COUNCIL-REQ", rel, "a council MUST declare members: [role, ...]"))
    for m in c.members:
        member = brain.concepts.get(m)
        if member is None or member.type != "role":
            issues.append(Issue("E-COUNCIL-MEMBER", rel, f"member {m!r} is not a role"))
    if c.rule not in COUNCIL_RULES:
        issues.append(
            Issue(
                "E-COUNCIL-RULE",
                rel,
                f"rule {c.rule!r} unknown (known: {', '.join(COUNCIL_RULES)})",
            )
        )
    return issues


def declared_types(brain: Brain) -> tuple:
    """A brain's index may extend the ontology: `types: [doctrine, reference]` in
    any type: index concept. The map declares the legal kinds."""
    extra = []
    for c in brain.concepts.values():
        if c.type == "index":
            t = c.meta.get("types", [])
            extra.extend(t if isinstance(t, list) else [t])
    return tuple(sorted(set(extra)))


def lint(brain: Brain, walls: bool = False, timeout: int = 30) -> list:
    issues = list(brain.load_issues)
    allowed = tuple(KNOWN_TYPES) + declared_types(brain)
    for name in sorted(brain.concepts):
        c = brain.concepts[name]
        rel = str(c.path.relative_to(brain.root))
        if not NAME_RE.match(c.name):
            issues.append(Issue("E-NAME", rel, f"name {c.name!r} is not kebab-case"))
        if not c.type:
            issues.append(Issue("E-FM-REQ", rel, "missing required field: type"))
        elif c.type not in allowed:
            issues.append(
                Issue("E-TYPE", rel, f"unknown type {c.type!r} (known: {', '.join(allowed)})")
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
        issues.extend(_check_role(brain, c, rel))
        issues.extend(_check_council(brain, c, rel))
        if c.type == "rite" and not parse_steps(c):
            issues.append(
                Issue("E-RITE-EMPTY", rel, "a rite MUST declare at least one '$ ' step line")
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
        rel = str(c.path.relative_to(brain.root))
        if c.verify.strip():
            code, detail = _sh(c.verify, brain, timeout)
            if code != 0:
                issues.append(Issue("E-WALL-FAIL", rel, f"verify exited {code}: {detail}"))
        if c.refute.strip():
            # advocatus diaboli: the attack MUST fail. If it succeeds, the law falls.
            code, detail = _sh(c.refute, brain, timeout)
            if code == 0:
                issues.append(
                    Issue(
                        "E-ADVOCATUS",
                        rel,
                        "refute: succeeded — the devil's advocate broke this law; it falls",
                    )
                )
    return issues


def _sh(cmd: str, brain: Brain, timeout: int):
    try:
        r = subprocess.run(
            cmd,
            shell=True,
            cwd=str(brain.root),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout}s"
    tail = (r.stderr or r.stdout or "").strip().splitlines()
    return r.returncode, tail[-1] if tail else ""


def has_errors(issues) -> bool:
    return any(i.level == "error" for i in issues)
