"""
Main script for interacting with Perplexity AI models.
This script provides a command-line interface to interact with Perplexity AI,
with features like progress tracking and multiline input support.
"""

import os
import sys
import time
from typing import NoReturn

from api import APIError, add_user_message, call_perplexity_api, messages
from article import Article
from config import get_config
from utils import ProgressBar, get_multiline_input


def handle_error(error: Exception) -> NoReturn:
    """
    Handle different types of errors and provide appropriate user feedback.

    Args:
        error: The exception that was raised

    Returns:
        NoReturn: This function always exits the program
    """
    if isinstance(error, APIError):
        print("\nError communicating with Perplexity API:")
        print(str(error))
    elif isinstance(error, KeyboardInterrupt):
        print("\nProgram interrupted by user.")
    else:
        print(f"\nAn unexpected error occurred: {str(error)}")

    # Print debug information for all errors
    config = get_config()
    print("\nDebug information:")
    print(f"Model: {config.name}")
    print(f"API Base: {config.api_base}")
    sys.exit(1)


def main() -> None:
    """
    Main function to run the AI chat interface.
    Gets user input, processes it through the API, and returns a structured article.
    """
    try:
        # Get user's question
        user_question = get_multiline_input()
        add_user_message(user_question)

        print("\nSending request to model\nAccessing deep research,\nThis could take a few minutes to complete...")
        progress = ProgressBar()
        progress.start()

        try:
            response = call_perplexity_api(messages)
            print("\nReceived response from API")
        finally:
            progress.stop()

        # Debug: Print the raw response content
        print("\nRaw response content:")
        print(response["choices"][0]["message"]["content"])

        # Convert response to structured article
        article = Article.from_response(response["choices"][0]["message"]["content"])
        print("\nArticle created successfully")

        # Get the current working directory
        current_dir = os.getcwd()
        output_file = os.path.join(current_dir, "article.md")

        print(f"\nWriting to file: {output_file}")

        # Write the markdown content to file
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                content = article.to_markdown()
                f.write(content)
                word_count = len(content.split())
                print(f"Successfully wrote {word_count} words to file")
        except Exception as e:
            print(f"Error writing to file: {str(e)}")
            raise

        print("\nArticle has been written to article.md")

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
        sys.exit(0)
    except Exception as e:
        handle_error(e)


if __name__ == "__main__":
    main()
