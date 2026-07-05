from nobody.rank import bm25, tokenize


def test_tokenize_drops_short_and_lowers():
    assert tokenize("A big-BLUE thing 42 x") == ["big", "blue", "thing", "42"]


def test_bm25_prefers_matching_doc():
    docs = {
        "deploy-notes": "deploy freeze rollback release production",
        "cooking": "pasta tomato basil olive oil",
        "mixed": "release party with pasta",
    }
    scores = bm25("deploy freeze rollback", docs)
    assert max(scores, key=scores.get) == "deploy-notes"
    assert "cooking" not in scores


def test_bm25_empty_inputs():
    assert bm25("", {"a": "text"}) == {}
    assert bm25("query", {}) == {}
