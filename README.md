# AI Ad Generator

An intelligent system that automates the process of creating ad copy for marketing campaigns by gathering insights from Reddit and generating compelling ad scripts using AI.

## Overview

The AI Ad Generator transforms the ad creation process through:

1. Intelligent research to find relevant online communities
2. Targeted data collection from Reddit discussions
3. AI-powered analysis of audience pain points and language
4. Generation of persuasive ad scripts using advanced language models
5. Review and refinement of ad content for maximum effectiveness
6. Production of practical runbooks for executing the ad campaign

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

### Platform-Specific Ad Generation
- **General**: Standard social media ad script
- **Instagram**: Optimized for Instagram with hashtags and visual descriptions
- **YouTube**: Full video script with timing, scenes, and dialogue
- **TikTok**: Ultra-concise vertical video format
- **Facebook**: Feed-optimized with headline and engagement focus
- **Video**: Generic video ad with scenes and visual directions
- **All**: Generate ads for all platforms at once

### NEW: Production Runbooks
- Automatically generates platform-specific production guides
- Detailed step-by-step instructions for creating the final ad
- Budget considerations for different production levels
- Technical specifications for each platform
- Upload instructions and best practices
- Performance tracking recommendations

### NEW: Enhanced Error Handling & Failback System
- Comprehensive retry logic with exponential backoff
- Smart fallback mechanisms when external services fail
- Stage independence to preserve successful data between steps
- Intelligent defaults generation based on product information
- Transparent disclaimer system for fallback-generated content
- Detailed logging and error reporting for easier debugging

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
python scripts/generate_multi_agent_ad.py --product-info examples/sleepwell_mattress.json --llm-provider openai
```

Options:
- `--product-info`: Path to a JSON file with product information
- `--save-intermediates`: Save intermediate results from each stage
- `--interactive`: Enter product information interactively
- `--output`: Path to save the final results (default: ad_generation_results.json)
- `--llm-provider`: LLM provider to use across all agents (openai, claude, groq; default: openai)
- `--model-name`: Specific model name to use (optional, uses default for provider if not specified)
- `--skip-reddit`: Skip Reddit scraping and rely only on LLM generation
- `--debug`: Print additional debug information
- `--no-runbook`: Skip production runbook generation
- `--max-retries`: Maximum number of retry attempts for each stage (default: 3)

### Platform-Specific Ads

Generate ad scripts optimized for specific platforms:

```bash
# Generate a YouTube video script with production runbook
python scripts/generate_multi_agent_ad.py --product-info examples/product.json --platform youtube

# Generate an Instagram ad without a runbook
python scripts/generate_multi_agent_ad.py --product-info examples/product.json --platform instagram --no-runbook

# Generate ads for all platforms at once
python scripts/generate_multi_agent_ad.py --product-info examples/product.json --platform all
```

Available platforms:
- `general`: Standard social media ad script (default)
- `instagram`: Optimized for Instagram with hashtags and visual descriptions
- `youtube`: Full video script with timing, scenes, and dialogue
- `tiktok`: Ultra-concise vertical video format
- `facebook`: Feed-optimized with headline and engagement focus
- `video`: Generic video ad with scenes and visual directions
- `all`: Generate ads for all platforms at once

### Examples

```bash
# Generate multiple platform-specific ads with Groq model and production runbooks
python scripts/generate_multi_agent_ad.py --product-info examples/sleepwell_mattress.json --llm-provider groq --platform all

# Interactive mode with YouTube video script
python scripts/generate_multi_agent_ad.py --interactive --platform youtube

