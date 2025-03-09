"""
OpenAI integration module for AI Ad Generator.
Provides functionality to generate ad scripts using OpenAI models.
"""

import requests
from src.config import Config

def generate_ad_script(prompt: str, model: str = None) -> str:
    """Generate ad script using OpenAI API.
    
    Args:
        prompt (str): The prompt to send to the OpenAI API
        model (str, optional): The OpenAI model to use. Defaults to Config.OPENAI_MODEL.
        
    Returns:
        str: Generated ad script
        
    Raises:
        ValueError: If OpenAI API key is not configured
        Exception: If API request fails
    """
    # Validate OpenAI configuration
    Config.validate_llm_config("openai")
    
    # Use default model if not specified
    model = model or Config.OPENAI_MODEL
    
    print(f"Generating ad script using OpenAI's {model}...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Config.OPENAI_API_KEY}"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"OpenAI API Error: {response.status_code}\n{response.text}")
    
    response_data = response.json()
    ad_script = response_data["choices"][0]["message"]["content"].strip()
    
    return ad_script