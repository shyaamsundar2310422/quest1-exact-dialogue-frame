from src.matching.text_matcher import normalize, find_dialogue


def test_normalize():
    assert normalize("  Hello   WORLD  ") == "hello world"