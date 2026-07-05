"""One file = one concept. The name IS the claim."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from . import frontmatter

KNOWN_TYPES = ("concept", "law", "playbook", "memory", "index", "role", "rite", "council")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[\[([a-z0-9][a-z0-9-]*)\]\]")


@dataclass
class Concept:
    name: str
    type: str
    description: str
    path: Path
    body: str
    tags: list = field(default_factory=list)
    verify: str = ""
    refute: str = ""  # advocatus diaboli: an attack that MUST fail for the law to stand
    charter: str = ""  # role: what it may do
    owes: str = ""  # role: the proof it must deliver
    heir: str = ""  # role: succession — who inherits on failure
    members: list = field(default_factory=list)  # council: member roles
    rule: str = ""  # council: majority | unanimous | any-veto
    links: list = field(default_factory=list)
    apocryphal: bool = False  # lives under apocrypha/ — quarantined, not canon
    meta: dict = field(default_factory=dict)


def _str(meta: dict, key: str) -> str:
    v = meta.get(key, "")
    return v if isinstance(v, str) else ""


def load_concept(path: Path) -> Concept:
    """Parse one concept file. Raises FrontmatterError on bad frontmatter."""
    meta, body = frontmatter.parse(path.read_text(encoding="utf-8"))
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    members = meta.get("members", [])
    if isinstance(members, str):
        members = [members]
    return Concept(
        name=path.stem,
        type=_str(meta, "type"),
        description=_str(meta, "description"),
        path=path,
        body=body,
        tags=list(tags),
        verify=_str(meta, "verify"),
        refute=_str(meta, "refute"),
        charter=_str(meta, "charter"),
        owes=_str(meta, "owes"),
        heir=_str(meta, "heir"),
        members=list(members),
        rule=_str(meta, "rule"),
        links=sorted(set(LINK_RE.findall(body))),
        meta=meta,
    )
