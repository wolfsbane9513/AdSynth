"""
OpenAI integration module for AI Ad Generator.
Provides functionality to generate ad scripts using OpenAI models.
This module combines functionality from the original openai_generator.py and openai_pipeline.py.
"""

from openai import OpenAI
from src.config import Config
from src.utils.json_utils import extract_json_from_llm_response
from typing import Union, Dict, Any, List
import json

def get_openai_client() -> OpenAI:
    """Get configured OpenAI client.
    
    Returns:
        OpenAI: Configured OpenAI client with OPENAI_API_KEY
    """
    return OpenAI(
        base_url="https://api.openai.com/v1/",
        api_key=Config.OPENAI_API_KEY,
    )

def generate_text(prompt: str, model: str = None, system_prompt: str = None) -> str:
    """Generate text response using OpenAI.
    
    Args:
        prompt (str): Main prompt
        model (str, optional): Model to use
        system_prompt (str, optional): System prompt
        
    Returns:
        str: Generated text
    """
    # Validate configuration
    Config.validate_llm_config("openai")
    
    # Use default model if not specified
    model = model or Config.OPENAI_MODEL
    
    client = get_openai_client()
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=0.7,
        max_tokens=2000
    )
    
    return response.choices[0].message.content.strip()

def generate_structured_data(
    prompt: str,
    expected_format: Dict[str, Any],
    model: str = None,
    system_prompt: str = None
) -> Dict[str, Any]:
    """Generate structured data response using OpenAI.
    
    Args:
        prompt (str): Main prompt
        expected_format (dict): Expected response format with example values
        model (str, optional): Model to use
        system_prompt (str, optional): System prompt
        
    Returns:
        dict: Generated structured data
    """
    # Validate configuration
    Config.validate_llm_config("openai")
    
    # Create format instructions
    format_instructions = f"""
Your response must be a valid JSON object with the following structure:
{json.dumps(expected_format, indent=2)}

Return ONLY the JSON object, no other text.
"""
    
    # Combine prompts
    full_prompt = f"{prompt}\n\n{format_instructions}"
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": full_prompt})
    
    client = get_openai_client()
    response = client.chat.completions.create(
        messages=messages,
        model=model or Config.OPENAI_MODEL,
        temperature=0.7,
        max_tokens=2000
    )
    
    try:
        content = response.choices[0].message.content.strip()
        # Try to parse as JSON
        return json.loads(content)
    except json.JSONDecodeError:
        # Return a safe default that matches the expected format
        return expected_format

def generate_ad_script(prompt: str, model: str = None, stream: bool = False) -> Union[str, dict]:
    """Generate ad script using OpenAI API.
    
    Args:
        prompt (str): The prompt to send to the OpenAI API
        model (str, optional): The model to use. Defaults to Config.OPENAI_MODEL.
        stream (bool, optional): Whether to stream the response. Defaults to False.
        
    Returns:
        Union[str, dict]: Generated ad script (str) or JSON response (dict)
        
    Raises:
        ValueError: If GitHub token is not configured
        Exception: If API request fails
    """
    # Validate configuration
    Config.validate_llm_config("openai")
    
    # Use default model if not specified
    model = model or Config.OPENAI_MODEL
    
    print(f"Generating ad script using OpenAI with {model}...")
    
    try:
        # Determine if we expect a JSON response
        expects_json = any(phrase in prompt for phrase in [
            "Provide a JSON response",
            "Respond with a JSON",
            "Format your response as a JSON",
            "Return a JSON"
        ])
        
        # Add explicit JSON instruction if expecting JSON
        if expects_json:
            prompt = prompt.strip() + "\n\nIMPORTANT: Return ONLY the JSON object without any additional text, thinking process, or explanations."

        # Initialize OpenAI client
        client = get_openai_client()
        
        # Create the completion
        if not stream:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert copywriter and marketing specialist."},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON if expected
            if expects_json:
                try:
                    json_result = extract_json_from_llm_response(content)
                    if json_result:
                        return json_result
                    
                    print("Failed to extract JSON from LLM response.")
                    print("Raw response:", content[:200] + "..." if len(content) > 200 else content)
                    
                    return {
                        "score": 7,
                        "strengths": ["Generated content needs review"],
                        "weaknesses": ["JSON parsing failed"],
                        "suggestions": ["Please review the raw content"],
                        "platform_specific_feedback": "Review needed",
                        "improved_script": content
                    }
                except Exception as json_error:
                    print(f"JSON parsing error: {str(json_error)}")
                    return {
                        "score": 7,
                        "strengths": ["Generated content needs review"],
                        "weaknesses": ["JSON parsing failed"],
                        "suggestions": ["Please review the raw content"],
                        "platform_specific_feedback": "Review needed",
                        "improved_script": content
                    }
            return content
        else:
            # Streaming mode
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert copywriter and marketing specialist."},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                temperature=0.7,
                max_tokens=2000,
                stream=True,
                stream_options={'include_usage': True}
            )
            
            content = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    chunk_content = chunk.choices[0].delta.content
                    print(chunk_content, end="", flush=True)
                    content += chunk_content
            
            if expects_json:
                try:
                    json_result = extract_json_from_llm_response(content)
                    if json_result:
                        return json_result
                except Exception:
                    return {
                        "score": 7,
                        "strengths": ["Generated content needs review"],
                        "weaknesses": ["JSON parsing failed"],
                        "suggestions": ["Please review the raw content"],
                        "platform_specific_feedback": "Review needed",
                        "improved_script": content
                    }
            return content.strip()
            
    except Exception as e:
        # Print detailed error information
        print(f"OpenAI API Error: {str(e)}")
        if expects_json:
            return {
                "score": 5,
                "strengths": ["Error occurred"],
                "weaknesses": ["API error occurred"],
                "suggestions": ["Try again or use a different model"],
                "platform_specific_feedback": f"Error: {str(e)}",
                "improved_script": "Error occurred during generation"
            }
        raise

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
        ValueError: If GitHub token is not configured
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

