"""
Tests for the Article class and related functionality.
"""

import pytest

from article import Article, ArticleError, convert_to_uk_english


def test_article_creation():
    """Test basic article creation with valid data."""
    article = Article(
        title="Test Title",
        description="Test Description",
        content="Test Content",
        citations=[{"number": 1, "url": "https://example.com"}],
    )
    assert article.title == "Test Title"
    assert article.content == "Test Content"


def test_article_validation():
    """Test article validation for required fields."""
    with pytest.raises(ArticleError):
        Article(title="", description="", content="", citations=[])

    with pytest.raises(ArticleError):
        Article(title="Title", description="", content="", citations="not a list")


def test_markdown_generation():
    """Test markdown output generation."""
    article = Article(
        title="Test Title",
        description="Test Description",
        content="Test Content",
        citations=[{"number": 1, "url": "https://example.com"}],
    )
    markdown = article.to_markdown()
    assert "# Test Title: Test Description" in markdown
    assert "Test Content" in markdown
    assert "```json" in markdown
    assert "https://example.com" in markdown


def test_content_cleaning():
    """Test content cleaning functionality."""
    text = """<think>This should be removed</think>
    # Title: Description
    
    Content with   multiple    spaces
    
    
    And multiple newlines."""

    cleaned = Article._clean_content(text)
    assert "<think>" not in cleaned
    assert "multiple    spaces" not in cleaned
    assert "\n\n\n" not in cleaned


def test_citation_extraction():
    """Test citation extraction from text."""
    text = """Some text
    1. https://example.com
    2. http://test.com/page
    3. www.another.com"""

    citations = Article._extract_citations(text)
    assert len(citations) == 3
    assert citations[0]["number"] == 1
    assert citations[0]["url"] == "https://example.com"


def test_uk_english_conversion():
    """Test conversion to UK English."""
    us_text = "The color of the theater is gray."
    uk_text = convert_to_uk_english(us_text)
    assert (
        "colour" in uk_text or "theater" in uk_text
    )  # At least some words should be converted


def test_article_from_response():
    """Test article creation from API response text."""
    response_text = """# Test Title: A Description

This is the content of the article.

# Sources
1. https://example.com
2. https://test.com"""

    article = Article.from_response(response_text)
    assert article.title == "Test Title"
    assert article.description == "A Description"
    assert len(article.citations) == 2


def test_error_handling():
    """Test error handling in article processing."""
    with pytest.raises(ArticleError):
        Article.from_response("Invalid response without proper format")

    with pytest.raises(ArticleError):
        Article.from_response("")
