
"""
Multi-Agent Architecture for AI Ad Generator.
This module orchestrates multiple specialized agents to create relevant ad scripts.
"""

import json
import re
import os
from typing import List, Dict, Any, Tuple, Optional
from src.config import Config
from src.scraping import scrape_subreddit
from src.utils.json_utils import extract_json_from_llm_response
from collections import Counter

def generate_tts_script(ad_script):
    """
    Convert a formatted ad script into a clean text-to-speech version.
    Handles multiple platform formats (YouTube, Instagram, TikTok, etc.)
    
    Args:
        ad_script (str): The original formatted ad script
        
    Returns:
        str: A clean script suitable for text-to-speech platforms like ElevenLabs
    """
    # Remove scene descriptions in square brackets (all platforms)
    cleaned_script = re.sub(r'\[.*?\]', '', ad_script)
    
    # Remove formatting indicators for all platforms
    cleaned_script = re.sub(r'\*.*?\*', '', cleaned_script)  # Asterisk formatting
    cleaned_script = re.sub(r'_.*?_', '', cleaned_script)    # Underscore formatting
    
    # Remove actor/role prefixes and dialogue indicators
    cleaned_script = re.sub(r'[A-Za-z]+\s*\([^)]*\):', '', cleaned_script)  # Character with description
    cleaned_script = re.sub(r'[A-Za-z]+\s*\(.*?\):', '', cleaned_script)    # Alternative format
    cleaned_script = re.sub(r'[A-Za-z]+:', '', cleaned_script)              # Simple character prefix
    
    # Handle YouTube/Video-specific formatting
    cleaned_script = re.sub(r'---+', ' ', cleaned_script)                  # Section dividers
    cleaned_script = re.sub(r'\*\*\[.*?\]\*\*', '', cleaned_script)        # Bold timestamps
    cleaned_script = re.sub(r'\*\*.*?\*\*', '', cleaned_script)            # Bold section headers
    cleaned_script = re.sub(r'Visual:.*?(\n|$)', '', cleaned_script)       # Visual descriptions
    cleaned_script = re.sub(r'SCENE \d+:.*?(\n|$)', '', cleaned_script)    # Scene headers
    cleaned_script = re.sub(r'\[SCENE \d+\].*?(\n|$)', '', cleaned_script) # Alternative scene format
    
    # Handle TikTok-specific formatting
    cleaned_script = re.sub(r'\[VISUAL\]:.*?(\n|$)', '', cleaned_script)   # Visual directions
    cleaned_script = re.sub(r'\[TEXT\]:.*?(\n|$)', '', cleaned_script)     # On-screen text
    cleaned_script = re.sub(r'\[AUDIO\]:', '', cleaned_script)             # Audio directions but keep content
    
    # Handle Instagram-specific formatting
    cleaned_script = re.sub(r'#\w+', '', cleaned_script)                   # Remove hashtags
    cleaned_script = re.sub(r'@\w+', '', cleaned_script)                   # Remove mentions
    
    # Handle Facebook-specific formatting
    cleaned_script = re.sub(r'Headline:.*?(\n|$)', '', cleaned_script)     # Headline indicator
    cleaned_script = re.sub(r'Main Copy:', '', cleaned_script)             # Main copy indicator but keep content
    cleaned_script = re.sub(r'CTA:', '', cleaned_script)                   # CTA indicator but keep content
    
    # Remove quotes around dialogue for all platforms
    cleaned_script = cleaned_script.replace('"', '')
    cleaned_script = cleaned_script.replace('"', '')
    cleaned_script = cleaned_script.replace('"', '')
    
    # Remove any remaining special formatting characters
    cleaned_script = cleaned_script.replace('*', '')
    cleaned_script = cleaned_script.replace('(V.O.)', '')
    cleaned_script = cleaned_script.replace('VOICEOVER:', '')
    cleaned_script = cleaned_script.replace('ON-SCREEN TEXT:', '')
    
    # Remove empty lines
    cleaned_script = re.sub(r'\n\s*\n', '\n', cleaned_script)
    
    # Remove extra whitespace and normalize spacing
    cleaned_script = re.sub(r'\s+', ' ', cleaned_script)
    
    # Clean up multiple periods and ensure proper spacing
    cleaned_script = re.sub(r'\.+', '.', cleaned_script)
    cleaned_script = re.sub(r'\.\s*\.', '.', cleaned_script)
    
    # Final cleanup - remove any markdown formatting that might remain
    cleaned_script = re.sub(r'\*+', '', cleaned_script)
    cleaned_script = re.sub(r'_+', '', cleaned_script)
    
    # Remove starting and ending indicators
    cleaned_script = re.sub(r'End of Ad', '', cleaned_script)
    cleaned_script = re.sub(r'End of Script', '', cleaned_script)
    
    return cleaned_script.strip()
class BaseAgent:
    """Base class for all agents with common LLM functionality."""
    
    def __init__(self, llm_provider: str = "openai", model_name: Optional[str] = None):
        """
        Initialize the agent with a specific LLM provider and model.
        
        Args:
            llm_provider (str): The LLM provider to use (openai, claude, groq)
            model_name (str, optional): Specific model name. If None, uses defaults.
        """
        self.llm_provider = llm_provider
        
        # Set default model names based on provider if not specified
        if not model_name:
            if llm_provider == "openai":
                self.model_name = "gpt-4o"
            elif llm_provider == "claude":
                self.model_name = "claude-3-5-sonnet-20240620"
            elif llm_provider == "groq":
                self.model_name = "deepseek-r1-distill-llama-70b"
            else:
                # Default to OpenAI if provider not recognized
                self.llm_provider = "openai"
                self.model_name = "gpt-4o"
        else:
            self.model_name = model_name
    
    def _clean_llm_response(self, response: str) -> str:
        """
        Clean LLM response by removing thinking process and other artifacts.
        
        Args:
            response (str): Raw LLM response
            
        Returns:
            str: Cleaned response
        """
        # If response is None or empty, return empty string
        if not response:
            return ""
        
        # Remove thinking process enclosed in <think> tags (for models like Deepseek)
        cleaned = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        
        # Sometimes the model includes the word "think" without proper tags
        cleaned = re.sub(r'<think.*?>', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'</think.*?>', '', cleaned, flags=re.DOTALL)
        
        # Remove any remaining tags that might cause issues
        cleaned = re.sub(r'<.*?>', '', cleaned, flags=re.DOTALL)
        
        # Clean up markdown code blocks that might interfere with parsing
        cleaned = re.sub(r'```json(.*?)```', r'\1', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'```(.*?)```', r'\1', cleaned, flags=re.DOTALL)
        
        # Remove any explicit JSON labels that might appear
        cleaned = re.sub(r'JSON response:', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'JSON:', '', cleaned, flags=re.DOTALL)
        
        # Clean up whitespace
        cleaned = cleaned.strip()
        
        return cleaned
    
    def generate_llm_response(self, prompt: str) -> str:
        """
        Generate response using the specified LLM provider and model.
        
        Args:
            prompt (str): The prompt to send to the LLM
            
        Returns:
            str: The generated response
        """
        try:
            if self.llm_provider == "openai":
                from src.generation.openai_generator import generate_ad_script as generate
                response = generate(prompt, model=self.model_name)
            elif self.llm_provider == "claude":
                from src.generation.claude_generator import generate_ad_script as generate
                response = generate(prompt, model=self.model_name)
            elif self.llm_provider == "groq":
                from src.generation.groq_generator import generate_ad_script as generate
                response = generate(prompt, model=self.model_name)
            else:
                # Default to OpenAI if provider not recognized
                from src.generation.openai_generator import generate_ad_script as generate
                response = generate(prompt, model="gpt-4o")
                
            # Clean the response before returning
            return self._clean_llm_response(response)
            
        except Exception as e:
            print(f"Error with {self.llm_provider} ({self.model_name}): {str(e)}")
            print("Falling back to OpenAI...")
            try:
                from src.generation.openai_generator import generate_ad_script as generate
                response = generate(prompt, model="gpt-4o")
                return self._clean_llm_response(response)
            except Exception as fallback_error:
                print(f"Fallback also failed: {str(fallback_error)}")
                return f"Error generating response: {str(e)}"
            

