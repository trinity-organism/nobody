import json

from conftest import REPO

from nobody import brain as brain_mod
from nobody.cli import main
from nobody.context import compile_context
from nobody.lint import has_errors, lint
from nobody.rite import parse_steps, run_rite, verify_witness

ROLE_OK = """---
type: role
description: A complete role.
charter: May do one thing.
owes: Proof of the thing.
heir: other-role
---

Body.
"""

ROLE_BARE = """---
type: role
description: A role missing everything.
---

Body.
"""

OTHER_ROLE = """---
type: role
description: The heir.
charter: May inherit.
owes: A report.
---

Body.
"""


def _w(tmp_path, name, content):
    (tmp_path / name).write_text(content, encoding="utf-8")


def _codes(issues):
    return sorted(i.code for i in issues)


def test_role_requirements(tmp_path):
    _w(tmp_path, "bare-role.md", ROLE_BARE)
    codes = _codes(lint(brain_mod.load(tmp_path)))
    assert codes.count("E-ROLE-REQ") == 2
    assert "W-SUCCESSION" in codes


def test_heir_must_resolve_to_role(tmp_path):
    _w(tmp_path, "captain.md", ROLE_OK)  # heir: other-role missing
    assert "E-HEIR" in _codes(lint(brain_mod.load(tmp_path)))
    _w(tmp_path, "other-role.md", OTHER_ROLE)
    issues = lint(brain_mod.load(tmp_path))
    assert "E-HEIR" not in _codes(issues)


def test_council_rules(tmp_path):
    _w(
        tmp_path,
        "ghost-council.md",
        "---\ntype: council\ndescription: d\nmembers: [ghost]\nrule: coin-flip\n---\nBody.\n",
    )
    codes = _codes(lint(brain_mod.load(tmp_path)))
    assert "E-COUNCIL-MEMBER" in codes
    assert "E-COUNCIL-RULE" in codes


def test_empty_council(tmp_path):
    _w(
        tmp_path,
        "empty-council.md",
        "---\ntype: council\ndescription: d\nrule: majority\n---\nBody.\n",
    )
    assert "E-COUNCIL-REQ" in _codes(lint(brain_mod.load(tmp_path)))


def test_rite_needs_steps(tmp_path):
    _w(tmp_path, "empty-rite.md", "---\ntype: rite\ndescription: d\n---\nNo steps here.\n")
    assert "E-RITE-EMPTY" in _codes(lint(brain_mod.load(tmp_path)))


def test_advocatus_breaks_weak_law(tmp_path):
    _w(
        tmp_path,
        "weak-law.md",
        "---\ntype: law\ndescription: d\n"
        'verify: python3 -c "pass"\n'
        'refute: python3 -c "pass"\n'
        "---\nThe attack succeeds, the law falls.\n",
    )
    issues = lint(brain_mod.load(tmp_path), walls=True)
    assert "E-ADVOCATUS" in _codes(issues)


def test_advocatus_repelled(tmp_path):
    _w(
        tmp_path,
        "solid-law.md",
        "---\ntype: law\ndescription: d\n"
        'verify: python3 -c "pass"\n'
        'refute: python3 -c "import sys; sys.exit(1)"\n'
        "---\nThe attack fails, the law stands.\n",
    )
    issues = lint(brain_mod.load(tmp_path), walls=True)
    assert not has_errors(issues)


def test_apocrypha_quarantined(tmp_path):
    _w(tmp_path, "canon-fact.md", "---\ntype: concept\ndescription: canon\n---\nsky is blue\n")
    (tmp_path / "apocrypha").mkdir()
    _w(
        tmp_path / "apocrypha",
        "wild-claim.md",
        "---\ntype: concept\ndescription: unproven\n---\nsky is green maybe\n",
    )
    b = brain_mod.load(tmp_path)
    assert b.concepts["wild-claim"].apocryphal
    out = compile_context(b, "what color is the sky")
    assert "wild-claim" not in out.names
    out2 = compile_context(b, "what color is the sky", include_apocrypha=True)
    assert "wild-claim" in out2.names


def test_canonize_moves_clean_concept(tmp_path, capsys):
    (tmp_path / "apocrypha").mkdir()
    _w(
        tmp_path / "apocrypha",
        "new-lesson.md",
        "---\ntype: memory\ndescription: a lesson learned\n---\nAlways verify.\n",
    )
    rc = main(["canonize", "new-lesson", "--brain", str(tmp_path)])
    assert rc == 0
    assert (tmp_path / "new-lesson.md").is_file()
    assert not (tmp_path / "apocrypha" / "new-lesson.md").exists()


def test_rite_runs_and_seals(tmp_path):
    _w(
        tmp_path,
        "tiny-rite.md",
        "---\ntype: rite\ndescription: d\n---\n\n$ true\n$ echo done\n",
    )
    b = brain_mod.load(tmp_path)
    witness = tmp_path / "witness.jsonl"
    code, results = run_rite(b, b.concepts["tiny-rite"], witness=str(witness))
    assert code == 0
    assert len(results) == 2
    ok, n = verify_witness(witness)
    assert ok and n == 2
    # tamper -> chain must break
    lines = witness.read_text().splitlines()
    rec = json.loads(lines[0])
    rec["cmd"] = "evil"
    lines[0] = json.dumps(rec, sort_keys=True)
    witness.write_text("\n".join(lines) + "\n")
    ok, _ = verify_witness(witness)
    assert not ok


def test_rite_stops_on_failure(tmp_path):
    _w(
        tmp_path,
        "failing-rite.md",
        "---\ntype: rite\ndescription: d\n---\n\n$ true\n$ false\n$ echo never\n",
    )
    b = brain_mod.load(tmp_path)
    code, results = run_rite(b, b.concepts["failing-rite"])
    assert code != 0
    assert len(results) == 2  # third step never ran


def test_example_brain_orchestration_clean():
    b = brain_mod.load(REPO / "examples" / "brain")
    issues = lint(b, walls=True)
    assert not has_errors(issues), [str(i) for i in issues]
    assert parse_steps(b.concepts["release-rite"])
