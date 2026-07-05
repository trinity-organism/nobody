"""A brain is a directory of concepts. The filesystem is the API."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .concept import load_concept
from .frontmatter import FrontmatterError


@dataclass
class Issue:
    code: str
    path: str
    msg: str
    level: str = "error"  # "error" | "warning"

    def __str__(self):
        return f"{self.level.upper():7s} {self.code:12s} {self.path}: {self.msg}"


@dataclass
class Brain:
    root: Path
    concepts: dict = field(default_factory=dict)  # name -> Concept
    load_issues: list = field(default_factory=list)

    def get(self, name):
        return self.concepts.get(name)


def load(root) -> Brain:
    root = Path(root)
    brain = Brain(root=root)
    if not root.is_dir():
        brain.load_issues.append(Issue("E-BRAIN", str(root), "brain directory not found"))
        return brain
    for path in sorted(root.rglob("*.md")):
        rel = str(path.relative_to(root))
        try:
            c = load_concept(path)
        except FrontmatterError as e:
            brain.load_issues.append(Issue("E-FM-PARSE", rel, str(e)))
            continue
        if c.name in brain.concepts:
            other = brain.concepts[c.name].path.name
            brain.load_issues.append(
                Issue("E-DUP", rel, f"duplicate concept name {c.name!r} (also {other})")
            )
            continue
        brain.concepts[c.name] = c
    return brain


def frontier(brain: Brain) -> dict:
    """Known unknowns: dangling [[links]] -> citing concepts. A feature, not a bug."""
    dangling: dict = {}
    for c in brain.concepts.values():
        for link in c.links:
            if link not in brain.concepts:
                dangling.setdefault(link, []).append(c.name)
    return {k: sorted(v) for k, v in sorted(dangling.items())}


def stats(brain: Brain) -> dict:
    by_type: dict = {}
    links = 0
    for c in brain.concepts.values():
        by_type[c.type] = by_type.get(c.type, 0) + 1
        links += len(c.links)
    return {
        "root": str(brain.root),
        "concepts": len(brain.concepts),
        "by_type": dict(sorted(by_type.items())),
        "links": links,
        "dangling_links": len(frontier(brain)),
        "walls": sum(1 for c in brain.concepts.values() if c.verify),
    }
