"""
Ad generation module for AI Ad Generator.
Provides functionality to generate ad scripts using various LLMs.
"""

# Import the generate_ad function from each provider
from src.generation.openai_generator import generate_ad as openai_generate
from src.generation.claude_generator import generate_ad_script as claude_generate
from src.generation.groq_generator import generate_ad_script as groq_generate

# Import additional OpenAI functions for direct access
from src.generation.openai_generator import generate_text, generate_structured_data, generate_marketing_content, review_ad_script

# Define a dictionary of available generators
providers = {
    "openai": openai_generate,
    "claude": claude_generate,
    "groq": groq_generate
}

def generate(prompt: str, provider: str = "openai", **kwargs):
    """
    Generate ad script using the specified provider.
    
    Args:
        prompt (str): The prompt to send to the LLM
        provider (str): The LLM provider to use (openai, claude, groq)
        **kwargs: Additional arguments to pass to the provider's generator
        
    Returns:
        str: Generated ad script
        
    Raises:
        ValueError: If the provider is not supported
    """
    if provider not in providers:
        raise ValueError(f"Unsupported provider: {provider}. Choose from: {', '.join(providers.keys())}")
    
    return providers[provider](prompt, **kwargs)

__all__ = ["generate", "providers", "openai_generate", "claude_generate", "groq_generate"]