def analyze_content(content: str, criteria: List[str], model: str = None) -> Dict[str, Any]:
    """Analyze content based on given criteria.
    
    Args:
        content (str): Content to analyze
        criteria (list): List of criteria to evaluate
        model (str, optional): Model to use
        
    Returns:
        dict: Analysis results
    """
    expected_format = {
        "score": 7,
        "strengths": ["Example strength"],
        "weaknesses": ["Example weakness"],
        "suggestions": ["Example suggestion"],
        "platform_specific_feedback": "Example feedback"
    }
    
    prompt = f"""
Analyze the following content based on these criteria: {', '.join(criteria)}

Content to analyze:
{content}

Provide a detailed analysis including:
1. Overall score (1-10)
2. Key strengths (2-3 points)
3. Areas for improvement (2-3 points)
4. Specific suggestions
5. Platform-specific feedback
"""
    
    return generate_structured_data(
        prompt=prompt,
        expected_format=expected_format,
        model=model,
        system_prompt="You are an expert content analyst and marketing specialist."
    )

def generate_marketing_content(
    product_info: Dict[str, str],
    insights: Dict[str, Any] = None,
    platform: str = "general",
    model: str = None
) -> str:
    """Generate marketing content based on product info and insights.
    
    Args:
        product_info (dict): Product information
        insights (dict, optional): Additional insights
        platform (str, optional): Target platform
        model (str, optional): Model to use
        
    Returns:
        str: Generated marketing content
    """
    # Build the prompt
    prompt = f"""Create an engaging ad script for {product_info['product_name']}.

Product Details:
- Description: {product_info['product_description']}
- Target Audience: {product_info['target_audience']}
- Key Use Cases: {product_info.get('key_use_cases', 'Not specified')}
- Campaign Goal: {product_info.get('campaign_goal', 'Not specified')}
"""
    
    if insights:
        prompt += f"""
Key Insights:
- Pain Points: {', '.join(insights.get('pain_points', []))}
- Audience Language: {', '.join(insights.get('language', []))}
- Trending Topics: {', '.join(insights.get('topics', []))}
"""
    
    # Add platform-specific instructions
    platform_instructions = {
        "instagram": "Create a visually descriptive Instagram post with relevant hashtags.",
        "facebook": "Write an engaging Facebook ad that encourages comments and shares.",
        "twitter": "Create a punchy Twitter thread (3-5 tweets) that drives engagement.",
        "linkedin": "Write a professional LinkedIn post that establishes authority.",
        "tiktok": "Create a script for a viral-worthy TikTok video (15-30 seconds)."
    }
    
    if platform in platform_instructions:
        prompt += f"\nPlatform-specific requirements:\n{platform_instructions[platform]}"
    
    return generate_text(
        prompt=prompt,
        model=model,
        system_prompt="You are an expert copywriter and marketing specialist."
    )

def review_ad_script(
    script: str,
    product_info: Dict[str, str],
    platform: str = "general",
    model: str = None
) -> Dict[str, Any]:
    """Review and provide feedback on an ad script.
    
    Args:
        script (str): Ad script to review
        product_info (dict): Product information
        platform (str): Target platform
        model (str, optional): Model to use
        
    Returns:
        dict: Review feedback
    """
    expected_format = {
        "score": 7,
        "strengths": ["Example strength"],
        "weaknesses": ["Example weakness"],
        "suggestions": ["Example suggestion"],
        "platform_specific_feedback": "Example feedback",
        "improved_script": "Example improved script"
    }
    
    prompt = f"""Review this {platform} ad script for {product_info['product_name']}.

Product Information:
- Description: {product_info['product_description']}
- Target Audience: {product_info['target_audience']}
- Campaign Goal: {product_info.get('campaign_goal', 'Not specified')}

Original Script:
{script}

Provide a detailed review including:
1. Overall score (1-10)
2. Key strengths (2-3 points)
3. Areas for improvement (2-3 points)
4. Specific suggestions for improvement
5. Platform-specific feedback
6. An improved version of the script
"""
    
    return generate_structured_data(
        prompt=prompt,
        expected_format=expected_format,
        model=model,
        system_prompt="You are an expert copywriter and marketing specialist."
    )