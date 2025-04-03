#!/usr/bin/env python
"""
Multi-agent ad generation script for AI Ad Generator.
Provides a command-line interface for generating ad scripts using the multi-agent system.
"""

import sys
import os
# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import json
import logging
import time
import traceback

from src.config import Config
from src.multi_agent.orchestrator import AdGeneratorOrchestrator

def parse_arguments():
    """Parse command line arguments for the multi-agent ad generator."""
    parser = argparse.ArgumentParser(description="Generate ad scripts using the multi-agent system")
    
    # Product information
    product_group = parser.add_mutually_exclusive_group()
    product_group.add_argument("--product-info", type=str, help="Path to a JSON file with product information")
    product_group.add_argument("--interactive", action="store_true", help="Enter product information interactively")
    
    # LLM provider options
    parser.add_argument("--llm-provider", type=str, default="openai", choices=["openai", "claude", "groq"],
                        help="LLM provider to use across all agents (openai, claude, groq)")
    parser.add_argument("--model-name", type=str, help="Specific model name to use (optional)")
    
    # Platform selection
    parser.add_argument("--platform", type=str, default="general", 
                        choices=["general", "instagram", "youtube", "tiktok", "facebook", "video", "all"],
                        help="Target platform for the ad")
    
    # Output options
    parser.add_argument("--output", type=str, default="ad_generation_results.json",
                        help="Path to save the final results")
    parser.add_argument("--save-intermediates", action="store_true",
                        help="Save intermediate results from each stage")
    
    # Processing options
    parser.add_argument("--skip-reddit", action="store_true",
                        help="Skip Reddit scraping and rely only on LLM generation")
    parser.add_argument("--no-runbook", action="store_true",
                        help="Skip production runbook generation")
    
    # Debug options
    parser.add_argument("--debug", action="store_true", help="Print additional debug information")
    
    return parser.parse_args()

def get_product_info_interactively():
    """Get product information interactively from the user."""
    print("\n=== Enter Product Information ===")
    
    product_info = {}
    
    # Required fields
    product_info["product_name"] = input("Product Name: ")
    product_info["product_description"] = input("Product Description: ")
    product_info["target_audience"] = input("Target Audience: ")
    product_info["campaign_goal"] = input("Campaign Goal (e.g., Increase sales by 20%): ")
    
    # Optional fields
    use_cases = input("Use Cases (comma-separated, press Enter to skip): ")
    if use_cases:
        product_info["use_cases"] = use_cases
    
    niche = input("Niche (comma-separated, press Enter to skip): ")
    if niche:
        product_info["niche"] = niche
    
    keywords = input("Keywords (comma-separated, press Enter to skip): ")
    if keywords:
        product_info["keywords"] = keywords
    
    print("\nProduct information collected successfully!")
    return product_info

def main():
    """Main function to run the multi-agent ad generator."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Get product information
    if args.interactive:
        product_info = get_product_info_interactively()
    elif args.product_info:
        try:
            with open(args.product_info, 'r', encoding='utf-8') as f:
                product_info = json.load(f)
        except Exception as e:
            print(f"Error loading product info file: {str(e)}")
            return
    else:
        # Use default product info for testing
        product_info = Config.default_product_info()
    
    # Validate required fields
    required_fields = ["product_name", "product_description", "target_audience", "campaign_goal"]
    missing_fields = [field for field in required_fields if field not in product_info]
    
    if missing_fields:
        print(f"Error: Missing required product information fields: {', '.join(missing_fields)}")
        return
    
    # Initialize Reddit client if not skipping Reddit
    reddit_client = None
    if not args.skip_reddit:
        try:
            from src.scraping.reddit import init_reddit_client
            reddit_client = init_reddit_client()
        except Exception as e:
            print(f"Error initializing Reddit client: {str(e)}")
            print("Proceeding without Reddit scraping...")
            args.skip_reddit = True
    
    # Initialize orchestrator with selected LLM provider
    orchestrator = AdGeneratorOrchestrator(
        reddit_client=reddit_client,
        llm_provider=args.llm_provider,
        model_name=args.model_name,
        debug=args.debug
    )
    
    # Track time for performance reporting
    start_time = time.time()
    
    try:
        # Generate ad using the orchestrator
        results = orchestrator.generate_ad(
            product_info=product_info,
            save_intermediates=args.save_intermediates,
            skip_reddit=args.skip_reddit,
            platform=args.platform,
            generate_runbook=not args.no_runbook
        )
        
        # Save results to output file
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Display summary
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n" + "="*50)
        print(f"Ad Generation Complete ({total_time:.2f} seconds)")
        print("="*50)
        
        # Single platform output
        if args.platform.lower() != "all":
            print(f"\nGenerated {args.platform.capitalize()} Ad Script:")
            print("-"*50)
            print(results["final_ad_script"])
            print("-"*50)

            if "tts_script_path" in results:
                print(f"\nElevenLabs TTS Script saved to: {results['tts_script_path']}")
                print("TTS Script Preview:")
                print("-"*30)
                preview = results["tts_script"][:150] + "..." if len(results["tts_script"]) > 150 else results["tts_script"]
                print(preview)
                print("-"*30)
            
            # Show runbook path if generated
            if "runbook" in results and results["runbook"].get("generated", False):
                print(f"\nProduction runbook: {results['runbook']['path']}")
        # All platforms output
        else:
            print("\nGenerated Ad Scripts for All Platforms:")
            print("-"*50)
            for platform, platform_results in results["platforms"].items():
                print(f"\n{platform.upper()} AD SCRIPT:")
                print(f"Saved to: final_ad_script_{platform}.txt")

                if "tts_script_path" in platform_results:
                    print(f"ElevenLabs TTS Script: {platform_results['tts_script_path']}")                
                
                # Show runbook path if generated
                if "runbook" in platform_results and platform_results["runbook"].get("generated", False):
                    print(f"Production runbook: {platform_results['runbook']['path']}")
                
                print("-"*30)
        
        print(f"\nFull results saved to: {args.output}")
        
    except Exception as e:
        print(f"Error generating ad: {str(e)}")
        if args.debug:
            traceback.print_exc()

if __name__ == "__main__":
    main()