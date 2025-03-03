"""
Claude (Anthropic) integration module for AI Ad Generator.
Provides functionality to generate ad scripts using Claude models.
"""

import requests
from src.config import Config

def generate_ad_script(prompt: str, model: str = None) -> str:
    """Generate ad script using Anthropic's Claude API.
    
    Args:
        prompt (str): The prompt to send to the Claude API
        model (str, optional): The Claude model to use. Defaults to Config.CLAUDE_MODEL.
        
    Returns:
        str: Generated ad script
        
    Raises:
        ValueError: If Anthropic API key is not configured
        Exception: If API request fails
    """
    # Validate Anthropic configuration
    Config.validate_llm_config("claude")
    
    # Use default model if not specified
    model = model or Config.CLAUDE_MODEL
    
    print(f"Generating ad script using Claude's {model}...")
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": Config.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"Claude API Error: {response.status_code}\n{response.text}")
    
    response_data = response.json()
    ad_script = response_data["content"][0]["text"]
    
    return ad_script