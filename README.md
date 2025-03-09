# AI Ad Generator

An intelligent system that automates the process of creating ad copy for marketing campaigns by gathering insights from Reddit and generating compelling ad scripts using AI.

## Overview

The AI Ad Generator transforms the ad creation process through:

1. Intelligent research to find relevant online communities
2. Targeted data collection from Reddit discussions
3. AI-powered analysis of audience pain points and language
4. Generation of persuasive ad scripts using advanced language models
5. Review and refinement of ad content for maximum effectiveness

## Features

### Basic Pipeline
- Reddit data scraping with PRAW
- Support for multiple LLM providers:
  - OpenAI (GPT-4o, etc.)
  - Claude (Anthropic)
  - Groq (Deepseek, Llama, etc.)
- Customizable prompt generation
- Simple command-line interface

### Advanced Multi-Agent System
- Research Agent: Finds relevant subreddits and generates targeted search queries
- Data Collection Agent: Performs focused searches across multiple communities
- Analysis Agent: Evaluates content relevance and extracts key insights
- Copywriting Agent: Creates compelling ad scripts based on audience insights
- Review Agent: Evaluates and refines the ad content
- **NEW**: Consistent LLM selection across all agents

## Setup

### Prerequisites

- Python 3.8+
- Reddit API credentials (client ID, client secret)
- API key for at least one LLM provider (OpenAI, Anthropic, or Groq)

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

### Basic Pipeline

Run the basic pipeline to generate an ad based on a single subreddit:

```bash
python scripts/generate_ad.py --subreddit productivity --model openai
```

Options:
- `--subreddit`: The subreddit to scrape (default: "productivity")
- `--limit`: Number of posts to scrape (default: 7)
- `--model`: LLM provider to use (options: "openai", "claude", "groq", "all"; default: "all")
- `--save-data`: Save scraped data and prompts to files

### Multi-Agent System (Recommended)

For a more targeted approach that finds relevant content across multiple subreddits:

```bash
python scripts/generate_multi_agent_ad.py --product-info examples/sleepwell_mattress.json --llm-provider groq
```

Options:
- `--product-info`: Path to a JSON file with product information
- `--save-intermediates`: Save intermediate results from each stage
- `--interactive`: Enter product information interactively
- `--output`: Path to save the final results (default: ad_generation_results.json)
- `--llm-provider`: LLM provider to use across all agents (openai, claude, groq; default: openai)
- `--model-name`: Specific model name to use (optional, uses default for provider if not specified)

Examples:
```bash
# Use OpenAI's GPT-4o model across all agents
python scripts/generate_multi_agent_ad.py --product-info examples/product.json --llm-provider openai --model-name gpt-4o

# Use Claude for all steps of the process
python scripts/generate_multi_agent_ad.py --product-info examples/product.json --llm-provider claude

# Use Groq with the Deepseek model
python scripts/generate_multi_agent_ad.py --product-info examples/product.json --llm-provider groq --model-name deepseek-r1-distill-llama-70b
```

### Product Information Format

Create a JSON file with the following structure for best results:

```json
{
  "product_name": "SleepWell Mattress",
  "product_description": "A premium memory foam mattress designed to provide optimal spine alignment and pressure relief.",
  "use_cases": "Reducing back pain, improving sleep quality, eliminating partner disturbance, temperature regulation",
  "niche": "Sleep health, wellness, back pain management",
  "keywords": "memory foam, spine alignment, pressure relief, back pain, sleep quality",
  "target_audience": "Health-conscious adults ages 30-65 who struggle with sleep quality or back pain.",
  "campaign_goal": "Increase direct-to-consumer sales and free in-home trials by 25%"
}
```

## Project Structure

```
ai-ad-generator/
├── src/                      # Source code
│   ├── scraping/             # Reddit scraping module
│   ├── generation/           # Ad generation module
│   ├── utils/                # Utility functions
│   │   ├── prompt_builder.py # Prompt templates
│   │   └── json_utils.py     # JSON extraction utilities
│   ├── multi_agent/          # Multi-agent architecture
│   │   └── orchestrator.py   # Agent orchestration logic
│   └── config.py             # Configuration and environment loading
├── scripts/                  # Standalone scripts
│   ├── generate_ad.py        # Basic pipeline script
│   └── generate_multi_agent_ad.py  # Multi-agent script
├── examples/                 # Example product info files
└── tests/                    # Tests
```

## Development

This project is structured to allow for easy extension and modification:

- Add new LLM providers in the `generation/` module
- Modify prompt templates in the `utils/prompt_builder.py` file
- Extend the multi-agent system in the `multi_agent/orchestrator.py` file

### Adding a New LLM Provider

1. Create a new module in `src/generation/`
2. Implement a `generate_ad_script` function
3. Update the BaseAgent class in `src/multi_agent/orchestrator.py`

### Creating Custom Product Info Files

For best results, provide detailed information in all fields:
- `product_name`: Short, recognizable name
- `product_description`: 1-2 sentences describing key features
- `use_cases`: Comma-separated list of primary uses
- `niche`: Industry or category
- `keywords`: Important terms related to the product
- `target_audience`: Detailed description of the ideal customer
- `campaign_goal`: Clear objective for the ad campaign

## Examples

See the `examples/` directory for sample product info files:
- `sleepwell_mattress.json`: Premium mattress example
- `focusflow_app.json`: Productivity app example

## Troubleshooting

### Common Issues

- **Reddit API Rate Limiting**: If you encounter 429 errors, reduce the number of requests or add delays
- **Subreddit Access Issues**: Some subreddits may return 403 errors if they're private or restricted
- **LLM Token Limits**: Very large prompts may hit token limits; reduce the number of posts or comments
- **LLM API Issues**: If you encounter errors with a specific provider, try another or check your API keys

### Getting Help

If you encounter any issues or have questions, please file an issue on the repository.

## License

[MIT License](LICENSE)

## Contributors

- @wolfsbane9513
- @dsaidinesh
- @Abhiram007G