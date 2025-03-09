"""
API interaction functions for the Perplexity AI chat interface.
Handles all direct communication with the Perplexity API.
"""

import logging
import time
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry

from config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


class PerplexityAPI:
    """
    Handles communication with the Perplexity API.

    Attributes:
        session (requests.Session): Session for making HTTP requests
        base_url (str): Base URL for the API
        headers (dict): Headers for API requests
    """

    def __init__(self):
        """Initialize the API handler with retry logic and timeouts."""
        self.session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=0.5,  # wait 0.5, 1, 2 seconds between retries
            status_forcelist=[500, 502, 503, 504],  # retry on these status codes
        )

        # Add retry adapter to session
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Get configuration
        config = get_config()

        # Store config values
        self.model_name = config.name
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens

        # Set up base URL and headers
        self.base_url = f"{config.api_base}/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        }

    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to the API with error handling and logging.

        Args:
            payload (dict): The request payload

        Returns:
            dict: The API response

        Raises:
            APIError: If there's an error communicating with the API
        """
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                start_time = time.time()
                response = self.session.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=(5, 30),  # (connect timeout, read timeout)
                )
                elapsed_time = time.time() - start_time
                logger.info(f"API request completed in {elapsed_time:.2f} seconds")

                if response.status_code == 500 and retry_count < max_retries - 1:
                    retry_count += 1
                    time.sleep(0.5 * (2**retry_count))  # Exponential backoff
                    continue

                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                raise APIError("Request timed out. Please try again.")
            except requests.exceptions.ConnectionError:
                raise APIError(
                    "Could not connect to the API. Please check your internet connection."
                )
            except requests.exceptions.HTTPError as e:
                error_msg = f"HTTP Error: {str(e)}"
                if response.text:
                    try:
                        error_data = response.json()
                        if "error" in error_data:
                            error_msg = f"API Error: {error_data['error']}"
                    except ValueError:
                        pass
                if response.status_code == 500 and retry_count < max_retries - 1:
                    retry_count += 1
                    time.sleep(0.5 * (2**retry_count))  # Exponential backoff
                    continue
                raise APIError(error_msg)
            except Exception as e:
                raise APIError(f"Unexpected error: {str(e)}")

        raise APIError("Maximum retries exceeded")

    def get_completion(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Get a completion from the API.

        Args:
            messages (list): List of message dictionaries

        Returns:
            dict: The API response

        Raises:
            APIError: If there's an error communicating with the API
        """
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        return self._make_request(payload)


# Initialize API handler
api = PerplexityAPI()


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
    return api.get_completion(messages)


def add_user_message(question: str) -> None:
    """
    Add a user message to the conversation history.

    Args:
        question (str): The user's question to add.
    """
    messages.append({"role": "user", "content": question})
