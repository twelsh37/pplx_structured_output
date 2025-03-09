"""
API interaction functions for the Perplexity AI chat interface.
Handles all direct communication with the Perplexity API.
"""

from typing import Any, Dict, List

import requests
from requests.exceptions import RequestException

from config import config

# Initialize conversation messages with system prompt
messages = [
    {
        "role": "system",
        "content": (
            "You are an artificial intelligence assistant and you need to "
            "engage in a helpful, detailed, polite conversation with a user."
        ),
    }
]


class APIError(Exception):
    """Custom exception for API-related errors."""

    pass


def call_perplexity_api(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Make a direct API call to Perplexity's chat endpoint.

    Args:
        messages (list): List of message dictionaries.

    Returns:
        dict: The JSON response from the Perplexity API.

    Raises:
        APIError: If there's an error communicating with the API
    """
    url = f"{config.api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config.name,
        "messages": messages,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise APIError(f"API request failed: {str(e)}") from e


def add_user_message(question: str) -> None:
    """
    Add a user message to the conversation history.

    Args:
        question (str): The user's question to add.
    """
    messages.append({"role": "user", "content": question})
