from nobody import brain as brain_mod
from nobody.cli import main
from nobody.context import compile_context


def test_add_crystallizes_to_apocrypha(tmp_path):
    rc = main(
        ["add", "lesson-one", "--brain", str(tmp_path),
         "--description", "a lesson learned", "--body", "Always verify the witness chain."]
    )
    assert rc == 0
    p = tmp_path / "apocrypha" / "lesson-one.md"
    assert p.is_file()
    b = brain_mod.load(tmp_path)
    assert b.concepts["lesson-one"].apocryphal
    assert "lesson-one" not in compile_context(b, "verify witness chain").names


def test_add_refuses_bad_name(tmp_path):
    rc = main(
        ["add", "Bad_Name", "--brain", str(tmp_path),
         "--description", "d", "--body", "x"]
    )
    assert rc == 1
    assert not (tmp_path / "apocrypha" / "Bad_Name.md").exists()


def test_add_refuses_duplicate(tmp_path):
    (tmp_path / "taken.md").write_text("---\ntype: concept\ndescription: d\n---\nx\n")
    rc = main(["add", "taken", "--brain", str(tmp_path), "--description", "d", "--body", "y"])
    assert rc == 2
