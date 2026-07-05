from nobody import brain as brain_mod
from nobody.lint import lint

DOCTRINE = "---\ntype: doctrine\ndescription: d\n---\nBody.\n"
INDEX_DECLARING = (
    "---\ntype: index\ndescription: map\ntypes: [doctrine, reference]\n---\n\n- [[some-doctrine]]\n"
)
INDEX_PLAIN = "---\ntype: index\ndescription: map\n---\n\n- [[some-doctrine]]\n"


def _codes(issues):
    return sorted(i.code for i in issues)


def test_undeclared_custom_type_is_error(tmp_path):
    (tmp_path / "some-doctrine.md").write_text(DOCTRINE, encoding="utf-8")
    (tmp_path / "index.md").write_text(INDEX_PLAIN, encoding="utf-8")
    assert "E-TYPE" in _codes(lint(brain_mod.load(tmp_path)))


def test_index_declares_ontology(tmp_path):
    (tmp_path / "some-doctrine.md").write_text(DOCTRINE, encoding="utf-8")
    (tmp_path / "index.md").write_text(INDEX_DECLARING, encoding="utf-8")
    issues = lint(brain_mod.load(tmp_path))
    assert "E-TYPE" not in _codes(issues)
