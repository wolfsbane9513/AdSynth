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
Use Cases: {product_info.get('use_cases', product_info.get('key_use_cases', 'N/A'))}
Niche: {product_info.get('niche', 'Not specified')}
Keywords: {product_info.get('keywords', 'Not specified')}
Campaign Goal: {product_info.get('campaign_goal', 'N/A')}

I've gathered insights from Reddit discussions in the {product_info.get('niche', product_info.get('keywords', 'relevant'))} niche. 
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

def build_research_prompt(product_info: Dict[str, str]) -> str:
    """Create a prompt for finding relevant subreddits.
    
    Args:
        product_info (Dict[str, str]): Dictionary containing product information
        
    Returns:
        str: Formatted prompt for LLM
    """
    return f"""
Given this product information:
Product Name: {product_info['product_name']}
Product Description: {product_info['product_description']}
Use Cases: {product_info.get('use_cases', 'Not specified')}
Niche: {product_info.get('niche', 'Not specified')}
Keywords: {product_info.get('keywords', 'Not specified')}
Target Audience: {product_info['target_audience']}

Provide a list of 5-7 most relevant subreddits where discussions about this product's 
use cases, pain points, or target audience would occur.

Choose subreddits where:
1. The target audience is likely to participate
2. Discussions about the product's niche and use cases occur
3. People discuss problems that this product solves

Return ONLY a comma-separated list of subreddit names without the 'r/' prefix.
For example: productivity, sleep, selfimprovement
"""

def build_query_prompt(product_info: Dict[str, str]) -> str:
    """Create a prompt for generating search queries.
    
    Args:
        product_info (Dict[str, str]): Dictionary containing product information
        
    Returns:
        str: Formatted prompt for LLM
    """
    return f"""
Generate 5 specific search queries to find relevant discussions about this product:

Product Name: {product_info['product_name']}
Product Description: {product_info['product_description']}
Use Cases: {product_info.get('use_cases', 'Not specified')}
Niche: {product_info.get('niche', 'Not specified')}
Keywords: {product_info.get('keywords', 'Not specified')}
Target Audience: {product_info['target_audience']}

The search queries should:
1. Find discussions about pain points that this product solves
2. Include language used by the target audience
3. Incorporate relevant keywords from the provided list
4. Be specific enough to find focused discussions, not generic content
5. Include terms related to the product's use cases

Return ONLY a comma-separated list of search queries.
"""

def build_relevance_prompt(posts_data: List[Dict[str, Any]], product_info: Dict[str, str]) -> str:
    """Create a prompt for evaluating post relevance.
    
    Args:
        posts_data (List[Dict[str, Any]]): List of post data dictionaries
        product_info (Dict[str, str]): Dictionary containing product information
        
    Returns:
        str: Formatted prompt for LLM
    """
    prompt = f"""
Rate each post's relevance to this product on a scale of 0-10:
Product: {product_info['product_name']} - {product_info['product_description']}
Target audience: {product_info['target_audience']}
Use cases: {product_info.get('use_cases', 'Not specified')}
Keywords: {product_info.get('keywords', 'Not specified')}

For each post, provide a JSON object with the following structure:
{{
    "post_index": <index of the post>,
    "relevance_score": <0-10 score>,
    "reason": <brief explanation for the score>
}}

Respond with a JSON array containing evaluations for all posts.

Here are the posts to evaluate:
"""
    
    # Add posts to the prompt (with a limit to prevent token overflow)
    batch_size = min(10, len(posts_data))
    batch = posts_data[:batch_size]
    
    for i, post in enumerate(batch):
        prompt += f"\nPost {i}:\nTitle: {post['title']}\n"
        content = post['selftext'][:500] + "..." if len(post['selftext']) > 500 else post['selftext']
        prompt += f"Content: {content}\n"
        
        # Add a sample of comments
        if post['top_comments']:
            prompt += "Top Comments:\n"
            for j, comment in enumerate(post['top_comments'][:2]):
                comment_text = comment['body'][:200] + "..." if len(comment['body']) > 200 else comment['body']
                prompt += f"- Comment {j+1}: {comment_text}\n"
    
    return prompt

