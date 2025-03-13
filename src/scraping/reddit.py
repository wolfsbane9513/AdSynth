"""
Reddit scraping module for AI Ad Generator.
Provides functionality to scrape Reddit posts and comments.
"""

import praw
from typing import List, Dict, Any
from src.config import Config

def init_reddit_client() -> praw.Reddit:
    """Initialize and return Reddit client.
    
    Returns:
        praw.Reddit: Initialized Reddit client
        
    Raises:
        ValueError: If Reddit API credentials are not configured
    """
    # Validate Reddit configuration
    Config.validate_reddit_config()
    
    return praw.Reddit(
        client_id=Config.REDDIT_CLIENT_ID,
        client_secret=Config.REDDIT_CLIENT_SECRET,
        user_agent=Config.REDDIT_USER_AGENT,
    )

def scrape_subreddit(
    subreddit_name: str, 
    limit: int = Config.DEFAULT_POST_LIMIT,
    comment_limit: int = Config.DEFAULT_COMMENT_LIMIT
) -> List[Dict[str, Any]]:
    """Scrape top posts from a subreddit and return structured data.
    
    Args:
        subreddit_name (str): Name of the subreddit to scrape
        limit (int, optional): Maximum number of posts to scrape. Defaults to Config.DEFAULT_POST_LIMIT.
        comment_limit (int, optional): Maximum number of comments to fetch per post. Defaults to Config.DEFAULT_COMMENT_LIMIT.
        
    Returns:
        List[Dict[str, Any]]: List of post data dictionaries
    """
    print(f"Scraping r/{subreddit_name}...")
    
    # Initialize Reddit client
    reddit_client = init_reddit_client()
    subreddit = reddit_client.subreddit(subreddit_name)
    posts_data = []
    
    # Get top posts from the subreddit
    for post in subreddit.hot(limit=limit):
        post_data = {
            'title': post.title,
            'selftext': post.selftext,
            'score': post.score,
            'num_comments': post.num_comments,
            'url': f"https://www.reddit.com{post.permalink}",
            'created_utc': post.created_utc,
            'top_comments': []
        }
        
        # Get top comments for each post
        post.comments.replace_more(limit=0)  # Remove comment stubs
        for comment in post.comments[:comment_limit]:
            if comment.body and len(comment.body) > 20:  # Filter out short comments
                post_data['top_comments'].append({
                    'body': comment.body,
                    'score': comment.score
                })
        
        posts_data.append(post_data)
    
    print(f"Scraped {len(posts_data)} posts with {sum(len(post['top_comments']) for post in posts_data)} comments")
    return posts_data

def get_relevant_posts(product_name: str, niche: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get relevant Reddit posts for a product and niche.
    
    Args:
        product_name (str): Name of the product
        niche (str): Product niche/category
        limit (int, optional): Maximum number of posts to return. Defaults to 5.
        
    Returns:
        List[Dict[str, Any]]: List of relevant Reddit posts
    """
    # Use the product's niche as the subreddit
    # This is a simple implementation - could be improved with better subreddit selection
    try:
        posts = scrape_subreddit(niche.lower(), limit=limit)
        return posts
    except Exception as e:
        print(f"Error fetching Reddit posts: {str(e)}")
        return []  # Return empty list if scraping fails