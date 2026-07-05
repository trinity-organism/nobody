from conftest import REPO

from nobody import brain as brain_mod
from nobody.bench import MockOracle, grade, load_tasks, run

BRAIN = brain_mod.load(REPO / "examples" / "brain")
TASKS = load_tasks(REPO / "bench" / "tasks.jsonl")


def test_grade_modes():
    assert grade("The answer is 42.", {"mode": "contains", "value": "42"})
    assert grade("exact", {"mode": "exact", "value": "exact"})
    assert grade("SEV-1 now", {"mode": "regex", "value": r"sev-\d"})
    assert not grade("nothing", {"mode": "contains", "value": "42"})


def test_naked_oracle_knows_nothing():
    assert MockOracle().complete("sys", "What is the error budget?") == "unknown"


def test_smoke_nobody_beats_naked():
    """Harness invariant: with a perfect reader, the semantic layer must surface
    the answers the naked arm cannot know. Validates harness + retrieval quality."""
    summary, rows = run(TASKS, BRAIN, MockOracle())
    assert summary["tasks"] == len(TASKS) == 12
    assert summary["naked"] == 0.0
    assert summary["nobody"] >= 0.75, f"retrieval too weak: {summary} {rows}"
    assert summary["delta"] > 0
