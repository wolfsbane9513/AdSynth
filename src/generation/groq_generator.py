"""
Groq integration module for AI Ad Generator.
Provides functionality to generate ad scripts using models via Groq's API.
"""

from groq import Groq
from src.config import Config
from src.utils.json_utils import extract_json_from_llm_response
from typing import Union

def generate_ad_script(prompt: str, model: str = None, stream: bool = False) -> str:
    """Generate ad script using Groq API.
    
    Args:
        prompt (str): The prompt to send to the Groq API
        model (str, optional): The model to use. Defaults to Config.GROQ_MODEL.
        stream (bool, optional): Whether to stream the response. Defaults to False.
        
    Returns:
        Union[str, dict]: Generated ad script (str) or JSON response (dict)
        
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
            
            # Get the content and clean it
            content = completion.choices[0].message.content
            # Remove thinking tags if present
            content = content.replace("<think>", "").replace("</think>", "").strip()
            
            # Parse JSON if expected
            if expects_json:
                try:
                    # Try to extract JSON first
                    json_result = extract_json_from_llm_response(content)
                    if json_result:
                        return json_result
                    
                    print("Failed to extract JSON from LLM response.")
                    print("Raw response:", content[:200] + "..." if len(content) > 200 else content)
                    
                    # Return a default JSON structure that won't break the flow
                    return {
                        "score": 7,
                        "strengths": ["Generated content needs review"],
                        "weaknesses": ["JSON parsing failed"],
                        "suggestions": ["Please review the raw content"],
                        "platform_specific_feedback": "Review needed",
                        "improved_script": content  # Use the raw content as the script
                    }
                except Exception as json_error:
                    print(f"JSON parsing error: {str(json_error)}")
                    # Return a safe default structure
                    return {
                        "score": 7,
                        "strengths": ["Generated content needs review"],
                        "weaknesses": ["JSON parsing failed"],
                        "suggestions": ["Please review the raw content"],
                        "platform_specific_feedback": "Review needed",
                        "improved_script": content  # Use the raw content as the script
                    }
            return content
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
            # Clean the content
            raw_content = raw_content.replace("<think>", "").replace("</think>", "").strip()
            
            # Parse JSON if expected
            if expects_json:
                try:
                    json_result = extract_json_from_llm_response(raw_content)
                    if json_result:
                        return json_result
                    
                    print("Failed to extract JSON from LLM response.")
                    print("Raw response:", raw_content[:200] + "..." if len(raw_content) > 200 else raw_content)
                    
                    # Return a default JSON structure that won't break the flow
                    return {
                        "score": 7,
                        "strengths": ["Generated content needs review"],
                        "weaknesses": ["JSON parsing failed"],
                        "suggestions": ["Please review the raw content"],
                        "platform_specific_feedback": "Review needed",
                        "improved_script": raw_content  # Use the raw content as the script
                    }
                except Exception as json_error:
                    print(f"JSON parsing error: {str(json_error)}")
                    # Return a safe default structure
                    return {
                        "score": 7,
                        "strengths": ["Generated content needs review"],
                        "weaknesses": ["JSON parsing failed"],
                        "suggestions": ["Please review the raw content"],
                        "platform_specific_feedback": "Review needed",
                        "improved_script": raw_content  # Use the raw content as the script
                    }
            return raw_content
    except Exception as e:
        # Print detailed error information
        print(f"Groq API Error: {str(e)}")
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