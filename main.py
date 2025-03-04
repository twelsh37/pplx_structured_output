import os
import re
import sys
import threading
import time
from itertools import cycle

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

YOUR_API_KEY = os.getenv("PPLX_API_KEY")


def get_multiline_input():
    """Get multiline input from user until they enter an empty line"""
    print("\nEnter your question (press Enter twice to finish):")
    lines = []
    try:
        while True:
            line = input().strip()
            if not line and lines:  # Empty line and we have content
                break
            if line:  # Add non-empty lines
                lines.append(line)
        return "\n".join(lines)
    except KeyboardInterrupt:
        print("\nExiting program...")
        sys.exit(0)


class ProgressBar:
    def __init__(self, width=30):
        self.width = width
        self.stop_event = threading.Event()
        self.start_time = time.time()

    def animate(self):
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
        self.thread = threading.Thread(target=self.animate)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()
        print(
            "\r" + " " * (self.width + 30) + "\r", end="", flush=True
        )  # Clear the progress bar


def confirm_question(question):
    """Display formatted question and get user confirmation"""
    print("\n# Your Question")
    print("---------------")
    print(question)
    print("\nDo you want to proceed with this question? (Y/N):")

    while True:
        try:
            response = input("> ").strip().upper()
            if response == "Y":
                return True
            elif response == "N":
                print("\nFair enough")
                return False
            else:
                print("Please enter 'Y' or 'N':")
        except KeyboardInterrupt:
            print("\nExiting program...")
            sys.exit(0)


def format_time(seconds):
    """Format time in minutes and seconds"""
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes}m:{remaining_seconds}s"


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
    """Remove any content between <think> tags"""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)


def format_response(response, elapsed_time):
    """Format the API response showing content and citations"""
    # Clean the response content
    content = clean_think_tags(response.choices[0].message.content)

    output = f"""

{content}"""

    # Add citations if they exist
    if hasattr(response, "citations"):
        output += "\n\n# Sources\n----------\n"
        for i, citation in enumerate(response.citations, 1):
            output += f"{i}. {citation}\n"

    return output


def main():
    client = OpenAI(api_key=YOUR_API_KEY, base_url="https://api.perplexity.ai")

    try:
        # Get user's multiline question
        user_question = get_multiline_input()

        # Confirm if user wants to proceed
        if not confirm_question(user_question):
            sys.exit(0)

        # Add user's question to messages
        messages.append({"role": "user", "content": user_question})

        # Start progress bar
        progress = ProgressBar()
        progress.start()

        # Start timing and make API call
        start_time = time.time()
        response = client.chat.completions.create(
            model="sonar-deep-research",
            messages=messages,
        )
        elapsed_time = time.time() - start_time

        # Stop progress bar
        progress.stop()

        # Print response
        print(format_response(response, elapsed_time))

    except KeyboardInterrupt:
        print("\nExiting program...")
        sys.exit(0)


if __name__ == "__main__":
    main()
