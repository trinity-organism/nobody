import pytest

from nobody.frontmatter import FrontmatterError, parse


def test_parse_scalars_and_lists():
    meta, body = parse(
        "---\n"
        "type: concept\n"
        'description: "A quoted description"\n'
        "tags: [ops, deploy]\n"
        "aliases:\n"
        "- first\n"
        "- second\n"
        "---\n"
        "Body line one.\n"
    )
    assert meta["type"] == "concept"
    assert meta["description"] == "A quoted description"
    assert meta["tags"] == ["ops", "deploy"]
    assert meta["aliases"] == ["first", "second"]
    assert "Body line one." in body


def test_missing_opening():
    with pytest.raises(FrontmatterError, match="opening"):
        parse("type: concept\n---\n")


def test_unclosed():
    with pytest.raises(FrontmatterError, match="unclosed"):
        parse("---\ntype: concept\n")


def test_unrecognized_line():
    with pytest.raises(FrontmatterError, match="unrecognized"):
        parse("---\ntype: concept\n:::weird:::\n---\n")


def test_dash_without_list():
    with pytest.raises(FrontmatterError, match="dash item"):
        parse("---\n- orphan\n---\n")


def test_duplicate_key():
    with pytest.raises(FrontmatterError, match="duplicate"):
        parse("---\ntype: a\ntype: b\n---\n")


def test_empty_inline_list():
    meta, _ = parse("---\ntype: concept\ntags: []\n---\n")
    assert meta["tags"] == []
