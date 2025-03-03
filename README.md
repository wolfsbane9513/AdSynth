# AdSynth
# AI Ad Generator - Barebones Pipeline

This repository contains a barebones implementation of an AI Ad Generator that collects insights from Reddit and uses various LLMs to generate ad copy.

## Overview

The AI Ad Generator automates the process of creating ad copy for marketing campaigns. It:

1. Gathers insights from Reddit's top threads in a specific niche
2. Extracts user pain points, questions, and trending topics
3. Uses LLMs (OpenAI, Claude, or Groq) to generate compelling ad copy
4. Provides output in a format ready for marketing use

## Features

- Reddit data scraping with PRAW
- Support for multiple LLM providers:
  - OpenAI (GPT-4o, etc.)
  - Claude (Anthropic)
  - Groq (Deepseek, Llama, etc.)
- Customizable prompt generation
- Simple command-line interface

## Setup

### Prerequisites

- Python 3.8+
- Reddit API credentials
- API keys for at least one LLM provider (OpenAI, Anthropic, or Groq)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-ad-generator.git
   cd ai-ad-generator
   ```

2. Set up a virtual environment:
   ```bash
   # For Windows
   python -m venv venv
   venv\Scripts\activate

   # For macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.template` and add your API credentials:
   ```bash
   cp .env.template .env
   # Edit .env with your credentials
   ```

## Usage

Run the main script to generate an ad:

```bash
python scripts/generate_ad.py --subreddit productivity --model openai
```

Available options:
- `--subreddit`: The subreddit to scrape (default: "productivity")
- `--limit`: Number of posts to scrape (default: 7)
- `--model`: LLM provider to use (options: "openai", "claude", "groq", "all"; default: "all")
- `--product-info`: Path to a JSON file with product information (optional)
- `--save-data`: Save scraped data and prompts to files
- `--stream`: Stream output for models that support it (currently only Groq)

### Example Product Info JSON

```json
{
  "product_name": "FocusFlow",
  "product_description": "A productivity app that helps users maintain focus and track their work habits.",
  "target_audience": "Remote workers, freelancers, and students who struggle with distractions",
  "key_use_cases": "Deep work sessions, deadline management, habit building",
  "campaign_goal": "Increase app downloads and free trial signups",
  "niche": "productivity"
}
```

## Project Structure

```
ai-ad-generator/
├── src/                      # Source code
│   ├── scraping/             # Reddit scraping module
│   ├── generation/           # Ad generation module
│   ├── utils/                # Utility functions
│   └── config.py             # Configuration and environment loading
├── scripts/                  # Standalone scripts
└── tests/                    # Tests for your code
```

## Development

This project is structured to allow for easy extension and modification:

- Add new LLM providers in the `generation/` module
- Modify prompt templates in the `utils/prompt_builder.py` file
- Extend the Reddit scraping functionality in the `scraping/reddit.py` file

## License

[MIT License](LICENSE)