# Skip Reddit scraping for faster results (LLM-only)
python scripts/generate_multi_agent_ad.py --product-info examples/product.json --skip-reddit --platform instagram
```

### Using Production Runbooks

When you generate an ad script, a platform-specific production runbook is automatically created (unless disabled with `--no-runbook`). The runbook includes:

1. **Production Steps**: Detailed guidance on creating the final ad
2. **Technical Specifications**: Platform-specific requirements (dimensions, length, etc.)
3. **Upload Instructions**: Step-by-step process for publishing the ad
4. **Budget Considerations**: Cost estimates for different production levels
5. **Performance Tracking**: Key metrics to monitor for your campaign

To use the runbook:
1. Find the generated file (e.g., `runbook_youtube_productname.md`)
2. Follow the step-by-step instructions to turn your script into a professional ad
3. Use the platform-specific upload instructions to publish your ad
4. Set up tracking based on the recommended metrics

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

## Error Handling & Failback System

The AI Ad Generator features a robust error handling system to ensure reliable operation even when external services fail or encounter rate limits.

### Key Features

1. **Multi-Stage Retry Logic**
   - Each operation attempts multiple retries with exponential backoff
   - Adjustable `max-retries` parameter to control retry attempts
   - Graceful degradation when services are unavailable

2. **Independent Stage Processing**
   - Each stage preserves data from successful previous stages
   - Reddit data is collected once and reused across retry attempts
   - Failures in later stages don't trigger re-scraping

3. **Intelligent Fallbacks**
   - When Reddit scraping fails: Generates insights directly from product info
   - When analysis fails: Falls back to algorithmically generated insights
   - When LLM providers fail: Attempts alternative providers

4. **Transparent Disclaimers**
   - Automatically adds disclaimers when fallbacks are used
   - Clearly indicates when ad scripts are generated without Reddit data
   - Provides detailed information about which stages used fallbacks

### When Fallbacks Are Used

The system will indicate when fallbacks were used through:

1. **Console Output**: Detailed logs showing retry attempts and fallback usage
2. **Results Object**: A `disclaimer` section in the results JSON with details
3. **Ad Script Disclaimer**: For critical fallbacks, a disclaimer appears at the top of the generated script

Example disclaimer in an ad script:
```
DISCLAIMER: This ad script was generated without Reddit data insights. 
It is based on product information only and may require additional customization.

---

[Ad script content follows...]
```

## Project Structure

```
ai-ad-generator/
├── src/                      # Source code
│   ├── scraping/             # Reddit scraping module
│   ├── generation/           # Ad generation module
│   ├── utils/                # Utility functions
│   │   ├── prompt_builder.py # Prompt templates
│   │   ├── json_utils.py     # JSON extraction utilities
│   │   └── runbook_generator.py # Production runbook generator
│   ├── multi_agent/          # Multi-agent architecture
│   │   └── orchestrator.py   # Agent orchestration logic
│   └── config.py             # Configuration and environment loading
├── scripts/                  # Standalone scripts
│   ├── generate_ad.py        # Basic pipeline script
│   └── generate_multi_agent_ad.py  # Multi-agent script
├── examples/                 # Example product info files
└── tests/                    # Tests
```

## Troubleshooting

### Common Issues

- **Reddit API Rate Limiting**: If you encounter 429 errors, reduce the number of requests or add delays
- **Subreddit Access Issues**: Some subreddits may return 403 errors if they're private or restricted
- **LLM Token Limits**: Very large prompts may hit token limits; reduce the number of posts or comments
- **LLM API Issues**: If you encounter errors with a specific provider, try another or check your API keys
- **Thinking Tags in Output**: If using Groq, the system will automatically remove thinking tags

### Command Line Examples for Common Issues

```bash
# If Reddit API is giving issues, skip Reddit and use LLM only
python scripts/generate_multi_agent_ad.py --product-info examples/product.json --skip-reddit

# If you're having trouble with a specific LLM provider
python scripts/generate_multi_agent_ad.py --product-info examples/product.json --llm-provider openai

# For debugging issues
python scripts/generate_multi_agent_ad.py --product-info examples/product.json --debug

# If you don't need production runbooks
python scripts/generate_multi_agent_ad.py --product-info examples/product.json --no-runbook

# Increase retry attempts for unstable environments
python scripts/generate_multi_agent_ad.py --product-info examples/product.json --max-retries 5
```

## License

[MIT License](LICENSE)