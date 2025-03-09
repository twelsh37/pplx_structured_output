"""
Article structure for organizing and processing AI responses.
Handles content parsing and UK English conversion.
"""

import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import nltk
from nltk.corpus import wordnet
from nltk.tokenize import sent_tokenize, word_tokenize

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find("tokenizers/punkt")
    nltk.data.find("corpora/wordnet")
except LookupError:
    logger.info("Downloading required NLTK data...")
    nltk.download("punkt")
    nltk.download("wordnet")
    nltk.download("averaged_perceptron_tagger")
    logger.info("NLTK data download complete.")


class ArticleError(Exception):
    """Custom exception for article processing errors."""

    pass


@dataclass
class Article:
    """
    Structured representation of an AI response.

    Attributes:
        title (str): The main title of the article
        description (str): Brief description or subtitle
        content (str): Main body of the article in markdown format
        citations (List[Dict[str, Any]]): List of citations in JSON format
    """

    title: str
    description: str
    content: str
    citations: List[Dict[str, Any]]

    def __post_init__(self):
        """Validate article attributes after initialization."""
        if not self.title:
            raise ArticleError("Article must have a title")
        if not self.content:
            raise ArticleError("Article must have content")
        if not isinstance(self.citations, list):
            raise ArticleError("Citations must be a list")

    @staticmethod
    def _extract_title_description(text: str) -> Tuple[str, str]:
        """
        Extract title and description from the text.

        Args:
            text (str): Raw text to process

        Returns:
            Tuple[str, str]: Title and description
        """
        title_match = re.match(r"^#\s*([^:]+)(?::(.+))?", text, re.MULTILINE)
        if not title_match:
            logger.warning("No title found in text, using default")
            return "Untitled", ""

        title = title_match.group(1).strip()
        description = (title_match.group(2) or "").strip()
        return title, description

    @staticmethod
    def _extract_citations(citation_text: str) -> List[Dict[str, Any]]:
        """
        Extract citations from the text.

        Args:
            citation_text (str): Text containing citations

        Returns:
            List[Dict[str, Any]]: List of citation objects
        """
        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', citation_text)
        return [{"number": i + 1, "url": url} for i, url in enumerate(urls)]

    @staticmethod
    def _clean_content(content: str) -> str:
        """
        Clean and format the content text.

        Args:
            content (str): Raw content text

        Returns:
            str: Cleaned and formatted content
        """
        # Remove think tags
        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)

        # Remove multiple newlines (preserve at least one)
        content = re.sub(r"\n{3,}", "\n\n", content)

        # Ensure proper spacing after punctuation
        content = re.sub(r"([.!?])\s*(\w)", r"\1 \2", content)

        # Replace multiple spaces with a single space (but preserve newlines)
        content = re.sub(r"[^\S\n]+", " ", content)

        return content.strip()

    @classmethod
    def from_response(cls, text: str) -> "Article":
        """
        Create an Article instance from raw response text.

        Args:
            text (str): Raw response text from the AI

        Returns:
            Article: Structured article with separated components

        Raises:
            ArticleError: If the text cannot be properly parsed
        """
        try:
            # Clean the initial text
            text = cls._clean_content(text)

            # Extract title and description
            title, description = cls._extract_title_description(text)

            # Split content and citations
            parts = text.split("# Sources", 1)
            if len(parts) < 2:
                logger.warning("No citations found in text")
                content_text = parts[0]
                citations = []
            else:
                content_text, citation_text = parts
                citations = cls._extract_citations(citation_text)

            # Get main content (remove title/description line)
            content_lines = content_text.split("\n")
            content = (
                "\n".join(content_lines[1:]).strip() if len(content_lines) > 1 else ""
            )

            # Convert to UK English
            uk_title = convert_to_uk_english(title)
            uk_description = convert_to_uk_english(description)
            uk_content = convert_to_uk_english(content)

            return cls(
                title=uk_title,
                description=uk_description,
                content=uk_content,
                citations=citations,
            )

        except Exception as e:
            raise ArticleError(f"Failed to parse article: {str(e)}") from e

    def to_markdown(self) -> str:
        """
        Convert the article to markdown format.

        Returns:
            str: Article in markdown format with JSON citations
        """
        try:
            # Build the markdown content
            parts = []

            # Add title and description
            title_line = f"# {self.title}"
            if self.description:
                title_line += f": {self.description}"
            parts.append(title_line)

            # Add content with proper spacing
            parts.append(self.content)

            # Add citations as JSON
            if self.citations:
                parts.append("```json")
                parts.append(json.dumps(self.citations, indent=2))
                parts.append("```")

            # Join with double newlines for proper markdown spacing
            return "\n\n".join(parts)

        except Exception as e:
            raise ArticleError(f"Failed to generate markdown: {str(e)}") from e


def convert_to_uk_english(text: str) -> str:
    """
    Convert American English text to UK English using NLTK for proper word tokenization.

    Args:
        text (str): Text in American English

    Returns:
        str: Text converted to UK English
    """
    try:
        # Tokenize into sentences first to preserve structure
        sentences = sent_tokenize(text)
        converted_sentences = []

        for sentence in sentences:
            # Tokenize sentence into words
            words = word_tokenize(sentence)

            # Process each word
            processed_words = []
            for word in words:
                # Skip if not a word
                if not re.match(r"^[a-zA-Z]+$", word):
                    processed_words.append(word)
                    continue

                # Get synsets and process
                synsets = wordnet.synsets(word)
                if synsets:
                    lemma = synsets[0].lemmas()[0]
                    if lemma.name().endswith("_us"):
                        uk_lemma = lemma.name().replace("_us", "_uk")
                        processed_words.append(uk_lemma)
                    else:
                        processed_words.append(word)
                else:
                    processed_words.append(word)

            # Reconstruct sentence
            converted_sentences.append(" ".join(processed_words))

        # Join sentences with proper spacing
        return " ".join(converted_sentences)

    except Exception as e:
        logger.error(f"Error converting to UK English: {str(e)}")
        return text  # Return original text if conversion fails
