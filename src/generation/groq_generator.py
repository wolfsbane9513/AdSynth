"""
Groq integration module for AI Ad Generator.
Provides functionality to generate ad scripts using models via Groq's API.
"""

from groq import Groq
from src.config import Config

def generate_ad_script(prompt: str, model: str = None, stream: bool = False) -> str:
    """Generate ad script using Groq API.
    
    Args:
        prompt (str): The prompt to send to the Groq API
        model (str, optional): The model to use. Defaults to Config.GROQ_MODEL.
        stream (bool, optional): Whether to stream the response. Defaults to False.
        
    Returns:
        str: Generated ad script
        
    Raises:
        ValueError: If Groq API key is not configured
        Exception: If API request fails
    """
    # Validate Groq configuration
    Config.validate_llm_config("groq")
    
    # Use default model if not specified
    model = model or Config.GROQ_MODEL
    
    print(f"Generating ad script using Groq with {model}...")
    
    # Initialize Groq client
    client = Groq(api_key=Config.GROQ_API_KEY)
    
    if not stream:
        # Non-streaming mode: get complete response at once
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=500,
            top_p=0.95,
            stream=False,
        )
        
        # Extract the ad script from the response
        ad_script = completion.choices[0].message.content
        return ad_script
    else:
        # Streaming mode: show output as it's generated
        ad_script = ""
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=500,
            top_p=0.95,
            stream=True,
        )
        
        print("\nGenerating ad script (streaming):")
        for chunk in completion:
            chunk_content = chunk.choices[0].delta.content or ""
            print(chunk_content, end="", flush=True)
            ad_script += chunk_content
        
        print("\n")
        return ad_script