class ResearchAgent(BaseAgent):
    """Agent responsible for finding relevant subreddits and search queries."""
    
    def find_relevant_subreddits(self, product_info: Dict[str, str]) -> List[str]:
        """Find most relevant subreddits for a given product."""
        prompt = f"""
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
        
        Do not include any thinking, reasoning, or explanation in your response. Just provide the list.
        """
        
        # Call LLM using the unified method - response is already cleaned
        response = self.generate_llm_response(prompt)
        
        # Parse response and clean up
        subreddits = [s.strip().lower() for s in response.split(',')]
        subreddits = [s.replace('r/', '') for s in subreddits]  # Remove r/ if present
        
        # Filter out empty or invalid subreddit names
        subreddits = [s for s in subreddits if s and len(s) > 2 and not s.startswith('<') and not s.endswith('>')]
        
        # Ensure we have at least some default subreddits if parsing failed
        if not subreddits:
            print("Warning: Failed to parse subreddits from LLM response. Generating defaults from product info.")
            
            # Extract niche and keywords
            niche = product_info.get('niche', '').lower()
            keywords = product_info.get('keywords', '').lower()
            
            # Generate potential subreddits based on niche and keywords
            potential_subreddits = []
            
            # Add niche-based subreddits
            if niche:
                niche_terms = [term.strip() for term in niche.split(',')]
                potential_subreddits.extend(niche_terms)
            
            # Add keyword-based subreddits
            if keywords:
                keyword_terms = [term.strip() for term in keywords.split(',')]
                potential_subreddits.extend(keyword_terms)
            
            # Add target audience based subreddits
            audience = product_info.get('target_audience', '').lower()
            audience_terms = []
            if "professionals" in audience or "workers" in audience:
                audience_terms.append("careers")
            if "students" in audience:
                audience_terms.append("college")
            if "parents" in audience:
                audience_terms.append("parenting")
            if "health" in audience:
                audience_terms.append("health")
            
            potential_subreddits.extend(audience_terms)
            
            # Filter and clean potential subreddits
            subreddits = []
            for sub in potential_subreddits:
                # Keep only simple words without spaces or special characters
                if ' ' not in sub and len(sub) > 2 and all(c.isalnum() or c == '_' for c in sub):
                    subreddits.append(sub)
            
            # Add some general popular subreddits if we don't have enough
            if len(subreddits) < 3:
                general_subs = ["askreddit", "advice", "tipofmytongue", "buyitforlife", "frugal"]
                subreddits.extend(general_subs)
            
            # Take only the first 5 unique subreddits
            subreddits = list(dict.fromkeys(subreddits))[:5]
        
        print(f"Found relevant subreddits: {', '.join(subreddits)}")
        return subreddits
    
    def generate_search_queries(self, product_info: Dict[str, str]) -> List[str]:
        """Generate search queries related to the product."""
        prompt = f"""
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
        
        Return ONLY a comma-separated list of search queries without quotes.
        
        Do not include any thinking, reasoning, or explanation in your response. Just provide the list.
        """
        
        # Call LLM using the unified method - response is already cleaned
        response = self.generate_llm_response(prompt)
        
        # Parse response and clean up
        queries = [q.strip() for q in response.split(',')]
        
        # Filter out empty or invalid queries
        queries = [q for q in queries if q and len(q) > 5]
        
        # Remove quotes that might cause issues with search
        queries = [q.replace('"', '') for q in queries]
        
        # Ensure we have at least some default queries if parsing failed
        if not queries:
            print("Warning: Failed to parse queries from LLM response. Generating defaults from product info.")
            
            # Extract key terms from product info
            product_name = product_info.get('product_name', '').lower()
            description = product_info.get('product_description', '').lower()
            use_cases = product_info.get('use_cases', '').lower()
            keywords = product_info.get('keywords', '').lower()
            
            # Extract potential keywords from all available fields
            all_text = f"{product_name} {description} {use_cases} {keywords}"
            potential_terms = [word for word in all_text.split() if len(word) > 4]
            
            # Get the most frequent words that might be relevant
            from collections import Counter
            word_counts = Counter(potential_terms)
            common_terms = [word for word, count in word_counts.most_common(5) if count > 1]
            
            # Use the common terms to build queries
            if common_terms and len(common_terms) >= 2:
                term1 = common_terms[0]
                term2 = common_terms[1]
                queries = [
                    f"{term1} {term2} discussion",
                    f"best {term1} reviews",
                    f"{term2} recommendations",
                    f"{term1} problems solutions",
                    f"{term2} vs competitors"
                ]
            else:
                # If we couldn't extract meaningful terms, use product name
                queries = [
                    f"{product_name} discussion",
                    f"{product_name} reviews",
                    f"{product_name} problems",
                    f"{product_name} alternatives",
                    f"{product_name} recommendations"
                ]
        
        print(f"Generated search queries: {', '.join(queries)}")
        return queries
    

