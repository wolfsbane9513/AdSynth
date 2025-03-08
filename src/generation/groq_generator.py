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
    
    try:
        # Initialize Groq client - avoiding any proxy configuration
        client = Groq(api_key=Config.GROQ_API_KEY)
        
        if not stream:
            # Non-streaming mode: get complete response at once
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=2000,
                top_p=0.95,
                stream=False,
            )
            
            # Extract the ad script from the response
            raw_content = completion.choices[0].message.content
            # Process the raw content to extract only the ad script
            ad_script = process_ad_script_content(raw_content)
            return ad_script
        else:
            # Streaming mode: show output as it's generated
            raw_content = ""
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
                raw_content += chunk_content
            
            print("\n")
            # Process the raw content to extract only the ad script
            ad_script = process_ad_script_content(raw_content)
            return ad_script
    except Exception as e:
        # Print detailed error information
        print(f"Groq API Error: {str(e)}")
        raise

def process_ad_script_content(raw_content: str) -> str:
    """Process the raw content from LLM to extract only the properly formatted ad script.
    
    Args:
        raw_content (str): Raw content from LLM including thinking process and formatting tags
        
    Returns:
        str: Clean, properly formatted ad script content
    """
    # Check if the content contains a thinking section
    if '<think>' in raw_content and '</think>' in raw_content:
        # Remove the thinking section
        start_idx = raw_content.find('<think>')
        end_idx = raw_content.find('</think>') + len('</think>')
        raw_content = raw_content[:start_idx] + raw_content[end_idx:]
    
    # Extract content between '*AD SCRIPT:*' marker if present
    if '*AD SCRIPT:*' in raw_content:
        start_idx = raw_content.find('*AD SCRIPT:*') + len('*AD SCRIPT:*')
        # Find the end of the script (before any trailing questions or comments)
        possible_endings = ['#', 'so what', 'what are', 'how can', 'CTA:']
        end_indices = [raw_content.rfind(ending) for ending in possible_endings if raw_content.rfind(ending) > start_idx]
        
        if end_indices:
            # Use the earliest ending marker found
            end_idx = min(end_indices)
            # If the ending is a hashtag, include it and any other hashtags
            if raw_content[end_idx] == '#':
                # Find the end of the hashtags section
                hashtag_end = raw_content.find('\n\n', end_idx)
                if hashtag_end != -1:
                    end_idx = hashtag_end
                else:
                    # If no double newline after hashtags, look for CTA
                    cta_idx = raw_content.find('*CTA:*', end_idx)
                    if cta_idx != -1:
                        end_idx = cta_idx
        else:
            # If no specific ending found, use the entire remaining content
            end_idx = len(raw_content)
        
        # Extract the script content
        script_content = raw_content[start_idx:end_idx].strip()
        
        # Check if there's a CTA section to include
        if '*CTA:*' in raw_content and end_idx < raw_content.find('*CTA:*'):
            cta_start = raw_content.find('*CTA:*')
            cta_end = raw_content.find('\n\n', cta_start)
            if cta_end == -1:
                cta_end = len(raw_content)
            cta_content = raw_content[cta_start:cta_end].strip()
            script_content += '\n\n' + cta_content
    else:
        # If no AD SCRIPT marker, return the content as is but clean up any obvious markers
        script_content = raw_content.strip()
    
    return script_content


def generate_ad(product_name: str, product_description: str, target_audience: str,
               key_use_cases: str, campaign_goal: str, reddit_posts: list) -> str:
    """Generate ad script using Groq API.
    
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
        ValueError: If Groq API key is not configured
        Exception: If API request fails
    """
    # Construct prompt
    prompt = f"""Create an engaging ad script for {product_name}.

Product Details:
- Description: {product_description}
- Target Audience: {target_audience}
- Key Use Cases: {key_use_cases}
- Campaign Goal: {campaign_goal}

Incorporate insights from these relevant Reddit discussions:"""
    
    # Add Reddit insights
    for post in reddit_posts[:3]:  # Use top 3 posts
        prompt += f"\n- {post.get('title', '')}"
        comments = post.get('comments', [])
        if comments:
            top_comment = max(comments, key=lambda x: x.get('score', 0))
            prompt += f"\n  Top comment: {top_comment.get('body', '')[:200]}..."
    
    return generate_ad_script(prompt)