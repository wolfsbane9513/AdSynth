#!/usr/bin/env python3
"""
Main script for generating ad scripts with AI Ad Generator.
"""

import os
import json
import argparse
from typing import Dict, Any

# Import modules from src directory
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.scraping import scrape_subreddit
from src.utils import prepare_llm_prompt
from src.generation import generate, providers

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate ad scripts using AI.")
    
    parser.add_argument(
        "--subreddit",
        type=str,
        default=Config.DEFAULT_SUBREDDIT,
        help=f"Subreddit to scrape (default: {Config.DEFAULT_SUBREDDIT})"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=Config.DEFAULT_POST_LIMIT,
        help=f"Number of posts to scrape (default: {Config.DEFAULT_POST_LIMIT})"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        choices=["openai", "claude", "groq", "all"],
        default="all",
        help="LLM provider to use (default: all)"
    )
    
    parser.add_argument(
        "--product-info",
        type=str,
        help="Path to JSON file with product information"
    )
    
    parser.add_argument(
        "--save-data",
        action="store_true",
        help="Save scraped data and prompts to files"
    )
    
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream output for models that support it (currently only Groq)"
    )
    
    return parser.parse_args()

def load_product_info(file_path: str = None) -> Dict[str, str]:
    """Load product information from a JSON file or use defaults."""
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: {file_path} is not a valid JSON file. Using default product info.")
    
    # Use default product info if no file is provided or loading fails
    return Config.default_product_info()

def save_data(data: Any, filename: str) -> None:
    """Save data to a file with proper encoding."""
    if isinstance(data, str):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)
    else:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved data to {filename}")

def main() -> None:
    """Main function to run the ad generation pipeline."""
    # Parse command-line arguments
    args = parse_args()
    
    # Load product information
    product_info = load_product_info(args.product_info)
    print(f"Using product info for: {product_info['product_name']}")
    
    # Scrape Reddit data
    posts_data = scrape_subreddit(args.subreddit, args.limit)
    
    # Save scraped data if requested
    if args.save_data:
        save_data(posts_data, "scraped_data.json")
    
    # Prepare prompt for LLM
    prompt = prepare_llm_prompt(posts_data, product_info)
    
    # Save prompt if requested
    if args.save_data:
        save_data(prompt, "llm_prompt.txt")
    
    # Generate ad scripts with selected models
    if args.model == "all":
        # Generate with all available providers
        for provider in providers.keys():
            try:
                # Special handling for Groq streaming
                if provider == "groq":
                    ad_script = generate(prompt, provider=provider, stream=args.stream)
                    if not args.stream:  # Only print header if not streaming
                        print(f"\n--- GENERATED AD SCRIPT ({provider.capitalize()}) ---\n")
                        print(ad_script)
                else:
                    ad_script = generate(prompt, provider=provider)
                    print(f"\n--- GENERATED AD SCRIPT ({provider.capitalize()}) ---\n")
                    print(ad_script)
                
                save_data(ad_script, f"generated_ad_{provider}.txt")
            except Exception as e:
                print(f"Error generating ad with {provider.capitalize()}: {e}")
    else:
        # Generate with the specified provider
        try:
            # Special handling for Groq streaming
            if args.model == "groq":
                ad_script = generate(prompt, provider=args.model, stream=args.stream)
                if not args.stream:  # Only print header if not streaming
                    print(f"\n--- GENERATED AD SCRIPT ({args.model.capitalize()}) ---\n")
                    print(ad_script)
            else:
                ad_script = generate(prompt, provider=args.model)
                print(f"\n--- GENERATED AD SCRIPT ({args.model.capitalize()}) ---\n")
                print(ad_script)
            
            save_data(ad_script, f"generated_ad_{args.model}.txt")
        except Exception as e:
            print(f"Error generating ad with {args.model.capitalize()}: {e}")

if __name__ == "__main__":
    main()