class DataCollectionAgent:
    """Agent responsible for collecting and filtering Reddit data."""
    
    def __init__(self, reddit_client):
        self.reddit_client = reddit_client
    
    def search_subreddit(self, subreddit_name: str, query: str, limit: int = 3, retry_count: int = 2) -> List[Dict[str, Any]]:
        """Search for posts in a subreddit with a specific query, with retries.
        
        Args:
            subreddit_name (str): Name of the subreddit to search
            query (str): Search query
            limit (int): Maximum number of posts to retrieve
            retry_count (int): Number of retry attempts if search fails
            
        Returns:
            List[Dict[str, Any]]: List of post data dictionaries
        """
        # Verify subreddit name is valid
        if not subreddit_name or len(subreddit_name) < 3 or ' ' in subreddit_name or '/' in subreddit_name:
            print(f"Invalid subreddit name: '{subreddit_name}'. Skipping.")
            return []
            
        # Clean the query to remove problematic characters
        clean_query = query.replace('"', '').replace("'", "").strip()
        if len(clean_query) < 3:
            print(f"Query too short after cleaning: '{clean_query}'. Skipping.")
            return []
        
        posts_data = []
        last_error = None
        
        # Try multiple times with increasing backoff
        for attempt in range(retry_count + 1):
            try:
                print(f"Searching r/{subreddit_name} for '{clean_query}'... (Attempt {attempt + 1}/{retry_count + 1})")
                
                # Create a new subreddit object for each attempt to avoid stale connections
                subreddit = self.reddit_client.subreddit(subreddit_name)
                
                # Use a try-except block to handle search failures gracefully
                # Search for posts with specific query
                for post in subreddit.search(clean_query, sort='relevance', limit=limit):
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
                    try:
                        post.comments.replace_more(limit=0)  # Remove comment stubs
                        for comment in post.comments[:3]:  # Limit to top 3 comments per post
                            if comment.body and len(comment.body) > 20:  # Filter out short comments
                                post_data['top_comments'].append({
                                    'body': comment.body,
                                    'score': comment.score
                                })
                    except Exception as comment_error:
                        print(f"Error getting comments for post in r/{subreddit_name}: {str(comment_error)}")
                    
                    posts_data.append(post_data)
                
                # If we got here without errors and have some data, break out of retry loop
                if posts_data:
                    print(f"Successfully found {len(posts_data)} posts in r/{subreddit_name}")
                    break
                else:
                    # No error but also no posts - try again if we have attempts left
                    print(f"No posts found in r/{subreddit_name} for query '{clean_query}'")
                    if attempt < retry_count:
                        # Try a more general search on the next attempt
                        clean_query = self._simplify_query(clean_query)
                        print(f"Simplifying query to '{clean_query}' for next attempt")
                        
            except Exception as e:
                last_error = e
                print(f"Error searching r/{subreddit_name} (Attempt {attempt + 1}): {str(e)}")
                
                # Wait before retrying (increasing backoff)
                if attempt < retry_count:
                    import time
                    wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4, 8...
                    print(f"Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
        
        # If we exhausted all retries and still have no data, log the final error
        if not posts_data and last_error:
            print(f"All attempts failed for r/{subreddit_name}: {str(last_error)}")
        
        return posts_data
    
    def _simplify_query(self, query: str) -> str:
        """Simplify a query that failed to return results to increase chances on retry.
        
        Args:
            query (str): The original query that failed
            
        Returns:
            str: A simplified version of the query
        """
        # Split query into words
        words = query.split()
        
        # If query has multiple words, return only the most important 1-2 words
        if len(words) > 2:
            # Remove common stop words and keep only substantive words
            stop_words = {'the', 'and', 'or', 'but', 'if', 'on', 'in', 'with', 'for', 'to', 'from', 'by', 'at', 'of'}
            filtered_words = [word for word in words if word.lower() not in stop_words]
            
            # If we still have enough words after filtering, take the first 2
            if len(filtered_words) > 1:
                return ' '.join(filtered_words[:2])
            
            # Otherwise take the first 2 original words
            return ' '.join(words[:2])
            
        # If query is already simple, return as is
        return query
    
    def collect_data(self, subreddits: List[str], queries: List[str], posts_per_query: int = 2, 
                    max_failures: int = 3) -> List[Dict[str, Any]]:
        """Collect data from multiple subreddits using multiple queries with failure tracking.
        
        Args:
            subreddits (List[str]): List of subreddit names
            queries (List[str]): List of search queries
            posts_per_query (int): Maximum posts to retrieve per query
            max_failures (int): Maximum number of consecutive subreddit failures before giving up
            
        Returns:
            List[Dict[str, Any]]: List of post data dictionaries
        """
        all_posts = []
        successful_subreddits = 0
        consecutive_failures = 0
        
        # Clean subreddit names
        clean_subreddits = []
        for subreddit in subreddits:
            # Basic validation
            if subreddit and len(subreddit) > 2 and ' ' not in subreddit and not subreddit.startswith('<'):
                clean_subreddits.append(subreddit.strip().lower())
        
        # Ensure we have some subreddits
        if not clean_subreddits:
            print("No valid subreddits provided. Using defaults.")
            clean_subreddits = ["askreddit", "advice", "tipofmytongue", "buyitforlife"]
            
        # Clean queries
        clean_queries = []
        for query in queries:
            if query and len(query) > 3:
                # Remove quotes and extraneous characters that might cause search issues
                clean_query = query.replace('"', '').replace("'", "").strip()
                if clean_query:
                    clean_queries.append(clean_query)
        
        # Ensure we have some queries
        if not clean_queries:
            print("No valid queries provided. Using defaults.")
            clean_queries = ["review", "recommendation", "problem", "alternative"]
        
        # Collect posts from each subreddit using each query
        for subreddit in clean_subreddits:
            # Check if we've had too many consecutive failures
            if consecutive_failures >= max_failures:
                print(f"Too many consecutive subreddit failures ({consecutive_failures}). Stopping search.")
                break
                
            posts_for_subreddit = []
            
            for query in clean_queries:
                try:
                    new_posts = self.search_subreddit(subreddit, query, limit=posts_per_query)
                    posts_for_subreddit.extend(new_posts)
                except Exception as e:
                    print(f"Unexpected error in collect_data for r/{subreddit} with query '{query}': {str(e)}")
            
            if posts_for_subreddit:
                successful_subreddits += 1
                consecutive_failures = 0  # Reset failure counter on success
                all_posts.extend(posts_for_subreddit)
            else:
                consecutive_failures += 1
                print(f"Failed to collect any posts from r/{subreddit}. Consecutive failures: {consecutive_failures}")
        
        # If we have no posts but some subreddits succeeded, we might have had issues with the queries
        if not all_posts and successful_subreddits > 0:
            print("No posts found with specific queries. Trying fallback queries.")
            # Try again with very generic queries for a few subreddits
            fallback_queries = ["recommendation", "review", "advice", "question", "help"]
            fallback_subreddits = clean_subreddits[:3] if len(clean_subreddits) > 2 else clean_subreddits
            
            for subreddit in fallback_subreddits:
                for query in fallback_queries:
                    try:
                        posts = self.search_subreddit(subreddit, query, limit=2)
                        if posts:
                            all_posts.extend(posts)
                            print(f"Fallback query '{query}' succeeded for r/{subreddit}")
                            # If we got some posts, we can stop trying fallback queries
                            if len(all_posts) >= 5:
                                break
                    except Exception:
                        pass
                
                # If we got enough posts from this subreddit, move to the next one
                if len(all_posts) >= 5:
                    break
        
        print(f"Collected {len(all_posts)} posts from {successful_subreddits} subreddits")
        
        # Check if we have enough data
        if len(all_posts) < 2:
            print("WARNING: Very few posts collected. The generated ad may lack audience insights.")
            
        return all_posts    

class AnalysisAgent(BaseAgent):
    """Agent responsible for analyzing and filtering the collected data."""
    
    def filter_posts_by_relevance(self, posts_data: List[Dict[str, Any]], product_info: Dict[str, str],
                                 retry_attempts: int = 2) -> List[Dict[str, Any]]:
        """Filter and rank posts based on relevance to the product with retry logic.
        
        Args:
            posts_data (List[Dict[str, Any]]): List of post data dictionaries
            product_info (Dict[str, str]): Dictionary containing product information
            retry_attempts (int): Number of retry attempts for LLM evaluation
            
        Returns:
            List[Dict[str, Any]]: Filtered list of relevant posts
        """
        if not posts_data:
            print("No posts to filter for relevance.")
            return []
        
        # Create a batch of posts to evaluate (limit to prevent token overflow)
        batch_size = min(10, len(posts_data))
        batch = posts_data[:batch_size]
        
        for attempt in range(retry_attempts + 1):
            try:
                # Prepare the evaluation prompt
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
                
                # Add each post to the prompt
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
                
                # Call LLM to evaluate posts
                response = self.generate_llm_response(prompt)
                
                # Extract JSON from response using the utility function
                evaluations = extract_json_from_llm_response(response, default_value=[])
                
                if evaluations:
                    # Filter posts based on relevance score (threshold = 6)
                    relevant_posts = []
                    for eval_item in evaluations:
                        if eval_item.get("relevance_score", 0) >= 6:
                            post_index = eval_item.get("post_index", -1)
                            if post_index >= 0 and post_index < len(batch):
                                relevant_posts.append(batch[post_index])
                    
                    if relevant_posts:
                        print(f"Filtered to {len(relevant_posts)} relevant posts (threshold score: 6/10)")
                        return relevant_posts
                    else:
                        print("No posts met the relevance threshold.")
                        # If this is the last attempt, use all posts
                        if attempt == retry_attempts:
                            print("Using all posts as no posts met the relevance threshold after all attempts.")
                            return batch
                        else:
                            # Try again with a lower threshold on subsequent attempts
                            print(f"Retrying with modified approach (attempt {attempt + 2}/{retry_attempts + 1})")
                else:
                    print(f"Failed to extract evaluations from LLM response (attempt {attempt + 1})")
                    # If this is the last attempt, use all posts
                    if attempt == retry_attempts:
                        print("Using all posts as fallback after failed evaluations.")
                        return batch
            
            except Exception as e:
                print(f"Error during relevance filtering (attempt {attempt + 1}): {str(e)}")
                # If this is the last attempt, use all posts
                if attempt == retry_attempts:
                    print("Using all posts as fallback after error.")
                    return batch
        
        # Fallback to returning all posts if all attempts failed
        return batch
    
    def extract_key_insights(self, posts_data: List[Dict[str, Any]], product_info: Dict[str, str],
                            retry_attempts: int = 2) -> Dict[str, Any]:
        """Extract key insights from the relevant posts with retry logic.
        
        Args:
            posts_data (List[Dict[str, Any]]): List of post data dictionaries
            product_info (Dict[str, str]): Dictionary containing product information
            retry_attempts (int): Number of retry attempts for LLM analysis
            
        Returns:
            Dict[str, Any]: Dictionary with extracted insights
        """
        # Default insights in case of failure
        default_insights = {
            "pain_points": self._generate_default_pain_points(product_info),
            "language": self._generate_default_language(product_info),
            "topics": self._generate_default_topics(product_info),
            "insights": f"No reliable insights could be extracted from Reddit data. The ad should focus on the core value proposition of {product_info['product_name']} for {product_info['target_audience']}."
        }
        
        if not posts_data:
            print("No posts to analyze for insights.")
            return default_insights
        
        for attempt in range(retry_attempts + 1):
            try:
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
                
                # Add posts to the prompt (with a reasonable limit)
                post_limit = min(5, len(posts_data))
                for i, post in enumerate(posts_data[:post_limit]):
                    prompt += f"\nPost {i+1}:\nTitle: {post['title']}\n"
                    content = post['selftext'][:300] + "..." if len(post['selftext']) > 300 else post['selftext']
                    prompt += f"Content: {content}\n"
                    
                    # Add a sample of comments
                    if post['top_comments']:
                        prompt += "Top Comments:\n"
                        for j, comment in enumerate(post['top_comments'][:2]):
                            comment_text = comment['body'][:150] + "..." if len(comment['body']) > 150 else comment['body']
                            prompt += f"- Comment {j+1}: {comment_text}\n"
                
                # Call LLM to analyze posts
                response = self.generate_llm_response(prompt)
                
                # Extract JSON using the utility function
                insights = extract_json_from_llm_response(response, default_value=None)
                
                if insights:
                    # Validate insights structure
                    required_keys = ["pain_points", "language", "topics", "insights"]
                    missing_keys = [key for key in required_keys if key not in insights]
                    
                    if not missing_keys:
                        # Ensure all lists have content
                        list_keys = ["pain_points", "language", "topics"]
                        valid_lists = all(isinstance(insights.get(key, None), list) and len(insights.get(key, [])) > 0 for key in list_keys)
                        
                        if valid_lists and insights.get("insights"):
                            print("Successfully extracted insights from posts.")
                            return insights
                        else:
                            print(f"Extracted insights have empty lists (attempt {attempt + 1}).")
                    else:
                        print(f"Extracted insights missing keys: {missing_keys} (attempt {attempt + 1}).")
                else:
                    print(f"Failed to extract valid insights JSON (attempt {attempt + 1}).")
                
                # If this is the last attempt, use default insights
                if attempt == retry_attempts:
                    print("Using default insights after all extraction attempts failed.")
                    return default_insights
                    
            except Exception as e:
                print(f"Error during insights extraction (attempt {attempt + 1}): {str(e)}")
                # If this is the last attempt, use default insights
                if attempt == retry_attempts:
                    print("Using default insights after error.")
                    return default_insights
        
        # Fallback to default insights if all attempts failed
        return default_insights
        
    def synthesize_insights_without_data(self, product_info: Dict[str, str], retry_attempts: int = 2) -> Dict[str, Any]:
        """Generate insights directly from product information when no Reddit data is available.
        
        Args:
            product_info (Dict[str, str]): Dictionary containing product information
            retry_attempts (int): Number of retry attempts for LLM synthesis
            
        Returns:
            Dict[str, Any]: Dictionary with synthesized insights
        """
        # Default insights in case all attempts fail
        default_insights = {
            "pain_points": self._generate_default_pain_points(product_info),
            "language": self._generate_default_language(product_info),
            "topics": self._generate_default_topics(product_info),
            "insights": f"Without access to specific user data, we can infer that {product_info['target_audience']} likely experience issues that {product_info['product_name']} can solve. The marketing campaign should focus on highlighting how the product addresses these pain points while using terminology familiar to the audience."
        }
        
        for attempt in range(retry_attempts + 1):
            try:
                prompt = f"""
                You need to create insights for an ad campaign without Reddit data.
                
                Based on the product information below, create a comprehensive set of insights that would help in creating a compelling ad script.
                
                PRODUCT INFORMATION:
                Name: {product_info['product_name']}
                Description: {product_info['product_description']}
                Target Audience: {product_info['target_audience']}
                Use Cases: {product_info.get('use_cases', 'Not specified')}
                Niche: {product_info.get('niche', 'Not specified')}
                Keywords: {product_info.get('keywords', 'Not specified')}
                Campaign Goal: {product_info['campaign_goal']}
                
                Generate the following:
                1. A list of likely pain points the target audience experiences
                2. Common phrases and language the target audience might use
                3. Current trending topics relevant to this product
                4. Overall insights that would be valuable for creating an ad
                
                Format your response as a JSON object with the following structure:
                {{
                    "pain_points": [list of 3-5 specific pain points],
                    "language": [list of 5-7 phrases, terms, or expressions used by the audience],
                    "topics": [list of 3-5 trending topics],
                    "insights": "A paragraph summarizing key insights for ad creation"
                }}
                """
                
                # Call LLM to generate insights
                response = self.generate_llm_response(prompt)
                
                # Extract JSON from the response
                insights = extract_json_from_llm_response(response, default_value=None)
                
                if insights:
                    # Validate insights structure
                    required_keys = ["pain_points", "language", "topics", "insights"]
                    missing_keys = [key for key in required_keys if key not in insights]
                    
                    if not missing_keys:
                        # Ensure all lists have content
                        list_keys = ["pain_points", "language", "topics"]
                        valid_lists = all(isinstance(insights.get(key, None), list) and len(insights.get(key, [])) > 0 for key in list_keys)
                        
                        if valid_lists and insights.get("insights"):
                            print("Successfully synthesized insights from product information.")
                            return insights
                        else:
                            print(f"Synthesized insights have empty lists (attempt {attempt + 1}).")
                    else:
                        print(f"Synthesized insights missing keys: {missing_keys} (attempt {attempt + 1}).")
                else:
                    print(f"Failed to extract valid insights JSON (attempt {attempt + 1}).")
                
                # If this is the last attempt, use default insights
                if attempt == retry_attempts:
                    print("Using default insights after all synthesis attempts failed.")
                    return default_insights
                    
            except Exception as e:
                print(f"Error during insights synthesis (attempt {attempt + 1}): {str(e)}")
                # If this is the last attempt, use default insights
                if attempt == retry_attempts:
                    print("Using default insights after error.")
                    return default_insights
        
        # Fallback to default insights if all attempts failed
        return default_insights

    def _generate_default_pain_points(self, product_info: Dict[str, str]) -> List[str]:
        """Generate default pain points based on product information."""
        # Extract key information
        use_cases = product_info.get('use_cases', '')
        description = product_info.get('product_description', '')
        
        # Generate pain points based on use cases
        pain_points = []
        
        # Parse use cases if available
        if use_cases:
            for use_case in use_cases.split(','):
                use_case = use_case.strip().lower()
                # Generate a pain point from each use case
                if "pain" in use_case:
                    pain_points.append(f"Chronic or recurring {use_case}")
                elif "quality" in use_case:
                    pain_points.append(f"Poor or inconsistent {use_case}")
                elif "improve" in use_case:
                    aspect = use_case.replace("improving", "").replace("improve", "").strip()
                    pain_points.append(f"Dissatisfaction with current {aspect} solutions")
                else:
                    pain_points.append(f"Frustration with inadequate {use_case} options")
        
        # If we couldn't generate from use cases, try from description
        if not pain_points and description:
            # Look for keywords indicating problems the product solves
            problem_indicators = ["solve", "problem", "challenge", "improve", "enhance", "prevent", "reduce"]
            for indicator in problem_indicators:
                if indicator in description.lower():
                    # Get the context around the indicator
                    parts = description.lower().split(indicator)
                    if len(parts) > 1:
                        context = parts[1].strip().split('.')[0]
                        pain_points.append(f"Difficulty with {context}")
        
        # Add some generic pain points if we still don't have enough
        if len(pain_points) < 3:
            generic_pain_points = [
                f"Frustration with current {product_info['product_name']} alternatives",
                f"Dissatisfaction with the quality of existing solutions",
                f"Feeling overwhelmed by too many complex options",
                "Wasting time and money on ineffective products",
                "Stress from dealing with persistent problems"
            ]
            pain_points.extend(generic_pain_points)
        
        # Return unique pain points, limited to 5
        return list(dict.fromkeys(pain_points))[:5]

    def _generate_default_language(self, product_info: Dict[str, str]) -> List[str]:
        """Generate default audience language based on product information."""
        # Extract relevant information
        keywords = product_info.get('keywords', '').split(',')
        target_audience = product_info.get('target_audience', '')
        niche = product_info.get('niche', '')
        
        # Combine all potential language sources
        language_sources = []
        language_sources.extend([k.strip() for k in keywords if k.strip()])
        
        # Extract potential phrases from target audience description
        if target_audience:
            # Look for specific demographic indicators
            if "professional" in target_audience.lower():
                language_sources.extend(["ROI", "efficiency", "performance", "productivity"])
            if "parent" in target_audience.lower():
                language_sources.extend(["family-friendly", "time-saving", "child-safe", "peace of mind"])
            if "health" in target_audience.lower():
                language_sources.extend(["wellness", "self-care", "healthy lifestyle", "well-being"])
            if "tech" in target_audience.lower():
                language_sources.extend(["innovative", "cutting-edge", "state-of-the-art", "seamless"])
        
        # Add niche-specific language
        if niche:
            niche_terms = [term.strip() for term in niche.split(',')]
            language_sources.extend(niche_terms)
        
        # Add some generic but effective marketing language
        generic_language = [
            "game-changer",
            "life-changing",
            "revolutionary",
            "must-have",
            "essential",
            "breakthrough",
            "hassle-free"
        ]
        
        # Combine all sources and return unique terms, limited to 7
        all_language = language_sources + generic_language
        return list(dict.fromkeys([term for term in all_language if term]))[:7]

    def _generate_default_topics(self, product_info: Dict[str, str]) -> List[str]:
        """Generate default trending topics based on product information."""
        # Extract relevant information
        niche = product_info.get('niche', '')
        keywords = product_info.get('keywords', '')
        
        # Generate topics based on niche and keywords
        topics = []
        
        if niche:
            niche_terms = [term.strip() for term in niche.split(',')]
            topics.extend([f"{term} innovation" for term in niche_terms if term])
        
        if keywords:
            keyword_terms = [term.strip() for term in keywords.split(',')]
            topics.extend([f"Advancements in {term}" for term in keyword_terms if term])
        
        # Add some generic trending topics that can apply to most products
        generic_topics = [
            "Sustainable and eco-friendly alternatives",
            "Digital transformation in daily life",
            "Health and wellness optimization",
            "Work-life balance improvements",
            "Smart technology integration"
        ]
        
        # Combine all topics and return unique ones, limited to 5
        all_topics = topics + generic_topics
        return list(dict.fromkeys(all_topics))[:5]
class CopywritingAgent(BaseAgent):
    """Agent responsible for creating the ad script."""
    
    def generate_ad_script(self, insights: Dict[str, Any], product_info: Dict[str, str], platform: str = "general") -> str:
        """
        Generate an ad script based on the analysis insights.
        
        Args:
            insights (Dict[str, Any]): Dictionary with insights from analysis
            product_info (Dict[str, str]): Dictionary with product information
            platform (str): Target platform for the ad script (general, instagram, youtube, video, tiktok, facebook)
            
        Returns:
            str: Generated ad script
        """
        # Base prompt with product information and insights
        base_prompt = f"""
        You are an expert copywriter creating a viral ad script.
        
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
        """
        
        # Platform-specific instructions
        platform_instructions = {
            "general": """
            Create a compelling ad script that:
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
            """,
            
            "instagram": """
            Create an Instagram ad script that:
            1. Is visually descriptive and engaging
            2. Uses concise, impactful language
            3. Incorporates relevant hashtags
            4. Is optimized for mobile viewing
            5. Has a strong CTA that works with Instagram's format
            
            Your Instagram ad should be 100-150 words max and include:
            - An attention-grabbing first line that works even when truncated
            - Short, punchy sentences that maintain interest
            - Visual descriptions that would pair well with imagery
            - 3-5 relevant hashtags
            - A clear call-to-action that directs to link in bio or swipe up
            """,
            
            "youtube": """
            Create a YouTube video ad script that:
            1. Hooks viewers in the first 5 seconds
            2. Maintains engagement throughout
            3. Incorporates both visual and audio elements
            4. Builds a narrative around the product
            5. Ends with a compelling call-to-action
            
            Format your script with timing, visual descriptions, and dialogue:
            [0:00-0:05] - Opening hook
            [0:05-0:15] - Problem statement
            [0:15-0:30] - Product introduction
            [0:30-0:45] - Features and benefits
            [0:45-0:60] - Testimonial or demonstration
            [0:60-0:75] - Call-to-action
            
            Include both visual directions and spoken dialogue in your script, keeping total length to 60-90 seconds.
            """,
            
            "video": """
            Create a video ad script that:
            1. Captures attention in the first 3 seconds
            2. Tells a compelling visual story
            3. Demonstrates the product solving a problem
            4. Uses both on-screen text and dialogue/voiceover
            5. Ends with a clear call-to-action
            
            Format your script with:
            [SCENE 1] - Description of visuals and setting
            VOICEOVER: "Dialogue here"
            ON-SCREEN TEXT: "Text here"
            
            [SCENE 2] - Description of visuals and setting
            VOICEOVER: "Dialogue here"
            ON-SCREEN TEXT: "Text here"
            
            Keep the script to 30-60 seconds total (3-5 scenes).
            """,
            
            "tiktok": """
            Create a TikTok ad script that:
            1. Is extremely concise and attention-grabbing
            2. Uses trendy language and references
            3. Feels authentic and native to TikTok
            4. Can incorporate popular TikTok formats (challenges, before/after, etc.)
            5. Is under 30 seconds when read aloud
            
            Format your script with:
            [VISUAL]: Brief description of what's shown
            [TEXT]: On-screen text
            [AUDIO]: Voice or sound description
            
            Keep the entire script to 15-30 seconds maximum. The language should be casual, authentic, and speak directly to TikTok users.
            """,
            
            "facebook": """
            Create a Facebook ad script that:
            1. Works well in the feed format
            2. Engages users with questions or relatable statements
            3. Clearly communicates benefits and value proposition
            4. Includes social proof or testimonial elements
            5. Has a clear call-to-action that aligns with Facebook's CTA buttons
            
            Your Facebook ad should be structured as:
            - Headline (attention-grabbing, 5-7 words)
            - Main ad copy (150-200 words)
            - Call-to-action (aligned with Facebook options like "Learn More", "Shop Now", etc.)
            
            Focus on creating a conversational tone that encourages engagement and sharing.
            """
        }
        
        # Use general instructions if platform not found
        if platform not in platform_instructions:
            platform = "general"
            
        # Combine base prompt with platform-specific instructions
        prompt = f"{base_prompt}\n{platform_instructions[platform]}\n\nAD SCRIPT:"
        
        # Use the standard generate_llm_response method
        ad_script = self.generate_llm_response(prompt)
                
        return ad_script


class ReviewAgent(BaseAgent):
    """Agent responsible for reviewing and refining the ad script."""
    
    def review_ad_script(self, ad_script: str, product_info: Dict[str, str], 
                         insights: Dict[str, Any], platform: str = "general") -> Dict[str, Any]:
        """
        Review the ad script and provide feedback.
        
        Args:
            ad_script (str): The ad script to review
            product_info (Dict[str, str]): Dictionary with product information
            insights (Dict[str, Any]): Dictionary with insights from analysis
            platform (str): Target platform for the ad (general, instagram, youtube, video, tiktok, facebook)
            
        Returns:
            Dict[str, Any]: Dictionary with review feedback and improved script
        """
        # Base evaluation criteria
        base_prompt = f"""
        Review this {platform} ad script for {product_info['product_name']} and evaluate it based on:
        
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
        """
        
        # Platform-specific evaluation criteria
        platform_criteria = {
            "general": """
            Additional evaluation criteria:
            - Does the ad have a clear structure with an opening, problem, solution, benefits, and CTA?
            - Is the ad concise yet comprehensive (150-200 words)?
            - Does it effectively communicate the product's value proposition?
            """,
            
            "instagram": """
            Additional evaluation criteria for Instagram:
            - Is the ad visually descriptive, helping users imagine the imagery?
            - Is it concise enough for Instagram (100-150 words)?
            - Does it include relevant hashtags?
            - Is the CTA appropriate for Instagram's format?
            - Would the opening line work well when truncated in feeds?
            """,
            
            "youtube": """
            Additional evaluation criteria for YouTube:
            - Does the script include proper timing indications [0:00-0:05]?
            - Does it hook viewers in the first 5 seconds?
            - Is there a clear narrative structure?
            - Does it include both visual direction and dialogue/voiceover?
            - Is the length appropriate (60-90 seconds)?
            - Does the CTA work for a video format?
            """,
            
            "video": """
            Additional evaluation criteria for video:
            - Is the script formatted correctly with scenes and visual descriptions?
            - Does it capture attention in the first 3 seconds?
            - Is there a clear visual story being told?
            - Are both visuals and dialogue/voiceover included?
            - Is the length appropriate (30-60 seconds)?
            """,
            
            "tiktok": """
            Additional evaluation criteria for TikTok:
            - Is the ad extremely concise (15-30 seconds when read)?
            - Does it use authentic, trendy language appropriate for TikTok?
            - Is it formatted with visual, text, and audio directions?
            - Does it feel native to the TikTok platform?
            - Would it be engaging enough for the TikTok audience?
            """,
            
            "facebook": """
            Additional evaluation criteria for Facebook:
            - Does it include a compelling headline?
            - Is the main copy engaging and appropriate length for Facebook?
            - Does it encourage engagement (comments, shares)?
            - Is there an element of social proof?
            - Does the CTA align with Facebook's button options?
            """
        }
        
        # Use general criteria if platform not found
        if platform not in platform_criteria:
            platform = "general"
            
        # Final prompt compilation
        prompt = f"""
        {base_prompt}
        
        {platform_criteria[platform]}
        
        AD SCRIPT:
        {ad_script}
        
        Provide a JSON response with:
        {{
            "score": <1-10 overall score>,
            "strengths": [list of 2-3 strengths],
            "weaknesses": [list of 2-3 areas for improvement],
            "suggestions": [list of 2-3 specific suggestions],
            "platform_specific_feedback": "Feedback specific to the {platform} platform",
            "improved_script": "An improved version of the script incorporating your suggestions"
        }}
        """
        
        # Call LLM to review the ad script - response is already cleaned
        response = self.generate_llm_response(prompt)
        
        # Extract JSON using the utility function
        review = extract_json_from_llm_response(response, default_value={
            "score": 7,
            "strengths": ["Generally on target"],
            "weaknesses": ["Could be more specific"],
            "suggestions": ["Review original script"],
            "platform_specific_feedback": f"Consider optimizing further for {platform} format",
            "improved_script": ad_script
        })
        
        # If no improved script is provided, use the original
        if "improved_script" not in review or not review["improved_script"]:
            review["improved_script"] = ad_script
            
        # Add platform information
        review["platform"] = platform
            
        return review

class AdGeneratorOrchestrator:
    """Main orchestrator for the multi-agent ad generation process."""
    
    def __init__(self, reddit_client, llm_provider: str = "openai", model_name: Optional[str] = None, debug: bool = False):
        """
        Initialize the orchestrator with Reddit client and LLM settings.
        
        Args:
            reddit_client: Initialized Reddit client
            llm_provider (str): The LLM provider to use across all agents (openai, claude, groq)
            model_name (str, optional): Specific model name to use. If None, uses defaults.
            debug (bool): Whether to print additional debug information
        """
        self.reddit_client = reddit_client
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.debug = debug
        
        print(f"Initializing multi-agent system with {llm_provider}" + 
              (f" ({model_name})" if model_name else ""))
              
        # Initialize all agents with the same LLM provider and model
        self.research_agent = ResearchAgent(llm_provider=llm_provider, model_name=model_name)
        self.data_collection_agent = DataCollectionAgent(reddit_client)
        self.analysis_agent = AnalysisAgent(llm_provider=llm_provider, model_name=model_name)
        self.copywriting_agent = CopywritingAgent(llm_provider=llm_provider, model_name=model_name)
        self.review_agent = ReviewAgent(llm_provider=llm_provider, model_name=model_name)
    
    def generate_ad(self, product_info: Dict[str, str], save_intermediates: bool = False, 
                    skip_reddit: bool = False, platform: str = "general", generate_runbook: bool = True,
                    max_retries: int = 3) -> Dict[str, Any]:
        """Generate an ad script using the multi-agent approach.
        
        Args:
            product_info (Dict[str, str]): Dictionary with product information
            save_intermediates (bool): Whether to save intermediate results to files
            skip_reddit (bool): Whether to skip Reddit scraping and rely only on LLM
            platform (str): Target platform for the ad (general, instagram, youtube, video, tiktok, facebook, all)
            generate_runbook (bool): Whether to generate a production and upload runbook
            max_retries (int): Maximum number of retry attempts for each stage
            
        Returns:
            Dict[str, Any]: Dictionary with results from each stage and final ad script
        """
        # Check if the user wants to generate ads for all platforms
        if platform.lower() == "all":
            return self.generate_ads_for_all_platforms(
                product_info=product_info,
                save_intermediates=save_intermediates,
                skip_reddit=skip_reddit,
                generate_runbook=generate_runbook,
                max_retries=max_retries
            )
        
        # Original implementation for a single platform
        results = {
            "product_info": product_info,
            "stages": {},
            "configuration": {
                "llm_provider": self.llm_provider,
                "model_name": self.model_name,
                "skip_reddit": skip_reddit,
                "platform": platform
            }
        }
        
        # Stage 1: Research
        print(f"\n=== Stage 1: Research ({self.llm_provider}) ===")
        research_success = False
        subreddits = []
        queries = []
        
        for attempt in range(max_retries):
            try:
                subreddits = self.research_agent.find_relevant_subreddits(product_info)
                queries = self.research_agent.generate_search_queries(product_info)
                
                # Validate the results
                if not subreddits or not queries:
                    raise ValueError("Failed to generate valid subreddits or queries")
                    
                research_success = True
                break
            except Exception as e:
                print(f"Research attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    print("All research attempts failed. Using default values.")
                    # Use reasonable defaults if all attempts fail
                    subreddits = ["productivity", "askreddit", "advice", "selfimprovement", "technology"]
                    queries = [f"{product_info['product_name']} alternatives", "productivity tips", 
                            "focus problems", "work efficiency", "distraction management"]
        
        results["stages"]["research"] = {
            "subreddits": subreddits,
            "queries": queries,
            "success": research_success
        }
        
        if save_intermediates:
            with open(f"stage1_research_{platform}.json", "w", encoding="utf-8") as f:
                json.dump(results["stages"]["research"], f, indent=2)
        
        # Stage 2: Data Collection (if not skipping Reddit)
        posts_data = []
        data_collection_success = False
        
        if not skip_reddit:
            print("\n=== Stage 2: Data Collection ===")
            for attempt in range(max_retries):
                try:
                    posts_data = self.data_collection_agent.collect_data(subreddits, queries)
                    
                    # Check if we actually got any useful data
                    if not posts_data:
                        raise ValueError("No posts were retrieved from Reddit")
                    
                    data_collection_success = True
                    break
                except Exception as e:
                    print(f"Data collection attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        print("All data collection attempts failed. Proceeding without Reddit data.")
            
            results["stages"]["data_collection"] = {
                "posts_count": len(posts_data),
                "success": data_collection_success
            }
            
            if save_intermediates and posts_data:
                with open(f"stage2_raw_data_{platform}.json", "w", encoding="utf-8") as f:
                    json.dump(posts_data, f, indent=2, ensure_ascii=False)
        else:
            print("\n=== Stage 2: Data Collection (SKIPPED) ===")
            results["stages"]["data_collection"] = {
                "posts_count": 0,
                "skipped": True,
                "success": True  # Marking as successful since it was intentionally skipped
            }
        
        # Stage 3: Analysis
        print(f"\n=== Stage 3: Analysis ({self.llm_provider}) ===")
        analysis_success = False
        insights = {}
        
        for attempt in range(max_retries):
            try:
                # If we have posts, analyze them; otherwise, synthesize insights directly
                if posts_data:
                    relevant_posts = self.analysis_agent.filter_posts_by_relevance(posts_data, product_info)
                    insights = self.analysis_agent.extract_key_insights(relevant_posts, product_info)
                else:
                    # No Reddit data, so generate insights directly from product info
                    print("No Reddit data available. Generating insights directly...")
                    insights = self.analysis_agent.synthesize_insights_without_data(product_info)
                
                # Validate that we have required keys in the insights
                required_keys = ["pain_points", "language", "topics", "insights"]
                if not all(key in insights for key in required_keys):
                    raise ValueError(f"Missing required keys in insights: {[k for k in required_keys if k not in insights]}")
                
                analysis_success = True
                break
            except Exception as e:
                print(f"Analysis attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    print("All analysis attempts failed. Using default insights.")
                    # Generate very basic insights as fallback
                    insights = {
                        "pain_points": ["Difficulty staying focused", "Time management challenges", "Distractions", "Task overload", "Burnout"],
                        "language": ["productivity", "focus", "distraction-free", "time management", "deep work", "flow state", "efficiency"],
                        "topics": ["Remote work productivity", "Digital wellness", "Task management", "Focus techniques", "Work-life balance"],
                        "insights": f"The target audience for {product_info['product_name']} struggles with maintaining focus and managing time effectively in distracting environments. They value tools that help them achieve more in less time and create sustainable work habits."
                    }
        
        results["stages"]["analysis"] = insights
        results["stages"]["analysis"]["success"] = analysis_success
        
        if save_intermediates:
            with open(f"stage3_analysis_{platform}.json", "w", encoding="utf-8") as f:
                json.dump(insights, f, indent=2)
        
        # Stage 4: Copywriting
        print(f"\n=== Stage 4: Copywriting ({self.llm_provider}) for {platform.capitalize()} ===")
        copywriting_success = False
        ad_script = ""
        
        for attempt in range(max_retries):
            try:
                ad_script = self.copywriting_agent.generate_ad_script(insights, product_info, platform=platform)
                
                # Validate that we actually got a script
                if not ad_script or len(ad_script.strip()) < 50:
                    raise ValueError("Generated ad script is too short or empty")
                    
                copywriting_success = True
                break
            except Exception as e:
                print(f"Copywriting attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    print("All copywriting attempts failed. Using default ad script.")
                    # Generate a basic ad script as fallback
                    ad_script = f"""Tired of constant distractions?

    Introducing {product_info['product_name']} - the productivity app designed to help you focus on what matters most.

    Our AI-powered system:
    • Blocks distractions before they happen
    • Tracks your productivity patterns
    • Sends gentle reminders to keep you on track
    • Helps you build better work habits over time

    {product_info['target_audience'].split(',')[0]} are already seeing 40% more productivity.

    Try {product_info['product_name']} free for 14 days. Download now and reclaim your focus!"""
        
        results["stages"]["copywriting"] = {
            "original_script": ad_script,
            "platform": platform,
            "success": copywriting_success
        }
        
        if save_intermediates:
            with open(f"stage4_original_script_{platform}.txt", "w", encoding="utf-8") as f:
                f.write(ad_script)
        
        # Stage 5: Review
        print(f"\n=== Stage 5: Review ({self.llm_provider}) ===")
        review_success = False
        review = {}
        
        for attempt in range(max_retries):
            try:
                review = self.review_agent.review_ad_script(ad_script, product_info, insights, platform=platform)
                
                # Validate the review contains an improved script
                if "improved_script" not in review or not review["improved_script"]:
                    raise ValueError("Review did not contain an improved script")
                    
                review_success = True
                break
            except Exception as e:
                print(f"Review attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    print("All review attempts failed. Using original script without review.")
                    # Create a basic review as fallback
                    review = {
                        "score": 7,
                        "strengths": ["Addresses target audience needs", "Clear value proposition"],
                        "weaknesses": ["Could be more specific", "Generic call-to-action"],
                        "suggestions": ["Add more specific benefits", "Strengthen call-to-action"],
                        "platform_specific_feedback": f"Consider optimizing further for {platform} format",
                        "improved_script": ad_script  # Use original script if review fails
                    }
        
        review["success"] = review_success
        results["stages"]["review"] = review
        
        if save_intermediates:
            with open(f"stage5_review_{platform}.json", "w", encoding="utf-8") as f:
                json.dump(review, f, indent=2)
        
        # Final result
        results["final_ad_script"] = review.get("improved_script", ad_script)
        results["platform"] = platform
        results["overall_success"] = all([
            results["stages"]["research"].get("success", False),
            results["stages"]["data_collection"].get("success", False) or skip_reddit,
            results["stages"]["analysis"].get("success", False),
            results["stages"]["copywriting"].get("success", False),
            results["stages"]["review"].get("success", False)
        ])
        
        with open(f"final_ad_script_{platform}.txt", "w", encoding="utf-8") as f:
            f.write(results["final_ad_script"])

        # Generate a clean TTS script for ElevenLabs
        tts_script = generate_tts_script(results["final_ad_script"])
        tts_script_path = f"final_ad_script_{platform}_tts.txt"
        with open(tts_script_path, "w", encoding="utf-8") as f:
            f.write(tts_script)
        
        # Add the TTS script to the results
        results["tts_script"] = tts_script
        results["tts_script_path"] = tts_script_path
        
        # Stage 6: Runbook Generation (optional)
        if generate_runbook:
            print(f"\n=== Stage 6: Runbook Generation ===")
            runbook_success = False
            
            for attempt in range(max_retries):
                try:
                    from src.utils.runbook_generator import save_runbook
                    runbook_path = save_runbook(
                        platform=platform,
                        ad_script=results["final_ad_script"],
                        product_info=product_info,
                        output_path=f"runbook_{platform}_{product_info['product_name'].replace(' ', '_').lower()}.md"
                    )
                    results["runbook"] = {
                        "generated": True,
                        "path": runbook_path,
                        "success": True
                    }
                    print(f"Production runbook generated: {runbook_path}")
                    runbook_success = True
                    break
                except Exception as e:
                    print(f"Runbook generation attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        print("All runbook generation attempts failed.")
                        results["runbook"] = {
                            "generated": False,
                            "error": str(e),
                            "success": False
                        }
            
        else:
            results["runbook"] = {
                "generated": False,
                "reason": "Runbook generation disabled",
                "success": True  # Marking as successful since it was intentionally skipped
            }
        
        # Generate a disclaimer if fallbacks were used
        disclaimer = []
        if not results["stages"]["research"].get("success", False):
            disclaimer.append("Research: Fallback subreddits and queries were used as the research phase encountered issues.")
            
        if not results["stages"]["data_collection"].get("success", False) and not skip_reddit:
            disclaimer.append("Data Collection: No Reddit data could be retrieved. The ad script was generated without audience insights from Reddit.")
            
        if not results["stages"]["analysis"].get("success", False):
            disclaimer.append("Analysis: Analysis of audience data failed. Generated insights were based on product information only.")
            
        if not results["stages"]["copywriting"].get("success", False):
            disclaimer.append("Copywriting: Fallback copywriting mechanisms were used. The ad may be more generic than intended.")
            
        if not results["stages"]["review"].get("success", False):
            disclaimer.append("Review: The review process failed. The original script was used without improvements.")

        # Add the disclaimer to the results if any fallbacks were used
        if disclaimer:
            results["disclaimer"] = {
                "message": "NOTE: This ad script was generated using fallback mechanisms due to issues in the generation process.",
                "details": disclaimer
            }
            
            # Modify the final script to include the disclaimer at the top if any critical stages failed
            critical_failures = not skip_reddit and (
                not results["stages"]["data_collection"].get("success", False) or 
                not results["stages"]["analysis"].get("success", False)
            )
            
            if critical_failures:
                disclaimer_text = "DISCLAIMER: This ad script was generated without Reddit data insights. " + \
                                "It is based on product information only and may require additional customization."
                
                results["final_ad_script"] = f"{disclaimer_text}\n\n---\n\n{results['final_ad_script']}"
                
                # Update the saved file as well
                with open(f"final_ad_script_{platform}.txt", "w", encoding="utf-8") as f:
                    f.write(results["final_ad_script"])

        return results    
    
    def generate_ads_for_all_platforms(self, product_info: Dict[str, str], save_intermediates: bool = False,
                                     skip_reddit: bool = False, generate_runbook: bool = True) -> Dict[str, Any]:
        """Generate ad scripts for all supported platforms using the multi-agent approach.
        Optimized to perform Reddit scraping only once.
        
        Args:
            product_info (Dict[str, str]): Dictionary with product information
            save_intermediates (bool): Whether to save intermediate results to files
            skip_reddit (bool): Whether to skip Reddit scraping and rely only on LLM
            generate_runbook (bool): Whether to generate production and upload runbooks
            
        Returns:
            Dict[str, Any]: Dictionary with results for each platform
        """
        # Define all supported platforms
        platforms = ["general", "instagram", "youtube", "tiktok", "facebook", "video"]
        
        # Container for all results
        all_results = {
            "product_info": product_info,
            "platforms": {},
            "configuration": {
                "llm_provider": self.llm_provider,
                "model_name": self.model_name,
                "skip_reddit": skip_reddit
            }
        }
        
        # Perform platform-agnostic operations once
        
        # Stage 1: Research (common for all platforms)
        print(f"\n=== Stage 1: Research ({self.llm_provider}) ===")
        subreddits = self.research_agent.find_relevant_subreddits(product_info)
        queries = self.research_agent.generate_search_queries(product_info)
        research_results = {
            "subreddits": subreddits,
            "queries": queries
        }
        if save_intermediates:
            with open(f"stage1_research_all_platforms.json", "w", encoding="utf-8") as f:
                json.dump(research_results, f, indent=2)
        
        # Stage 2: Data Collection (if not skipping Reddit, common for all platforms)
        posts_data = []
        if not skip_reddit:
            print("\n=== Stage 2: Data Collection ===")
            posts_data = self.data_collection_agent.collect_data(subreddits, queries)
            data_collection_results = {
                "posts_count": len(posts_data)
            }
            if save_intermediates and posts_data:
                with open(f"stage2_raw_data_all_platforms.json", "w", encoding="utf-8") as f:
                    json.dump(posts_data, f, indent=2, ensure_ascii=False)
        else:
            print("\n=== Stage 2: Data Collection (SKIPPED) ===")
            data_collection_results = {
                "posts_count": 0,
                "skipped": True
            }
        
        # Stage 3: Analysis (common for all platforms)
        print(f"\n=== Stage 3: Analysis ({self.llm_provider}) ===")
        
        # If we have posts, analyze them; otherwise, synthesize insights directly
        if posts_data:
            relevant_posts = self.analysis_agent.filter_posts_by_relevance(posts_data, product_info)
            insights = self.analysis_agent.extract_key_insights(relevant_posts, product_info)
        else:
            # No Reddit data, so generate insights directly from product info
            print("No Reddit data available. Generating insights directly...")
            insights = self.analysis_agent.synthesize_insights_without_data(product_info)
            
        if save_intermediates:
            with open(f"stage3_analysis_all_platforms.json", "w", encoding="utf-8") as f:
                json.dump(insights, f, indent=2)
        
        # Now generate platform-specific content for each platform
        for platform in platforms:
            print(f"\n=== Generating content for {platform.capitalize()} ===")
            
            # Create a platform-specific results container
            platform_results = {
                "stages": {
                    "research": research_results,
                    "data_collection": data_collection_results,
                    "analysis": insights
                }
            }
            
            # Stage 4: Copywriting (platform-specific)
            print(f"\n=== Stage 4: Copywriting ({self.llm_provider}) for {platform.capitalize()} ===")
            ad_script = self.copywriting_agent.generate_ad_script(insights, product_info, platform=platform)
            platform_results["stages"]["copywriting"] = {
                "original_script": ad_script,
                "platform": platform
            }
            if save_intermediates:
                with open(f"stage4_original_script_{platform}.txt", "w", encoding="utf-8") as f:
                    f.write(ad_script)
            
            # Stage 5: Review (platform-specific)
            print(f"\n=== Stage 5: Review ({self.llm_provider}) for {platform.capitalize()} ===")
            review = self.review_agent.review_ad_script(ad_script, product_info, insights, platform=platform)
            platform_results["stages"]["review"] = review
            if save_intermediates:
                with open(f"stage5_review_{platform}.json", "w", encoding="utf-8") as f:
                    json.dump(review, f, indent=2)
            
            # Final result for this platform
            platform_results["final_ad_script"] = review.get("improved_script", ad_script)
            platform_results["platform"] = platform
            
            with open(f"final_ad_script_{platform}.txt", "w", encoding="utf-8") as f:
                f.write(platform_results["final_ad_script"])

            # Generate a clean TTS script for ElevenLabs
            tts_script = generate_tts_script(platform_results["final_ad_script"])
            tts_script_path = f"final_ad_script_{platform}_tts.txt"
            with open(tts_script_path, "w", encoding="utf-8") as f:
                f.write(tts_script)
            
            # Add the TTS script to the results
            platform_results["tts_script"] = tts_script
            platform_results["tts_script_path"] = tts_script_path
            
            # Stage 6: Runbook Generation (optional, platform-specific)
            if generate_runbook:
                print(f"\n=== Stage 6: Runbook Generation for {platform.capitalize()} ===")
                try:
                    from src.utils.runbook_generator import save_runbook
                    runbook_path = save_runbook(
                        platform=platform,
                        ad_script=platform_results["final_ad_script"],
                        product_info=product_info,
                        output_path=f"runbook_{platform}_{product_info['product_name'].replace(' ', '_').lower()}.md"
                    )
                    platform_results["runbook"] = {
                        "generated": True,
                        "path": runbook_path
                    }
                    print(f"Production runbook generated: {runbook_path}")
                except Exception as e:
                    print(f"Error generating runbook: {str(e)}")
                    platform_results["runbook"] = {
                        "generated": False,
                        "error": str(e)
                    }
            else:
                platform_results["runbook"] = {
                    "generated": False,
                    "reason": "Runbook generation disabled"
                }
            
            # Add this platform's results to the overall results
            all_results["platforms"][platform] = platform_results
        
        return all_results