from conftest import REPO

from nobody import brain as brain_mod
from nobody.context import compile_context

BRAIN = brain_mod.load(REPO / "examples" / "brain")


def test_relevant_concept_packed():
    out = compile_context(BRAIN, "What is the monthly error budget for the Acme API?")
    assert "error-budget" in out.names
    assert "0.05%" in out.text


def test_budget_respected():
    out = compile_context(BRAIN, "error budget sla uptime rollback staging", budget=80)
    assert out.used <= 80
    assert len(out.names) >= 1


def test_index_never_packed():
    out = compile_context(BRAIN, "index map of the brain concepts linked here")
    assert "index" not in out.names


def test_link_expansion_pulls_neighbor():
    # deploy-freeze links rollback-procedure; a freeze-only query should pull both
    out = compile_context(BRAIN, "During a deploy freeze what change is allowed?")
    assert "deploy-freeze" in out.names
    assert "rollback-procedure" in out.names


def test_deterministic():
    a = compile_context(BRAIN, "error budget")
    b = compile_context(BRAIN, "error budget")
    assert a.text == b.text
