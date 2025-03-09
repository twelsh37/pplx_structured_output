"""
Utility functions for the Perplexity AI chat interface.
Contains helper functions for input handling, formatting, and progress tracking.
"""

import re
import threading
import time
from typing import Any, Dict, List


def get_multiline_input() -> str:
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
        raise


def format_time(seconds: float) -> str:
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


def clean_think_tags(text: str) -> str:
    """
    Remove any content between <think> tags from the text.

    Args:
        text (str): The text to clean.

    Returns:
        str: The cleaned text with think tags and their content removed.
    """
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)


def format_response(response: Dict[str, Any], elapsed_time: float) -> str:
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


class ProgressBar:
    """
    A class to display an animated progress bar with elapsed time.

    Attributes:
        width (int): The width of the progress bar in characters.
        stop_event (threading.Event): Event to control the animation thread.
        start_time (float): The time when the progress bar started.
    """

    def __init__(self, width: int = 30):
        """
        Initialize the progress bar.

        Args:
            width (int): The width of the progress bar in characters.
        """
        self.width = width
        self.stop_event = threading.Event()
        self.start_time = time.time()

    def animate(self) -> None:
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

    def start(self) -> None:
        """Start the progress bar animation in a separate thread."""
        self.thread = threading.Thread(target=self.animate)
        self.thread.start()

    def stop(self) -> None:
        """Stop the progress bar animation and clean up the display."""
        self.stop_event.set()
        self.thread.join()
        print(
            "\r" + " " * (self.width + 30) + "\r", end="", flush=True
        )  # Clear the progress bar
