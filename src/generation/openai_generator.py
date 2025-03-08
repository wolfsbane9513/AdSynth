"""
OpenAI integration module for AI Ad Generator.
Provides functionality to generate ad scripts using OpenAI models.
"""

import requests
from src.config import Config

def generate_ad(product_name: str, product_description: str, target_audience: str,
               key_use_cases: str, campaign_goal: str, reddit_posts: list) -> str:
    """Generate ad script using OpenAI API.
    
    Args:
        product_name (str): Name of the product
        product_description (str): Description of the product
        target_audience (str): Target audience description
        key_use_cases (str): Key use cases of the product
        campaign_goal (str): Goal of the ad campaign
        reddit_posts (list): List of relevant Reddit posts
        
    Returns:
        str: Generated ad script
        
    Raises:
        ValueError: If OpenAI API key is not configured
        Exception: If API request fails
    """
    # Validate OpenAI configuration
    Config.validate_llm_config("openai")
    
    # Construct prompt
    prompt = f"""Create an engaging ad script for {product_name}.

Product Details:
- Description: {product_description}
- Target Audience: {target_audience}
- Key Use Cases: {key_use_cases}
- Campaign Goal: {campaign_goal}

Incorporate insights from these relevant Reddit discussions:
"""
    
    # Add Reddit insights
    for post in reddit_posts[:3]:  # Use top 3 posts
        prompt += f"\n- {post['title']}"
        if post['comments']:
            top_comment = max(post['comments'], key=lambda x: x['score'])
            prompt += f"\n  Top comment: {top_comment['body'][:200]}..."
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Config.OPENAI_API_KEY}"
    }
    
    payload = {
        "model": Config.OPENAI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        raise Exception(f"OpenAI API Error: {response.status_code}\n{response.text}")
    
    return response.json()["choices"][0]["message"]["content"].strip()