from nobody import brain as brain_mod
from nobody.lint import has_errors, lint


def test_conventional_docs_are_not_concepts(tmp_path):
    (tmp_path / "README.md").write_text("# My Brain\n\nProse, no frontmatter.\n")
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## 0.1.0\n")
    (tmp_path / "real-concept.md").write_text("---\ntype: concept\ndescription: d\n---\nbody\n")
    b = brain_mod.load(tmp_path)
    assert "real-concept" in b.concepts
    assert "README" not in b.concepts
    assert not has_errors(lint(b))


def test_prose_without_frontmatter_skipped_not_errored(tmp_path):
    (tmp_path / "notes.md").write_text("just some notes, no frontmatter at all\n")
    (tmp_path / "ok.md").write_text("---\ntype: memory\ndescription: d\n---\nx\n")
    assert not has_errors(lint(brain_mod.load(tmp_path)))


def test_malformed_frontmatter_still_errors(tmp_path):
    # starts with --- but is broken -> still a real error, not silently skipped
    (tmp_path / "broken.md").write_text("---\ntype: concept\n:::garbage:::\n---\nx\n")
    codes = sorted(i.code for i in lint(brain_mod.load(tmp_path)))
    assert "E-FM-PARSE" in codes
