"""
Configuration management for the Perplexity AI chat interface.
Handles environment variables and model settings.
"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


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

    name: str
    api_base: str
    temperature: float
    max_tokens: int
    api_key: Optional[str] = None

    @classmethod
    def load_from_env(cls) -> "ModelConfig":
        """
        Load configuration from environment variables.

        Returns:
            ModelConfig: Configuration object with settings from environment

        Raises:
            ValueError: If required environment variables are missing
        """
        load_dotenv()

        api_key = os.getenv("PPLX_API_KEY")
        if not api_key:
            raise ValueError("PPLX_API_KEY environment variable is not set")

        return cls(
            name="sonar-deep-research",
            api_base="https://api.perplexity.ai",
            temperature=0.7,
            max_tokens=2000,
            api_key=api_key,
        )


# Initialize configuration
config = ModelConfig.load_from_env()
