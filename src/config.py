"""
Configuration module for AI Ad Generator.
Loads environment variables and provides access to configuration settings.
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for AI Ad Generator."""
    
    # Reddit API credentials
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "script:ai-ad-generator:v0.1 (by /u/YOUR_USERNAME)")
    
    # LLM API keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Default settings
    DEFAULT_SUBREDDIT = "productivity"
    DEFAULT_POST_LIMIT = 7
    DEFAULT_COMMENT_LIMIT = 5
    
    # LLM models
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20240620")
    
    # Groq models and configurations
    GROQ_MODELS = {
        "llama-3.3-70b-versatile": {
            "name": "llama-3.3-70b-versatile",
            "description": "Versatile model for general purpose tasks",
            "max_tokens": 4096
        },
        "deepseek-r1-distill-llama-70b": {
            "name": "deepseek-r1-distill-llama-70b",
            "description": "Distilled model optimized for efficiency",
            "max_tokens": 4096
        }
    }
    GROQ_DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///test_adsynth.db")
    
    @classmethod
    def validate_reddit_config(cls) -> None:
        """Validate Reddit API configuration."""
        if not all([cls.REDDIT_CLIENT_ID, cls.REDDIT_CLIENT_SECRET]):
            raise ValueError(
                "Reddit API credentials not found. Please set REDDIT_CLIENT_ID and "
                "REDDIT_CLIENT_SECRET in your .env file."
            )
    
    @classmethod
    def validate_llm_config(cls, provider: str) -> None:
        """Validate LLM API configuration for a specific provider."""
        if provider == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
        if provider == "claude" and not cls.ANTHROPIC_API_KEY:
            raise ValueError("Anthropic API key not found. Please set ANTHROPIC_API_KEY in your .env file.")
        if provider == "groq" and not cls.GROQ_API_KEY:
            raise ValueError("Groq API key not found. Please set GROQ_API_KEY in your .env file.")

    @staticmethod
    def default_product_info() -> Dict[str, str]:
        """Return default product information for testing."""
        return {
            "product_name": "FocusFlow",
            "product_description": "A productivity app that helps users maintain focus and track their work habits using AI-powered insights and gentle reminders.",
            "target_audience": "Remote workers, freelancers, and students who struggle with distractions",
            "key_use_cases": "Deep work sessions, deadline management, habit building, distraction blocking",
            "campaign_goal": "Increase app downloads and free trial signups",
            "niche": "productivity"
        }

# Add to Config class:
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
