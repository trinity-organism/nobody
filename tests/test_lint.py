from nobody import brain as brain_mod
from nobody.lint import has_errors, lint

GOOD = """---
type: concept
description: A well-formed concept.
---

Links to [[other-thing]].
"""

LAW_NO_WALL = """---
type: law
description: A law that forgot its wall.
---

Unenforced.
"""

LAW_WITH_WALL = """---
type: law
description: A law whose wall passes.
verify: python3 -c "pass"
---

Enforced.
"""

LAW_FAILING_WALL = """---
type: law
description: A law whose wall fails.
verify: python3 -c "import sys; sys.exit(1)"
---

Broken.
"""


def _write(tmp_path, name, content):
    (tmp_path / name).write_text(content, encoding="utf-8")


def _codes(issues):
    return sorted(i.code for i in issues)


def test_good_brain_only_frontier_warning(tmp_path):
    _write(tmp_path, "good-concept.md", GOOD)
    issues = lint(brain_mod.load(tmp_path))
    assert _codes(issues) == ["W-LINK"]
    assert not has_errors(issues)


def test_bad_name(tmp_path):
    _write(tmp_path, "Bad_Name.md", GOOD)
    issues = lint(brain_mod.load(tmp_path))
    assert "E-NAME" in _codes(issues)


def test_missing_type_and_description(tmp_path):
    _write(tmp_path, "empty-meta.md", "---\ntags: [x]\n---\nbody\n")
    codes = _codes(lint(brain_mod.load(tmp_path)))
    assert codes.count("E-FM-REQ") == 2


def test_unknown_type(tmp_path):
    _write(tmp_path, "weird-type.md", "---\ntype: spell\ndescription: d\n---\nbody\n")
    assert "E-TYPE" in _codes(lint(brain_mod.load(tmp_path)))


def test_law_without_wall(tmp_path):
    _write(tmp_path, "lazy-law.md", LAW_NO_WALL)
    assert "E-LAW-WALL" in _codes(lint(brain_mod.load(tmp_path)))


def test_duplicate_name_across_dirs(tmp_path):
    _write(tmp_path, "twin.md", GOOD)
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "twin.md").write_text(GOOD, encoding="utf-8")
    b = brain_mod.load(tmp_path)
    assert "E-DUP" in _codes(lint(b))


def test_parse_error_reported(tmp_path):
    # a file that OPENS frontmatter but breaks it is a real malformed concept
    _write(tmp_path, "broken-front.md", "---\ntype: concept\n:::garbage:::\n---\nx\n")
    assert "E-FM-PARSE" in _codes(lint(brain_mod.load(tmp_path)))


def test_no_frontmatter_is_not_a_concept(tmp_path):
    # prose with no frontmatter is documentation, skipped — not a malformed concept
    _write(tmp_path, "just-prose.md", "no frontmatter at all\n")
    assert "E-FM-PARSE" not in _codes(lint(brain_mod.load(tmp_path)))


def test_walls_pass_and_fail(tmp_path):
    _write(tmp_path, "solid-law.md", LAW_WITH_WALL)
    _write(tmp_path, "broken-law.md", LAW_FAILING_WALL)
    issues = lint(brain_mod.load(tmp_path), walls=True)
    fails = [i for i in issues if i.code == "E-WALL-FAIL"]
    assert len(fails) == 1
    assert "broken-law.md" in fails[0].path
