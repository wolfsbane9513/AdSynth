#!/usr/bin/env python3
"""
Script for generating ad scripts using the multi-agent approach.
"""

import os
import json
import argparse
from typing import Dict, Any
import sys
import re

# Import modules from src directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.scraping.reddit import init_reddit_client
from src.multi_agent.orchestrator import AdGeneratorOrchestrator

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate ad scripts using multi-agent approach.")
    
    parser.add_argument(
        "--product-info",
        type=str,
        help="Path to JSON file with product information"
    )
    
    parser.add_argument(
        "--save-intermediates",
        action="store_true",
        help="Save intermediate results from each stage"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="ad_generation_results.json",
        help="Path to save the final results"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enter product information interactively"
    )
    
    parser.add_argument(
        "--llm-provider",
        type=str,
        choices=["openai", "claude", "groq"],
        default="groq",
        help="LLM provider to use across all agents (default: openai)"
    )
    
    parser.add_argument(
        "--model-name",
        type=str,
        help="Specific model name to use (e.g., gpt-4o, claude-3-5-sonnet, llama-70b)"
    )
    
    parser.add_argument(
        "--skip-reddit",
        action="store_true",
        help="Skip Reddit scraping and use only LLM for ad generation"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print additional debug information"
    )
    
    parser.add_argument(
        "--platform",
        type=str,
        choices=["general", "instagram", "youtube", "video", "tiktok", "facebook", "all"],
        default="general",
        help="Target platform for the ad (default: general)"
    )
    
    parser.add_argument(
        "--no-runbook",
        action="store_true",
        help="Skip production runbook generation"
    )
    
    return parser.parse_args()

def interactive_product_info() -> Dict[str, str]:
    """Collect product information interactively from the user."""
    print("\n=== Product Information Input ===")
    print("Please provide the following information about your product:\n")
    
    product_name = input("Product Name: ")
    product_description = input("Product Description: ")
    use_cases = input("Use Cases (comma separated): ")
    niche = input("Niche/Industry: ")
    keywords = input("Keywords (comma separated): ")
    target_audience = input("Target Audience: ")
    campaign_goal = input("Campaign Goal: ")
    
    return {
        "product_name": product_name,
        "product_description": product_description,
        "use_cases": use_cases,
        "niche": niche,
        "keywords": keywords,
        "target_audience": target_audience,
        "campaign_goal": campaign_goal
    }

def load_product_info(file_path: str = None, interactive: bool = False) -> Dict[str, str]:
    """Load product information from a JSON file or interactively."""
    if interactive:
        return interactive_product_info()
    
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: {file_path} is not a valid JSON file.")
            if input("Would you like to enter information interactively instead? (y/n): ").lower() == 'y':
                return interactive_product_info()
            else:
                sys.exit(1)
    
    # If no file is provided or loading fails, prompt for interactive input
    print("No product info file provided or file not found.")
    if input("Would you like to enter information interactively? (y/n): ").lower() == 'y':
        return interactive_product_info()
    else:
        print("Please provide product information via file or interactive input. Exiting.")
        sys.exit(1)

def validate_model_name(provider: str, model_name: str) -> str:
    """Validate and correct common model name errors."""
    if not model_name:
        return None
        
    if provider == "openai":
        # Fix common typos
        if model_name == "gtp-4o" or model_name == "gtp4o":
            print(f"Correcting model name from '{model_name}' to 'gpt-4o'")
            return "gpt-4o"
        if model_name == "gtp-4" or model_name == "gtp4":
            print(f"Correcting model name from '{model_name}' to 'gpt-4'")
            return "gpt-4"
        if model_name == "gtp-3.5-turbo" or model_name == "gtp3.5":
            print(f"Correcting model name from '{model_name}' to 'gpt-3.5-turbo'")
            return "gpt-3.5-turbo"
    
    return model_name

def main() -> None:
    """Main function to run the multi-agent ad generation pipeline."""
    # Parse command-line arguments
    args = parse_args()
    
    # Load product information
    product_info = load_product_info(args.product_info, args.interactive)
    
    # Validate required fields
    required_fields = ["product_name", "product_description", "target_audience", "campaign_goal"]
    missing_fields = [field for field in required_fields if not product_info.get(field)]
    
    if missing_fields:
        print(f"Error: Missing required product information: {', '.join(missing_fields)}")
        sys.exit(1)
    
    print(f"Generating ad for: {product_info['product_name']}")
    
    # Get and validate model name
    model_name = validate_model_name(args.llm_provider, args.model_name)
    
    # Validate LLM provider requirements
    if args.llm_provider == "openai" and not Config.OPENAI_API_KEY:
        print("Error: OpenAI selected but no API key found in .env")
        sys.exit(1)
    elif args.llm_provider == "claude" and not Config.ANTHROPIC_API_KEY:
        print("Error: Claude selected but no Anthropic API key found in .env")
        sys.exit(1)
    elif args.llm_provider == "groq" and not Config.GROQ_API_KEY:
        print("Error: Groq selected but no Groq API key found in .env")
        sys.exit(1)
    
    # Initialize Reddit client
    reddit_client = init_reddit_client()
    
    # Initialize orchestrator with specified LLM provider and model
    orchestrator = AdGeneratorOrchestrator(
        reddit_client, 
        llm_provider=args.llm_provider,
        model_name=model_name,
        debug=args.debug
    )
    
    # Generate ad using multi-agent approach
    try:
        print("\nStarting multi-agent ad generation process...")
        
        if args.platform == "all":
            print("\nGenerating ads for all platforms...")
            platforms = ["general", "instagram", "youtube", "video", "tiktok", "facebook"]
            all_results = {}
            
            for platform in platforms:
                print(f"\n=== Generating {platform.capitalize()} Ad ===")
                platform_results = orchestrator.generate_ad(
                    product_info, 
                    save_intermediates=args.save_intermediates,
                    skip_reddit=args.skip_reddit,
                    platform=platform,
                    generate_runbook=not args.no_runbook
                )
                all_results[platform] = platform_results
                
                # Save platform-specific ad script
                with open(f"final_ad_script_{platform}.txt", "w", encoding="utf-8") as f:
                    f.write(platform_results["final_ad_script"])
                    
                print(f"\n{platform.capitalize()} Ad Script:")
                print("-" * 60)
                print(platform_results["final_ad_script"])
                print("-" * 60)
                
                # Display runbook information if generated
                if not args.no_runbook and platform_results.get("runbook", {}).get("generated", False):
                    print(f"Production runbook saved to: {platform_results['runbook']['path']}")
            
            # Save combined results
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
                
            print(f"\nAll ad generation complete! Results saved to {args.output}")
        else:
            # Generate a single ad for the specified platform
            results = orchestrator.generate_ad(
                product_info, 
                save_intermediates=args.save_intermediates,
                skip_reddit=args.skip_reddit,
                platform=args.platform,
                generate_runbook=not args.no_runbook
            )
            
            # Save final results
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\nAd generation complete! Results saved to {args.output}")
            print(f"\n{args.platform.capitalize()} Ad Script:")
            print("-" * 60)
            print(results["final_ad_script"])
            print("-" * 60)
            
            # Display runbook information if generated
            if not args.no_runbook and results.get("runbook", {}).get("generated", False):
                print(f"Production runbook saved to: {results['runbook']['path']}")
                print("Follow the instructions in the runbook to produce and upload your ad.")
        
    except Exception as e:
        print(f"Error during ad generation: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()
        else:
            print("Run with --debug for more information.")

if __name__ == "__main__":
    main()