def build_insights_prompt(posts_data: List[Dict[str, Any]], product_info: Dict[str, str]) -> str:
    """Create a prompt for extracting key insights.
    
    Args:
        posts_data (List[Dict[str, Any]]): List of post data dictionaries
        product_info (Dict[str, str]): Dictionary containing product information
        
    Returns:
        str: Formatted prompt for LLM
    """
    prompt = f"""
Analyze these Reddit posts related to {product_info['product_name']} ({product_info['product_description']}).

Extract the following information:
1. Key pain points mentioned by users
2. Common phrases and language used by the target audience
3. Trending topics relevant to the product
4. General insights that would be valuable for creating an ad

Product information:
- Name: {product_info['product_name']}
- Description: {product_info['product_description']}
- Target audience: {product_info['target_audience']}
- Use cases: {product_info.get('use_cases', 'Not specified')}
- Keywords: {product_info.get('keywords', 'Not specified')}

Respond with a JSON object with the following structure:
{{
    "pain_points": [list of 3-5 specific pain points],
    "language": [list of 5-7 phrases, terms, or expressions used by the audience],
    "topics": [list of 3-5 trending topics],
    "insights": "A paragraph summarizing key insights for ad creation"
}}

Here are the posts to analyze:
"""
    
    # Add posts to the prompt (with a limit to prevent token overflow)
    for i, post in enumerate(posts_data[:5]):
        prompt += f"\nPost {i+1}:\nTitle: {post['title']}\n"
        content = post['selftext'][:300] + "..." if len(post['selftext']) > 300 else post['selftext']
        prompt += f"Content: {content}\n"
        
        # Add a sample of comments
        if post['top_comments']:
            prompt += "Top Comments:\n"
            for j, comment in enumerate(post['top_comments'][:2]):
                comment_text = comment['body'][:150] + "..." if len(comment['body']) > 150 else comment['body']
                prompt += f"- Comment {j+1}: {comment_text}\n"
    
    return prompt

def build_ad_script_prompt(insights: Dict[str, Any], product_info: Dict[str, str]) -> str:
    """Create a prompt for generating an ad script.
    
    Args:
        insights (Dict[str, Any]): Dictionary containing insights from analysis
        product_info (Dict[str, str]): Dictionary containing product information
        
    Returns:
        str: Formatted prompt for LLM
    """
    return f"""
You are an expert copywriter creating a viral social media ad script.

PRODUCT INFORMATION:
Product Name: {product_info['product_name']}
Product Description: {product_info['product_description']}
Target Audience: {product_info['target_audience']}
Use Cases: {product_info.get('use_cases', 'Not specified')}
Keywords: {product_info.get('keywords', 'Not specified')}
Campaign Goal: {product_info['campaign_goal']}

INSIGHTS FROM AUDIENCE ANALYSIS:
Pain Points: {', '.join(insights['pain_points'])}
Audience Language: {', '.join(insights['language'])}
Trending Topics: {', '.join(insights['topics'])}

Key Insights: {insights['insights']}

Based on these insights, create a compelling ad script that:
1. Addresses the key pain points identified
2. Uses language and terminology familiar to the target audience
3. Ties into trending topics when relevant
4. Clearly communicates the product's value proposition
5. Includes a strong call-to-action

Your ad script should be 150-200 words and structured for a social media ad:
- Attention-grabbing opening
- Problem statement
- Solution (product introduction)
- Benefits
- Call-to-action

AD SCRIPT:
"""

def build_review_prompt(ad_script: str, product_info: Dict[str, str], insights: Dict[str, Any]) -> str:
    """Create a prompt for reviewing an ad script.
    
    Args:
        ad_script (str): The ad script to review
        product_info (Dict[str, str]): Dictionary containing product information
        insights (Dict[str, Any]): Dictionary containing insights from analysis
        
    Returns:
        str: Formatted prompt for LLM
    """
    return f"""
Review this ad script for {product_info['product_name']} and evaluate it based on:

1. Relevance to the product and target audience
2. Use of audience language and addressing pain points
3. Clarity of value proposition
4. Effectiveness of call-to-action
5. Overall persuasiveness

Product: {product_info['product_description']}
Target Audience: {product_info['target_audience']}
Campaign Goal: {product_info['campaign_goal']}
Use Cases: {product_info.get('use_cases', 'Not specified')}
Keywords: {product_info.get('keywords', 'Not specified')}

Pain Points: {', '.join(insights['pain_points'])}
Audience Language: {', '.join(insights['language'])}

AD SCRIPT:
{ad_script}

Provide a JSON response with:
{{
    "score": <1-10 overall score>,
    "strengths": [list of 2-3 strengths],
    "weaknesses": [list of 2-3 areas for improvement],
    "suggestions": [list of 2-3 specific suggestions],
    "improved_script": "An improved version of the script incorporating your suggestions"
}}
"""