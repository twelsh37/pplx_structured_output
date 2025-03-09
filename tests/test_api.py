"""
Tests for API functionality.
"""

import pytest
import responses
from requests.exceptions import Timeout as TimeoutError

from api import APIError, PerplexityAPI, add_user_message, messages


@pytest.fixture
def api():
    """Create a test API instance."""
    return PerplexityAPI()


@responses.activate
def test_successful_api_call(api):
    """Test successful API call."""
    # Mock successful response
    responses.add(
        responses.POST,
        "https://api.perplexity.ai/chat/completions",
        json={
            "choices": [
                {
                    "message": {
                        "content": "# Test Response\n\nThis is a test response.\n\n# Sources\n1. https://example.com"
                    }
                }
            ]
        },
        status=200,
    )

    response = api.get_completion([{"role": "user", "content": "test"}])
    assert "choices" in response
    assert "message" in response["choices"][0]


@responses.activate
def test_api_error_handling(api):
    """Test API error handling."""
    # Mock error response
    responses.add(
        responses.POST,
        "https://api.perplexity.ai/chat/completions",
        json={"error": "Invalid API key"},
        status=401,
    )

    with pytest.raises(APIError) as exc:
        api.get_completion([{"role": "user", "content": "test"}])
    assert "Invalid API key" in str(exc.value)


@responses.activate
def test_timeout_handling(api):
    """Test timeout handling."""
    # Mock timeout
    responses.add(
        responses.POST,
        "https://api.perplexity.ai/chat/completions",
        body=TimeoutError("Request timed out"),
    )

    with pytest.raises(APIError) as exc:
        api.get_completion([{"role": "user", "content": "test"}])
    assert "timed out" in str(exc.value)


def test_message_handling():
    """Test message handling."""
    # Clear existing messages
    messages.clear()
    messages.append({"role": "system", "content": "You are an AI assistant"})

    # Test adding a message
    add_user_message("test question")
    assert len(messages) == 2
    assert messages[-1]["role"] == "user"
    assert messages[-1]["content"] == "test question"


@responses.activate
def test_retry_mechanism(api):
    """Test retry mechanism for failed requests."""
    # Mock responses that fail twice then succeed
    responses.add(
        responses.POST,
        "https://api.perplexity.ai/chat/completions",
        json={"error": "Server Error"},
        status=500,
    )
    responses.add(
        responses.POST,
        "https://api.perplexity.ai/chat/completions",
        json={"error": "Server Error"},
        status=500,
    )
    responses.add(
        responses.POST,
        "https://api.perplexity.ai/chat/completions",
        json={"choices": [{"message": {"content": "Success"}}]},
        status=200,
    )

    response = api.get_completion([{"role": "user", "content": "test"}])
    assert "choices" in response
