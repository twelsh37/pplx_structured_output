"""
Main script for interacting with Perplexity AI models.
This script provides a command-line interface to interact with Perplexity AI,
with features like progress tracking and multiline input support.
"""

import os
import re
import sys
import threading
import time
from itertools import cycle

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key for Perplexity from environment variables
YOUR_API_KEY = os.getenv("PPLX_API_KEY")

# Configure Perplexity model settings
MODEL_CONFIG = {
    "name": "sonar-deep-research",
    "api_base": "https://api.perplexity.ai",
    "temperature": 0.7,
    "max_tokens": 2000,
}


def get_multiline_input():
    """
    Get multiline input from user until they enter an empty line.
    Each line is prefixed with a '>' prompt.

    Returns:
        str: The combined multiline input as a single string.

    Raises:
        KeyboardInterrupt: If user interrupts the input process.
    """
    print("\nEnter your question (press Enter twice to finish):")
    lines = []
    try:
        while True:
            line = input("> ").strip()
            if not line and lines:  # Empty line and we have content
                break
            if line:  # Add non-empty lines
                lines.append(line)
        return "\n".join(lines)
    except KeyboardInterrupt:
        print("\nExiting program...")
        sys.exit(0)


class ProgressBar:
    """
    A class to display an animated progress bar with elapsed time.

    Attributes:
        width (int): The width of the progress bar in characters.
        stop_event (threading.Event): Event to control the animation thread.
        start_time (float): The time when the progress bar started.
    """

    def __init__(self, width=30):
        """
        Initialize the progress bar.

        Args:
            width (int): The width of the progress bar in characters.
        """
        self.width = width
        self.stop_event = threading.Event()
        self.start_time = time.time()

    def animate(self):
        """
        Animate the progress bar by moving a cursor back and forth.
        Displays elapsed time alongside the progress bar.
        """
        pos = 0
        direction = 1  # 1 for right, -1 for left
        while not self.stop_event.is_set():
            # Calculate elapsed time
            elapsed = time.time() - self.start_time
            elapsed_str = format_time(elapsed)

            # Create the progress bar
            bar = ["-"] * self.width
            bar[pos] = "█"
            progress = "".join(bar)

            # Print progress bar with elapsed time
            print(f"\rProcessing [{progress}] {elapsed_str}", end="", flush=True)

            # Update position
            pos += direction
            if pos == self.width - 1 or pos == 0:
                direction *= -1  # Reverse direction at ends

            time.sleep(0.1)

    def start(self):
        """Start the progress bar animation in a separate thread."""
        self.thread = threading.Thread(target=self.animate)
        self.thread.start()

    def stop(self):
        """Stop the progress bar animation and clean up the display."""
        self.stop_event.set()
        self.thread.join()
        print(
            "\r" + " " * (self.width + 30) + "\r", end="", flush=True
        )  # Clear the progress bar


def format_time(seconds):
    """
    Format time in minutes and seconds.

    Args:
        seconds (float): Time in seconds.

    Returns:
        str: Formatted time string in the format "Xm:Ys".
    """
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes}m:{remaining_seconds}s"


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


def clean_think_tags(text):
    """
    Remove any content between <think> tags from the text.

    Args:
        text (str): The text to clean.

    Returns:
        str: The cleaned text with think tags and their content removed.
    """
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)


def format_response(response, elapsed_time):
    """
    Format the API response for display.

    Args:
        response: The API response object.
        elapsed_time (float): Time taken to get the response.

    Returns:
        str: Formatted response text with citations if available.
    """
    # Clean the response content
    content = clean_think_tags(response["choices"][0]["message"]["content"])

    output = f"""

{content}"""

    # Add citations if they exist
    if "citations" in response:
        output += "\n\n# Sources\n----------\n"
        for i, citation in enumerate(response["citations"], 1):
            output += f"{i}. {citation}\n"

    return output


def call_perplexity_api(messages):
    """
    Make a direct API call to Perplexity's chat endpoint.

    Args:
        messages (list): List of message dictionaries.

    Returns:
        dict: The JSON response from the Perplexity API.
    """
    url = f"{MODEL_CONFIG['api_base']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {YOUR_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_CONFIG["name"],
        "messages": messages,
        "temperature": MODEL_CONFIG["temperature"],
        "max_tokens": MODEL_CONFIG["max_tokens"],
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def main():
    """
    Main function to run the AI chat interface.
    Handles user input, API calls, and response formatting.
    """
    try:
        # Get user's multiline question
        user_question = get_multiline_input()

        # Add user's question to messages
        messages.append({"role": "user", "content": user_question})

        # Start timing
        start_time = time.time()

        print("\nSending request to model...")  # Debug print

        # Start progress bar just before API call
        progress = ProgressBar()
        progress.start()

        try:
            # Make the API call
            response = call_perplexity_api(messages)
        finally:
            # Ensure progress bar is stopped even if API call fails
            progress.stop()

        elapsed_time = time.time() - start_time

        # Print response
        print(format_response(response, elapsed_time))

    except KeyboardInterrupt:
        print("\nExiting program...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nDebug info:")
        print(f"Model config: {MODEL_CONFIG}")
        print(f"API base: {MODEL_CONFIG['api_base']}")
        print(f"Model name: {MODEL_CONFIG['name']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
