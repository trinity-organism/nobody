"""One file = one concept. The name IS the claim."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from . import frontmatter

KNOWN_TYPES = ("concept", "law", "playbook", "memory", "index")
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
    links: list = field(default_factory=list)
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
    return Concept(
        name=path.stem,
        type=_str(meta, "type"),
        description=_str(meta, "description"),
        path=path,
        body=body,
        tags=list(tags),
        verify=_str(meta, "verify"),
        links=sorted(set(LINK_RE.findall(body))),
        meta=meta,
    )
