"""
Tests for configuration management.
"""

import os

import pytest

from config import ConfigurationError, ModelConfig, reset_config


@pytest.fixture(autouse=True)
def clean_config():
    """Reset configuration before each test."""
    reset_config()
    yield
    reset_config()


def test_config_validation():
    """Test configuration validation."""
    # Test valid configuration
    config = ModelConfig(
        name="test-model",
        api_base="https://api.test.com",
        temperature=0.5,
        max_tokens=1000,
        api_key="test-key",
    )
    assert config.name == "test-model"
    assert config.temperature == 0.5

    # Test invalid temperature
    with pytest.raises(ConfigurationError):
        ModelConfig(
            name="test",
            api_base="https://test.com",
            temperature=1.5,  # Invalid temperature
            max_tokens=1000,
            api_key="key",
        )

    # Test invalid max_tokens
    with pytest.raises(ConfigurationError):
        ModelConfig(
            name="test",
            api_base="https://test.com",
            temperature=0.5,
            max_tokens=-1,  # Invalid token count
            api_key="key",
        )


def test_env_loading(monkeypatch):
    """Test loading configuration from environment variables."""
    # Set up test environment variables
    test_env = {
        "PPLX_API_KEY": "test-key",
        "PPLX_TEMPERATURE": "0.8",
        "PPLX_MAX_TOKENS": "2000",
        "PPLX_MODEL": "test-model",
        "PPLX_API_BASE": "https://test.com",
    }

    for key, value in test_env.items():
        monkeypatch.setenv(key, value)

    config = ModelConfig.load_from_env()
    assert config.api_key == "test-key"
    assert config.temperature == 0.8
    assert config.max_tokens == 2000
    assert config.name == "test-model"
    assert config.api_base == "https://test.com"


def test_missing_api_key(monkeypatch):
    """Test handling of missing API key."""
    # Start with a clean environment for this test
    monkeypatch.delenv("PPLX_API_KEY", raising=False)

    # Ensure we don't load from .env file
    with pytest.raises(ConfigurationError) as exc:
        ModelConfig.load_from_env(env_file=False)
    assert "PPLX_API_KEY" in str(exc.value)


def test_invalid_env_values(monkeypatch):
    """Test handling of invalid environment variable values."""
    monkeypatch.setenv("PPLX_API_KEY", "test-key")
    monkeypatch.setenv("PPLX_TEMPERATURE", "invalid")

    with pytest.raises(ValueError):
        ModelConfig.load_from_env()


def test_default_values():
    """Test default configuration values."""
    config = ModelConfig(api_key="test-key")
    assert config.name == "sonar-deep-research"
    assert config.temperature == 0.7
    assert config.max_tokens == 4000
