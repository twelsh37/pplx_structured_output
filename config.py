"""
Configuration management for the Perplexity AI chat interface.
Handles environment variables and model settings.
"""

import os
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""

    pass


@dataclass
class ModelConfig:
    """
    Configuration settings for the Perplexity AI model.

    Attributes:
        name (str): Name of the model to use
        api_base (str): Base URL for the API
        temperature (float): Temperature setting for response generation
        max_tokens (int): Maximum number of tokens in the response
        api_key (str): API key for authentication
    """

    name: str = "sonar-deep-research"
    api_base: str = "https://api.perplexity.ai"
    temperature: float = 0.7
    max_tokens: int = 4000  # Increased for longer responses
    api_key: Optional[str] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_config()

    def _validate_config(self) -> None:
        """
        Validate the configuration settings.

        Raises:
            ConfigurationError: If any configuration values are invalid
        """
        if not isinstance(self.temperature, float) or not 0 <= self.temperature <= 1:
            raise ConfigurationError("Temperature must be a float between 0 and 1")

        if not isinstance(self.max_tokens, int) or self.max_tokens <= 0:
            raise ConfigurationError("max_tokens must be a positive integer")

        if not self.name or not isinstance(self.name, str):
            raise ConfigurationError("Model name must be a non-empty string")

        if not self.api_base or not isinstance(self.api_base, str):
            raise ConfigurationError("API base URL must be a non-empty string")

        if not self.api_key:
            raise ConfigurationError(
                "PPLX_API_KEY environment variable is not set. "
                "Please set it in your .env file or environment variables."
            )

    @classmethod
    def load_from_env(cls, env_file: bool = True) -> "ModelConfig":
        """
        Load configuration from environment variables.

        Args:
            env_file: Whether to load from .env file. Defaults to True.

        Returns:
            ModelConfig: Configuration object with settings from environment

        Raises:
            ConfigurationError: If required environment variables are missing
        """
        if env_file:
            # Load environment variables from file
            load_dotenv()

        # Get API key first and validate it immediately
        api_key = os.getenv("PPLX_API_KEY")
        if not api_key:
            raise ConfigurationError(
                "PPLX_API_KEY environment variable is not set. "
                "Please set it in your .env file or environment variables."
            )

        # Create instance with default values and API key
        config = cls(api_key=api_key)

        # Override defaults with environment variables if they exist
        if temp := os.getenv("PPLX_TEMPERATURE"):
            config.temperature = float(temp)

        if tokens := os.getenv("PPLX_MAX_TOKENS"):
            config.max_tokens = int(tokens)

        if model := os.getenv("PPLX_MODEL"):
            config.name = model

        if base := os.getenv("PPLX_API_BASE"):
            config.api_base = base

        return config


# Initialize configuration
_config_instance = None


def get_config(env_file: bool = True):
    """
    Get the configuration, initializing it if necessary.

    Args:
        env_file: Whether to load from .env file. Defaults to True.

    Returns:
        ModelConfig: The configuration instance

    Raises:
        ConfigurationError: If the configuration is invalid
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ModelConfig.load_from_env(env_file=env_file)
    return _config_instance


def reset_config():
    """
    Reset the configuration instance.
    This is primarily used for testing purposes.
    """
    global _config_instance
    _config_instance = None
