# tests/unit/test_text_utils.py

from src.infrastructure.utils.text import clean_text, count_words


def test_clean_text():
    xml_text = "<p>Text with <b>HTML</b> tags.</p>"
    cleaned = clean_text(xml_text)
    assert cleaned == "Text with HTML tags."

    empty_text = None
    assert clean_text(empty_text) == ""

    whitespace_text = "   \n\t  "
    assert clean_text(whitespace_text) == ""


def test_count_words():
    text = "This is a simple test."
    assert count_words(text) == 5

    empty_text = ""
    assert count_words(empty_text) == 0

    whitespace_text = "   \n\t  "
    assert count_words(whitespace_text) == 0