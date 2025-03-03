
"""
Prompt builder module for AI Ad Generator.
Provides functionality to create prompts for LLMs.
"""

from typing import List, Dict, Any

def prepare_llm_prompt(posts_data: List[Dict[str, Any]], product_info: Dict[str, str]) -> str:
    """Create a prompt for the LLM using the scraped data and product information.
    
    Args:
        posts_data (List[Dict[str, Any]]): List of post data dictionaries
        product_info (Dict[str, str]): Dictionary containing product information
        
    Returns:
        str: Formatted prompt for LLM
    """
    prompt = f"""
You are an expert copywriter specializing in creating viral social media ad scripts.

PRODUCT INFORMATION:
Product Name: {product_info.get('product_name', 'N/A')}
Product Description: {product_info.get('product_description', 'N/A')}
Target Audience: {product_info.get('target_audience', 'N/A')}
Key Use Cases: {product_info.get('key_use_cases', 'N/A')}
Campaign Goal: {product_info.get('campaign_goal', 'N/A')}

I've gathered insights from Reddit discussions in the {product_info.get('niche', 'relevant')} niche. 
Here are key posts and comments that reveal pain points, desires, and language of the target audience:

"""
    
    # Add top posts and their comments to the prompt
    for i, post in enumerate(posts_data, 1):
        prompt += f"\nPOST {i}: {post['title']}\n"
        prompt += f"Upvotes: {post['score']} | Comments: {post['num_comments']}\n"
        
        if post['selftext']:
            # Truncate long post content
            content = post['selftext'][:500] + "..." if len(post['selftext']) > 500 else post['selftext']
            prompt += f"Content: {content}\n"
        
        # Add top comments
        if post['top_comments']:
            prompt += "Top Comments:\n"
            for j, comment in enumerate(post['top_comments'][:3], 1):
                # Truncate long comments
                comment_text = comment['body'][:200] + "..." if len(comment['body']) > 200 else comment['body']
                prompt += f"- Comment {j} (Upvotes: {comment['score']}): {comment_text}\n"
        
        prompt += "\n" + "-"*40 + "\n"
    
    prompt += """
Based on these Reddit insights, create a compelling ad script that:
1. Addresses the key pain points identified in the discussions
2. Uses language and terminology familiar to the target audience
3. Clearly communicates the product's value proposition
4. Includes a strong call-to-action
5. Is structured for a social media ad (attention-grabbing opening, problem, solution, benefit, CTA)

Your ad script should be 150-200 words.

AD SCRIPT:
"""
    
    return prompt