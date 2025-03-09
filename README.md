# Perplexity AI Article Generator

A Python project that interacts with the Perplexity AI API to generate articles, process them into UK English, and format them with proper citations.

## Features

- Interacts with Perplexity AI API
- Converts American English to UK English using NLTK
- Limits content to 1000 words while preserving sentence boundaries
- Extracts and formats citations as JSON
- Outputs content in markdown format

## Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/pplx_test_delete.git
cd pplx_test_delete
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Perplexity API key:

```
PPLX_API_KEY=your_api_key_here
```

## Usage

Run the main script:

```bash
python main.py
```

The script will:

1. Prompt for your question
2. Send it to the Perplexity AI API
3. Process the response (UK English conversion, word limiting)
4. Save the formatted article to `article.md`

## Output Format

The generated `article.md` file will contain:

- Title and description
- Main content (limited to 1000 words)
- Citations in JSON format

Example:

````markdown
# Title: Description

Content in UK English...

```json
[
  {
    "number": 1,
    "url": "https://example.com/citation1"
  }
]
```
````

```

## Project Structure

- `main.py`: Main script that handles user interaction and program flow
- `article.py`: Article class and text processing functions
- `api.py`: API interaction functions
- `config.py`: Configuration management
- `utils.py`: Utility functions for input/output and progress tracking
```
