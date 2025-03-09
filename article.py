"""
Article structure for organizing and processing AI responses.
Handles content parsing and UK English conversion.
"""

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List

import nltk
from nltk.corpus import wordnet, words
from nltk.tokenize import word_tokenize

# Download required NLTK data
try:
    nltk.data.find("tokenizers/punkt")
    nltk.data.find("corpora/wordnet")
    nltk.data.find("corpora/words")
except LookupError:
    print("Downloading required NLTK data...")
    nltk.download("punkt")
    nltk.download("wordnet")
    nltk.download("words")
    nltk.download("punkt_tab")
    nltk.download("averaged_perceptron_tagger")
    print("NLTK data download complete.")


def limit_words(text: str, max_words: int = 1000) -> str:
    """
    Limit text to a specified number of words while preserving sentence boundaries.

    Args:
        text (str): Text to limit
        max_words (int): Maximum number of words to keep

    Returns:
        str: Text limited to max_words
    """
    # Split into sentences first
    sentences = re.split(r"(?<=[.!?])\s+", text)

    # Process each sentence
    word_count = 0
    limited_sentences = []

    for sentence in sentences:
        sentence_words = sentence.split()
        if word_count + len(sentence_words) > max_words:
            break
        limited_sentences.append(sentence)
        word_count += len(sentence_words)

    return " ".join(limited_sentences)


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

    @classmethod
    def from_response(cls, text: str) -> "Article":
        """
        Create an Article instance from raw response text.

        Args:
            text (str): Raw response text from the AI

        Returns:
            Article: Structured article with separated components
        """
        # Clean any think tags from the text
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

        # Extract title and description
        title_match = re.match(r"^#\s*([^:]+)(?::(.+))?", text, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            description = (title_match.group(2) or "").strip()
        else:
            title = "Untitled"
            description = ""

        # Split content and citations
        parts = text.split("# Sources", 1)

        # Get main content (remove title/description line)
        content = parts[0].split("\n", 1)[1].strip() if "\n" in parts[0] else ""

        # Extract citations if they exist
        citations = []
        if len(parts) > 1:
            citation_text = parts[1].strip()
            # Extract URLs from citations
            urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', citation_text)
            # Create citation objects with numbers and URLs
            citations = [{"number": i + 1, "url": url} for i, url in enumerate(urls)]

        # Convert to UK English and limit content length
        uk_title = convert_to_uk_english(title)
        uk_description = convert_to_uk_english(description)
        uk_content = convert_to_uk_english(content)
        limited_content = limit_words(uk_content)

        return cls(
            title=uk_title,
            description=uk_description,
            content=limited_content,
            citations=citations,
        )

    def to_markdown(self) -> str:
        """
        Convert the article to markdown format.

        Returns:
            str: Article in markdown format with JSON citations
        """
        # Build the markdown content
        markdown = f"# {self.title}"
        if self.description:
            markdown += f": {self.description}"
        markdown += f"\n\n{self.content}\n\n"

        # Add citations as JSON
        markdown += "```json\n"
        markdown += json.dumps(self.citations, indent=2)
        markdown += "\n```"

        return markdown


def convert_to_uk_english(text: str) -> str:
    """
    Convert American English text to UK English using NLTK for proper word tokenization.

    Args:
        text (str): Text in American English

    Returns:
        str: Text converted to UK English
    """
    # Tokenize the text into words
    words = word_tokenize(text)

    # Process each word
    processed_words = []
    for word in words:
        # Skip if not a word (punctuation, numbers, etc.)
        if not re.match(r"^[a-zA-Z]+$", word):
            processed_words.append(word)
            continue

        # Get the word's synsets (sets of synonyms)
        synsets = wordnet.synsets(word)
        if synsets:
            # Check if the word is in the wordnet corpus
            lemma = synsets[0].lemmas()[0]
            # If it's an American English lemma, get the British English equivalent
            if lemma.name().endswith("_us"):
                uk_lemma = lemma.name().replace("_us", "_uk")
                processed_words.append(uk_lemma)
            else:
                processed_words.append(word)
        else:
            processed_words.append(word)

    # Join the words back together
    return " ".join(processed_words)
