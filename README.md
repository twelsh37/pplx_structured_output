# Perplexity AI Article Generator

A Python project that interacts with the Perplexity AI API to generate articles, process them into UK English, and format them with proper citations.

## Features

- Interacts with Perplexity AI API using the sonar-deep-research model
- Converts American English to UK English using NLTK
- Extracts and formats citations as JSON
- Outputs content in markdown format
- Configurable API settings and model parameters
- Automatic retries with exponential backoff
- Progress tracking during API calls

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

For development and testing, also install test dependencies:

```bash
pip install -r tests/requirements-test.txt
```

3. Create a `.env` file with your configuration:

```env
# Required
PPLX_API_KEY=your_api_key_here

# Optional - defaults shown below
PPLX_API_BASE=https://api.perplexity.ai
PPLX_MODEL_NAME=sonar-deep-research
PPLX_TEMPERATURE=0.7
PPLX_MAX_TOKENS=1024
```

## Configuration

The project uses a configuration system (`config.py`) that manages API settings and model parameters:

### Default Configuration

```python
MODEL_CONFIG = {
    "name": "sonar-deep-research",  # Model identifier
    "api_base": "https://api.perplexity.ai",  # API endpoint
    "temperature": 0.7,  # Controls response randomness (0.0-1.0)
    "max_tokens": 1024  # Maximum response length
}
```

### Environment Variables

- `PPLX_API_KEY`: (Required) Your Perplexity API key
- `PPLX_API_BASE`: (Optional) API endpoint URL
- `PPLX_MODEL_NAME`: (Optional) Model identifier
- `PPLX_TEMPERATURE`: (Optional) Response randomness (0.0-1.0)
- `PPLX_MAX_TOKENS`: (Optional) Maximum response length

The configuration system will:

1. Load defaults from `MODEL_CONFIG`
2. Override with environment variables if present
3. Validate the configuration before use

## Usage

Run the main script:

```bash
python main.py
```

The script will:

1. Prompt for your question
2. Send it to the Perplexity AI API with progress tracking
3. Process the response (UK English conversion)
4. Save the formatted article to `article.md`

## Error Handling

The system includes robust error handling:

- API timeouts (with automatic retries)
- Connection issues
- Invalid API keys
- Rate limiting
- Server errors

Default timeout settings:

- Connection timeout: 5 seconds
- Read timeout: 180 seconds (3 minutes)
- Maximum retries: 3 with exponential backoff

## Output Format

The generated `article.md` file will contain:

- Title and description
- Main content in UK English
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

## Project Structure

- `main.py`: Main script that handles user interaction and program flow
- `article.py`: Article class and text processing functions
- `api.py`: API interaction functions with retry logic
- `config.py`: Configuration management and validation
- `utils.py`: Utility functions for input/output and progress tracking
- `tests/`: Test suite with pytest configuration
  - `conftest.py`: Test configuration
  - `test_api.py`: API interaction tests
  - `test_article.py`: Article processing tests
  - `test_config.py`: Configuration validation tests

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Tests cover:

- Configuration validation
- API interaction
- Article processing
- Error handling
- UK English conversion

```

```
